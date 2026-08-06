---
name: build-and-run
description: Running the FastAPI server and Typer CLI, endpoint reference, smoke tests, and architecture notes. Use when you need to start the app or understand how to interact with it.
---

# Skill: Building and Running the Project

Use this skill to run the Task Manager API server or CLI after setup is complete.

## Running the API Server

```bash
uv run uvicorn src.api.main:app --reload
```

- Starts on `http://localhost:8000` by default.
- Add `--host 0.0.0.0 --port <PORT>` to bind to all interfaces or a custom port.
- The `--reload` flag enables auto-reload on code changes (dev mode).
- Interactive API docs are available at `http://localhost:8000/docs` (Swagger UI).

### API Endpoints

| Method | Path                  | Description                              |
|--------|-----------------------|------------------------------------------|
| GET    | `/health`             | Health check (returns `{"status": "ok"}`) |
| GET    | `/tasks`              | List tasks (optional `?status=todo`)      |
| GET    | `/tasks/search`       | Search by title/description (`?q=...`)    |
| GET    | `/tasks/overdue`      | List overdue tasks                        |
| GET    | `/tasks/stats`        | Aggregate statistics                      |
| GET    | `/tasks/{id}`         | Get a single task                         |
| POST   | `/tasks`              | Create a task                             |
| PATCH  | `/tasks/{id}`         | Partially update a task                   |
| POST   | `/tasks/{id}/complete`| Mark a task as done                       |
| DELETE | `/tasks/{id}`         | Delete a task                             |

### Quick API smoke test

```bash
# Health check
curl http://localhost:8000/health

# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "priority": "high"}'

# List all tasks
curl http://localhost:8000/tasks
```

## Running the CLI

```bash
uv run python -m src.cli --help
```

### CLI Commands

```bash
# Add a task
uv run python -m src.cli add "My task" --priority high --due 2024-12-31

# List tasks (optionally filter by status)
uv run python -m src.cli list
uv run python -m src.cli list --status todo

# Mark a task as done
uv run python -m src.cli done 1

# Show statistics
uv run python -m src.cli stats
```

- CLI tasks are persisted in `data/cli_tasks.json` (gitignored).
- On first run, when `data/cli_tasks.json` does not exist yet, the CLI seeds its store from `data/sample_tasks.json` so demos start with sample data. Subsequent mutations persist to `data/cli_tasks.json`.
- The CLI uses the same `TaskService` as the API but with file-based persistence.

## Architecture Notes

- **`src/api/main.py`**: FastAPI app factory (`create_app()`) with route definitions. Uses a shared in-memory `TaskService` instance via FastAPI dependency injection.
- **`src/cli.py`**: Typer CLI that hydrates a `TaskService` from `data/cli_tasks.json` on startup (falling back to `data/sample_tasks.json` as seed data on first run) and persists after mutations.
- **`src/services/task_service.py`**: Core business logic (in-memory CRUD store). Historical bugs have been fixed and are covered by tests (see the testing skill).
- **`src/models/task.py`**: Pydantic v2 models (`Task`, `TaskCreate`, `TaskUpdate`, `TaskStats`, enums `TaskStatus`, `TaskPriority`).
- Both the API and CLI share the same models and service layer.
