#!/usr/bin/env python3
"""
Workflow Orchestration Executor
DAG-based task runner for AI agent pipelines.
"""
import asyncio
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("workflow_orchestrator")


@dataclass
class Step:
    name: str
    fn: Callable
    depends: List[str] = field(default_factory=list)
    timeout: int = 60  # seconds
    retry: int = 1
    fallback: Optional[Callable] = None


class DAGExecutor:
    """Execute steps in DAG order with parallel support."""

    def __init__(self):
        self.steps: Dict[str, Step] = {}
        self.results: Dict[str, Any] = {}

    def add_step(self, step: Step):
        self.steps[step.name] = step

    def _can_execute(self, name: str) -> bool:
        step = self.steps[name]
        return all(dep in self.results for dep in step.depends)

    def _execute_step(self, name: str, input_data: Any) -> Any:
        step = self.steps[name]
        logger.info(f"Executing step: {name}")
        try:
            result = step.fn(input_data, self.results)
            self.results[name] = result
            return result
        except Exception as e:
            logger.error(f"Step {name} failed: {e}")
            if step.fallback:
                result = step.fallback(input_data, self.results)
                self.results[name] = result
                return result
            raise

    async def execute_async(self, initial_input: Any) -> Dict[str, Any]:
        """Async execution with parallel branching."""
        pending = set(self.steps.keys())
        running = {}

        while pending:
            # Launch all steps whose dependencies are met
            for name in list(pending):
                if self._can_execute(name):
                    step = self.steps[name]
                    pending.discard(name)
                    running[name] = asyncio.create_task(
                        asyncio.wait_for(
                            asyncio.to_thread(self._execute_step, name, initial_input),
                            timeout=step.timeout
                        )
                    )

            if not running:
                break

            done, _ = await asyncio.wait(running.values(), return_when=asyncio.FIRST_COMPLETED)

            for task in done:
                name = [k for k, v in running.items() if v == task][0]
                del running[name]
                try:
                    await task
                except Exception as e:
                    logger.error(f"Step {name} failed: {e}")
                    raise

        return self.results

    def execute(self, initial_input: Any) -> Dict[str, Any]:
        """Sync wrapper."""
        return asyncio.run(self.execute_async(initial_input))


# --- Example Usage ---

def fetch_data(input_data, ctx):
    return {"url": input_data["url"], "status": "fetched"}

def transform_data(input_data, ctx):
    raw = ctx["fetch"]["url"]
    return {"transformed": raw.upper()}

def save_data(input_data, ctx):
    return {"saved": True, "data": ctx["transform"]["transformed"]}


if __name__ == "__main__":
    executor = DAGExecutor()
    executor.add_step(Step("fetch", fetch_data))
    executor.add_step(Step("transform", transform_data, depends=["fetch"]))
    executor.add_step(Step("save", save_data, depends=["transform"]))

    result = executor.execute({"url": "https://example.com"})
    print("Results:", result)
