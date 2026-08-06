---
name: security-review
description: Review the current diff for security issues before merging. Use for any change touching the FastAPI routes, the CLI, or file/data handling.
---

## Steps

1. Read the full diff against the base branch: `git diff --merge-base origin/main`.
2. For each added or changed route in `src/api/main.py`, check that all user input is constrained by a Pydantic model or a typed `Query`/`Path` parameter — never accept a free-form `dict` body.
3. Check error handling: `HTTPException.detail` must carry a short message, never a stack trace, file path, or raw exception text.
4. Check file handling in `src/cli.py` and `src/utils/data_processor.py`: paths must not be built from unvalidated user input, and JSON/CSV loading must handle missing or malformed files instead of crashing.
5. Search the diff for hardcoded secrets, tokens, passwords, or absolute developer paths.
6. Check any new dependency in `pyproject.toml`: pinned sensibly, actively maintained, and published at least 7 days ago.
7. If the change adds CORS, auth, or any middleware, confirm it is not permissive by default (no `allow_origins=["*"]` combined with credentials).
8. Write a short report: issue, `file:line`, severity (high/medium/low), suggested fix.
9. Fix every high-severity issue before opening the PR. Note: the `# BUG:` comments in `src/services/task_service.py` are intentional demo bugs, not security findings.
