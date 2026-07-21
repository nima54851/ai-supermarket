# Multi-Agent Coordination

> Orchestrate multiple AI agents working together — task distribution, shared memory, and result aggregation.

## Overview

When a single agent isn't enough, coordinate a team of specialized agents. This skill covers:
- **Task decomposition** — split complex goals into agent-sized tasks
- **Agent spawning** — launch sub-agents with specific roles
- **Shared memory** — coordinate state across agents
- **Result aggregation** — combine outputs into coherent responses
- **Conflict resolution** — handle disagreements between agents

## Concepts

```
User Request
     ↓
┌────┴────┐
│Orchestrator│ ← plans, decomposes, coordinates
└────┬────┘
  ↓  ↓  ↓
[Agent A] [Agent B] [Agent C]  ← specialized sub-agents
  ↓  ↓  ↓
[Shared Memory / State]
  ↓
Aggregated Result → User
```

## Architecture Patterns

### 1. Supervisor Pattern (Sequential)
One orchestrator → one sub-agent at a time → combine results
- Good for: dependent tasks (B needs A's output)
- Example: research → write → review → edit

### 2. Manager Pattern (Parallel)
One orchestrator → multiple sub-agents simultaneously → aggregate
- Good for: independent parallel tasks
- Example: analyze X, analyze Y, analyze Z concurrently

### 3. Debate Pattern
Multiple agents argue different positions → moderator resolves
- Good for: decisions with trade-offs
- Example: evaluate A vs B, pick winner

### 4. Voting Pattern
Multiple agents independently solve same problem → vote/fverage
- Good for: reducing hallucinations, diverse perspectives
- Example: same question → 3 agents → majority answer

## OpenClaw Agent Spawning

```python
# Using OpenClaw sessions_spawn
from agents import sessions_spawn

async def run_multi_agent(request: str):
    """Orchestrate multiple agents for a complex task."""

    # Step 1: Analyze and decompose
    plan = await analyze_task(request)
    # Output: {"tasks": [{"agent": "researcher", "goal": "..."}, ...]}

    # Step 2: Spawn sub-agents in parallel
    results = await asyncio.gather(*[
        sessions_spawn(
            agent_id="sub-agent",
            task=task["goal"],
            context={"role": task["agent"]}
        )
        for task in plan["tasks"]
    ])

    # Step 3: Aggregate results
    aggregated = aggregate_results(results)

    # Step 4: Return final response
    return aggregated
```

## Supervisor Chain

```python
# supervisor_chain.py — sequential supervisor pattern
import asyncio

SUPERVISOR_PROMPT = """You are a supervisor. Given a user request:
1. Break it into 2-3 tasks for specialized agents
2. Assign each to the appropriate agent
3. Review their outputs
4. Produce the final answer

Current request: {request}

Respond with a JSON plan:
{{"tasks": [{{"agent": "researcher|writer|reviewer|coder", "goal": "specific task description"}}]}}"""

AGENT_CONFIGS = {
    "researcher": {
        "prompt": "You are a research specialist. Find accurate, up-to-date information. Cite sources. Be thorough.",
        "model": "gpt-4o"
    },
    "writer": {
        "prompt": "You are a technical writer. Create clear, well-structured content. Use appropriate formatting.",
        "model": "gpt-4o"
    },
    "reviewer": {
        "prompt": "You are a quality reviewer. Check for accuracy, completeness, and clarity. Suggest specific improvements.",
        "model": "gpt-4o"
    },
    "coder": {
        "prompt": "You are a software engineer. Write clean, working code. Include tests.",
        "model": "claude-sonnet"
    }
}


class SupervisorChain:
    """Sequential supervisor: plan → execute each task → review → final."""

    def __init__(self):
        self.tasks = []
        self.results = []
        self.memory = {}

    async def plan(self, request: str) -> list:
        """Decompose request into tasks."""
        plan_text = await self.call_llm(SUPERVISOR_PROMPT.format(request=request))
        import json, re
        match = re.search(r'\{.*\}', plan_text, re.DOTALL)
        plan = json.loads(match.group()) if match else {"tasks": []}
        self.tasks = plan["tasks"]
        return self.tasks

    async def execute_tasks(self) -> list:
        """Execute each task in sequence (can be parallelized if independent)."""
        results = []
        for task in self.tasks:
            agent_type = task["agent"]
            agent_config = AGENT_CONFIGS.get(agent_type, AGENT_CONFIGS["researcher"])

            result = await sessions_spawn(
                agent_id="sub-agent",
                task=task["goal"],
                context={"system_prompt": agent_config["prompt"]},
                mode="run"
            )
            results.append({
                "agent": agent_type,
                "goal": task["goal"],
                "result": result
            })
            self.memory[f"task_{len(results)}"] = result
        self.results = results
        return results

    async def review_and_finalize(self) -> str:
        """Supervisor reviews all results and produces final answer."""
        review_prompt = f"""Review these agent outputs and produce a final answer:

{chr(10).join([f"[{r['agent']}] {r['goal']}: {r['result'][:500]}" for r in self.results])}

Final answer:"""
        return await self.call_llm(review_prompt)

    async def run(self, request: str) -> str:
        await self.plan(request)
        await self.execute_tasks()
        return await self.review_and_finalize()
```

## Shared Memory (Multi-Agent Coordination)

```python
# shared_memory.py — Redis-backed coordination for multi-agent systems
import redis
import json
import time
from typing import Any, Optional
from datetime import timedelta

class MultiAgentMemory:
    """Shared memory for coordinating multiple agents."""

    def __init__(self, namespace: str = "agent-team", ttl: int = 3600):
        self.r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self.ns = namespace
        self.ttl = ttl

    def _key(self, agent_id: str, key: str) -> str:
        return f"{self.ns}:{agent_id}:{key}"

    def write(self, agent_id: str, key: str, value: Any, ttl: int = None) -> None:
        """Agent writes to shared memory."""
        self.r.setex(
            self._key(agent_id, key),
            ttl or self.ttl,
            json.dumps(value)
        )

    def read(self, agent_id: str, key: str) -> Optional[Any]:
        data = self.r.get(self._key(agent_id, key))
        return json.loads(data) if data else None

    def read_all(self, key: str) -> dict:
        """Read a key from all agents (e.g., "findings" from all agents)."""
        results = {}
        for full_key in self.r.scan_iter(f"{self.ns}:*:{key}"):
            agent_id = full_key.split(":")[1]
            data = self.r.get(full_key)
            if data:
                results[agent_id] = json.loads(data)
        return results

    def broadcast(self, key: str, value: Any) -> None:
        """Write to all agents at once (e.g., new instruction)."""
        for agent_id in self.r.smembers(f"{self.ns}:agents"):
            self.write(agent_id, key, value)

    def register_agent(self, agent_id: str) -> None:
        """Register an agent in the team."""
        self.r.sadd(f"{self.ns}:agents", agent_id)

    def agent_done(self, agent_id: str, result: Any) -> None:
        """Mark agent as done and store result."""
        self.write(agent_id, "done", True)
        self.write(agent_id, "result", result)
        self.r.incr(f"{self.ns}:done_count")

    def all_done(self) -> bool:
        """Check if all registered agents are done."""
        total = self.r.scard(f"{self.ns}:agents")
        done = int(self.r.get(f"{self.ns}:done_count") or 0)
        return done >= total and total > 0

    def wait_for_all(self, timeout: int = 300, poll_interval: int = 2) -> dict:
        """Block until all agents report done, or timeout."""
        start = time.time()
        while time.time() - start < timeout:
            if self.all_done():
                return self.read_all("result")
            time.sleep(poll_interval)
        raise TimeoutError(f"Timeout after {timeout}s waiting for agents")
```

## Conflict Resolution

```python
# debate.py — agent debate pattern with moderator

DEBATE_SYSTEM = """You are {role}. Argue for: {position}
Be direct, specific, and cite evidence when possible.
Concede when the other side makes valid points.
"""

MODERATOR_SYSTEM = """You are a debate moderator.
Given multiple arguments, identify:
1. Key agreements
2. Key disagreements  
3. Best-supported conclusion

Respond with: {{"agreements": [...], "disagreements": [...], "winner": "...", "reasoning": "..."}}"""


async def run_debate(question: str, positions: list) -> dict:
    """Run a multi-agent debate and return moderator's verdict."""
    import asyncio

    # Spawn agent for each position
    tasks = [
        sessions_spawn(
            agent_id="debate-agent",
            task=f"Question: {question}\nArgue for: {pos}\nBe concise but compelling.",
            context={"role": positions[i]},
            mode="run"
        )
        for i, pos in enumerate(positions)
    ]

    arguments = await asyncio.gather(*tasks)

    # Moderator reviews
    moderator_input = "\n\n".join([
        f"[{positions[i]}]: {arg}" for i, arg in enumerate(arguments)
    ])
    verdict = await sessions_spawn(
        agent_id="moderator",
        task=f"Debate arguments:\n{moderator_input}\n\nProvide your verdict.",
        context={"role": "moderator"},
        mode="run"
    )

    return {
        "question": question,
        "positions": positions,
        "arguments": dict(zip(positions, arguments)),
        "verdict": verdict
    }
```

## n8n Workflow: Agent Orchestrator

```json
{
  "name": "Multi-Agent Orchestrator",
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": { "path": "multi-agent", "method": "POST" }
    },
    {
      "name": "Parse & Plan",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// Decompose task into agent tasks\nconst request = $json.body.request;\nconst plan = {\n  tasks: [\n    { agent: 'researcher', goal: `Research: ${request}` },\n    { agent: 'writer', goal: `Write content based on research for: ${request}` },\n    { agent: 'reviewer', goal: `Review and improve: ${request}` }\n  ]\n};\nreturn [{ json: plan }];"
      }
    },
    {
      "name": "Spawn Researcher",
      "type": "n8n-nodes-base.openAIFunctions",
      "parameters": {
        "resource": "chat",
        "messages": [{"role": "user", "content": "={{ $('Parse & Plan').first().json.tasks[0].goal }}"}]
      }
    },
    {
      "name": "Spawn Writer",
      "type": "n8n-nodes-base.openAIFunctions",
      "parameters": {
        "resource": "chat",
        "messages": [{"role": "user", "content": "={{ $('Parse & Plan').first().json.tasks[1].goal }}"}]
      }
    },
    {
      "name": "Aggregate & Finalize",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "const research = $('Spawn Researcher').first().json.message.content;\nconst writing = $('Spawn Writer').first().json.message.content;\nreturn [{ json: { final: `Research:\\n${research}\\n\\nContent:\\n${writing}` } }];"
      }
    }
  ]
}
```

## See Also

- `skills/mcp-integration/` — MCP tool calling across agents
- `skills/self-hosted-ai/` — deploy multiple local LLMs
- `skills/browser-automation/` — agent-controlled browser tasks
