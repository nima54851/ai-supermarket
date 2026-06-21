---
name: test-master
description: AI Agent testing assistant — writes unit/integration/E2E tests, builds test automation frameworks, analyzes coverage, and creates test strategies. Triggers: test, testing, QA, unit test, integration test, E2E, coverage, performance test, regression.
---

# Test Master — AI Agent Testing Assistant

## PURPOSE

Act as a senior QA engineer for AI agent projects. Generate comprehensive tests, build test automation frameworks, and ensure software quality.

## WHEN TO TRIGGER

- Writing unit tests, integration tests, or E2E tests
- Creating test strategies or test plans
- Analyzing code coverage and quality metrics
- Building test automation frameworks
- Debugging test failures
- Creating mock data and fixtures

## TEST STRATEGY FRAMEWORK

### 1. Analyze the Code

```
Before writing tests, identify:
- Public API surface (functions, classes, endpoints)
- Edge cases and boundary conditions
- Error paths and exception handling
- External dependencies (DB, APIs, file I/O)
- State mutations
```

### 2. Coverage Targets

| Project Type | Target | Focus Areas |
|---|---|---|
| Library/SDK | 90%+ | Public API, edge cases |
| Web App | 80%+ | Business logic, API routes |
| Scripts/Tools | 70%+ | Main paths, error handling |
| AI Agents | 85%+ | Tool calls, memory, output formats |

### 3. Test Structure

```
tests/
├── unit/           # Isolated function/class tests
├── integration/   # API, DB, external service tests
├── e2e/            # Full flow tests
├── fixtures/       # Mock data and helpers
└── conftest.py    # Shared pytest config
```

## PYTEST BEST PRACTICES

```python
# Use descriptive names: test_<what>_<when>_<expected>
def test_user_login_with_valid_credentials_returns_token():
    ...

# Arrange-Act-Assert pattern
def test_api_returns_404_for_nonexistent_user():
    # Arrange
    user_id = "nonexistent-id"
    # Act
    response = client.get(f"/users/{user_id}")
    # Assert
    assert response.status_code == 404

# Parametrize for multiple scenarios
@pytest.mark.parametrize("input,expected", [
    ("", False),
    ("a", False),
    ("ab", True),
    ("hello@example.com", True),
])
def test_email_validation(input, expected):
    assert validate_email(input) == expected
```

## MOCKING STRATEGY

```python
# Mock external APIs
@pytest.fixture
def mock_github_api(mocker):
    return mocker.patch("scripts.github_trending.requests.get")

# Mock file I/O
def test_read_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"key": "value"}')
    result = load_config(str(config_file))
    assert result == {"key": "value"}

# Mock LLM responses (deterministic output testing)
def test_agent_response_format(mocker):
    mocker.patch("llm.call", return_value='{"action": "search", "query": "test"}')
    result = agent.respond("search for test")
    assert '"action"' in result
```

## COVERAGE ANALYSIS

```bash
# Run with coverage
pytest --cov=src --cov-report=html tests/

# Minimum coverage enforcement
# pyproject.toml
[tool.coverage.report]
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
```

## E2E TESTING (PLAYWRIGHT EXAMPLE)

```python
from playwright.sync_api import sync_playwright

def test_github_pages_loads():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://nima54851.github.io/agent-studio")
        assert page.title() != ""
        assert page.locator("h1").count() > 0
        browser.close()
```

## OUTPUT FORMAT

When asked to write tests, respond with:
1. **Test strategy** — what to test and why
2. **Test file** — complete, runnable code
3. **Run instructions** — how to execute
4. **Coverage estimate** — expected lines/functions covered

## EXAMPLE REQUEST/RESPONSE

**Request:** "Write tests for a GitHub trending fetcher script"

**Response includes:**
- Unit tests for API response parsing
- Unit tests for error handling (rate limits, timeouts)
- Integration tests with mocked API
- Fixtures for sample trending data
- Coverage report setup
