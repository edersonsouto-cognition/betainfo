---
name: review-diff-for-security-issues
description: Review the current diff for OWASP Top 10 issues. Use for any change touching endpoints, the CLI, or user input.
---

## Steps

1. Read the full diff against the base branch: `git diff --merge-base origin/HEAD`.
2. For each added or changed route in `src/api/main.py`, check that all user input is constrained by a Pydantic model or a typed `Query`/`Path` parameter — never accept a free-form `dict` body.
3. Check object access: any route that reads or writes a task by id must handle the missing/unauthorized case explicitly instead of trusting the caller-supplied id.
4. Check error handling: `HTTPException.detail` must carry a short message, never a stack trace, file path, or raw exception text.
5. Check file handling in `src/cli.py` and `src/utils/data_processor.py`: paths must not be built from unvalidated user input, and JSON/CSV loading must handle missing or malformed files instead of crashing.
6. Search the diff for hardcoded secrets, tokens, passwords, or absolute developer paths.
7. Check any new dependency in `pyproject.toml`: pinned sensibly, actively maintained, and published at least 7 days ago.
8. If the change adds CORS, auth, or any middleware, confirm it is not permissive by default (no `allow_origins=["*"]` combined with credentials).
9. Write a short report: issue, `file:line`, severity (high/medium/low), suggested fix.
10. Fix every high-severity issue before opening the PR. Note: the `# BUG:` comments in `src/services/task_service.py` are intentional demo bugs, not security findings.
