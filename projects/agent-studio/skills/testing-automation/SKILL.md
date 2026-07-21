# Testing Automation

## Overview
AI-powered test generation and coverage tracking — auto-generate pytest/jest tests from code, track coverage trends, and run regression suites on every PR.

## What It Does
- Analyzes Python/JavaScript functions and generates pytest/jest test cases
- Generates edge case and boundary condition tests automatically
- Integrates with GitHub Actions for CI test runs
- Tracks coverage delta per PR (reports when coverage drops)
- Auto-fixes broken tests using AI

## Files
- `n8n-test-gen-workflow.json` — Code → AI test generator → PR comment workflow
- `pytest_runner.py` — Local test runner with coverage report
- `jest_runner.sh` — Jest test runner wrapper for Node.js projects
- `coverage_tracker.py` — Coverage trend tracking and alerting

## Setup
1. Import `n8n-test-gen-workflow.json` into n8n
2. Configure GitHub token for PR comments
3. Add coverage thresholds (warn at 80%, fail at 70%)
4. Hook into GitHub Actions on PR events

## Usage
PR opened → n8n picks up changed files → AI generates tests → posts comment with test file patch
