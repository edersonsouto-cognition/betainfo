---
name: verify-in-browser
description: Start the API server and verify changed endpoints through Swagger UI or curl before finishing an API task. This repo has no frontend; verification happens against the API.
---

## Steps

1. Make sure dependencies are installed: `uv sync --all-extras`.
2. Start the server in its own shell and leave it running:
   ```bash
   uv run uvicorn src.api.main:app --reload
   ```
3. Confirm it is up: `curl http://localhost:8000/health` returns `{"status": "ok"}`.
4. From the diff, list every endpoint the change touches.
5. Exercise each one, either with `curl` or interactively via Swagger UI at `http://localhost:8000/docs` ("Try it out" on each route). Note that the API store is in-memory and empty on startup, so create a task first:
   ```bash
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Test task", "priority": "high"}'
   ```
6. Check both the happy path and a failure path (unknown id -> 404, invalid body -> 422).
7. Watch the uvicorn console for tracebacks; an unhandled exception there is a failure even if the response looks acceptable.
8. If the change touches the CLI instead, verify it the same way with `uv run python -m src.cli <command>`, and delete `data/cli_tasks.json` first if you need a clean seeded store.
9. Attach screenshots of the Swagger responses (or paste the curl output) in the PR description.
