---
name: write-tests-for-untested-code
description: Find code without test coverage and add focused pytest tests for it.
---

## Steps

1. Measure coverage (`pytest-cov` is not a project dependency, so pull it in for the run):
   ```bash
   uv run --with pytest-cov pytest --cov=src --cov-report=term-missing
   ```
2. Pick the most critical uncovered paths first. Use the coverage report to find gaps; new features and recently added modules are usually the best targets.
3. Write focused tests: one behavior per test, clear names, arrange-act-assert, grouped in `Test*` classes like the existing suite.
4. Reuse the `service` and `populated_service` fixtures in `tests/conftest.py` instead of duplicating setup; add new fixtures there when several tests need them.
5. Cover at least one error/edge case per function (missing id -> `TaskNotFoundError`, empty store, invalid input), not just the happy path.
6. Tests must assert the *correct* behavior. If a correct test fails, report the bug rather than asserting the buggy behavior, and only fix the code if the task asks for it.
7. Re-run coverage and report the before/after numbers in the PR description.
