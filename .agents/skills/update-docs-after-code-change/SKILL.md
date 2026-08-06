---
name: update-docs-after-code-change
description: Keep README and docs in sync with the code after any behavior change.
---

## Steps

1. Read the diff (`git diff --merge-base origin/HEAD`) and list every user-visible change: endpoints, CLI commands, config, data files, setup steps.
2. Update the affected `README.md` sections (Quick Start, Project Structure, API Endpoints, CLI Commands).
3. Update the matching skill docs under `.agents/skills/`: the endpoint and CLI tables in `build-and-run`, architecture/bug notes in `codebase-guide`, test and CI details in `testing-and-linting`.
4. Verify every command you document actually runs as written (`uv sync --all-extras`, `uv run pytest`, the curl calls, the CLI invocations).
5. Check docstrings of changed public functions (`TaskService` methods, route handlers, CLI commands) and update stale ones.
6. Keep the tone and format of the existing docs; do not rewrite unrelated sections.
