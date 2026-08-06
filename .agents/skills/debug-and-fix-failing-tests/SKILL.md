---
name: debug-and-fix-failing-tests
description: Systematically diagnose and fix failing tests without weakening them.
---

## Steps

1. Reproduce and stop at the first failure with locals: `uv run pytest -x -l`. Narrow down with `uv run pytest tests/test_task_service.py::TestGetStats -x` once you know where it fails.
2. Read the failing test to understand the expected behavior before touching any code.
3. Decide: is the product code wrong or the test outdated? Fix the product code by default. In this repo the intentional `# BUG:` comments in `src/services/task_service.py` are the usual root cause.
4. Never delete assertions, add `@pytest.mark.skip`/`xfail`, or loosen a test just to make it pass.
5. Fix shared logic in `TaskService` rather than patching the API handler or the CLI, so both interfaces get the fix.
6. Re-run the full suite (`uv run pytest`) plus `uv run ruff check .` to confirm nothing else broke.
7. In the PR description, explain the root cause in one or two sentences.
