---
name: start-api-and-test-endpoints-live
description: Start the FastAPI server and exercise the changed endpoints with real requests before finishing any API task.
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
6. Check both the happy path and a failure path (unknown id -> 404, invalid body -> 422), and confirm status codes and response bodies match the intended behavior.
7. Open `http://localhost:8000/docs` and confirm the OpenAPI schema reflects the change.
8. Watch the uvicorn console for tracebacks; an unhandled exception there is a failure even if the response looks acceptable.
9. If the change touches the CLI instead, verify it the same way with `uv run python -m src.cli <command>`, and delete `data/cli_tasks.json` first if you need a clean seeded store.
10. Paste the curl commands and responses (or Swagger screenshots) in the PR description.
