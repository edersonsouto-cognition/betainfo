---
name: run-quality-checks-before-pr
description: Run lint, format check, and the full test suite, then self-review the diff. Required before opening any PR.
---

## Steps

1. Run the lint checks and fix everything they report:
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   ```
   `uv run ruff check . --fix` and `uv run ruff format .` apply the fixes automatically.
2. Run the test suite; every test must pass:
   ```bash
   uv run pytest
   ```
3. Read the full diff against the base branch: `git diff --merge-base origin/HEAD`.
4. Self-review the diff for: leftover `print()` / debugging code, hardcoded secrets or absolute paths, missing error handling, and unused imports.
5. Do not remove or "fix" the `# BUG:` comments in `src/services/task_service.py` unless the task is explicitly to fix those bugs — they are intentional demo material.
6. Do not commit `data/cli_tasks.json` or `.venv/` (both gitignored).
7. Only open the PR once lint and tests pass. These are exactly the two CI jobs in `.github/workflows/ci.yml` (lint, then test), so a green local run means a green CI run. List the checks you ran in the PR description.
