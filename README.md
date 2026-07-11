# Task Manager API – Devin Demo Playground

A feature-rich Task Manager project designed for **Devin demo recordings**. It includes intentional bugs, missing test coverage, refactor-worthy code, and sample data — all set up to showcase different Devin capabilities.

## Quick Start

```bash
# Install dependencies (Python 3.11+ required)
uv sync --all-extras

# Run the API server
uv run uvicorn src.api.main:app --reload

# Run the CLI
uv run python -m src.cli --help

# Run tests
uv run pytest

# Lint
uv run ruff check .
uv run ruff format --check .
```

## Project Structure

```
├── src/
│   ├── api/              # FastAPI app with CRUD endpoints
│   │   └── main.py
│   ├── models/           # Pydantic v2 models
│   │   └── task.py
│   ├── services/         # Business logic (with intentional bugs)
│   │   └── task_service.py
│   ├── utils/
│   │   ├── text_processing.py   # Refactor-worthy text helpers
│   │   └── data_processor.py    # CSV/JSON wrangling with pandas
│   └── cli.py            # Typer + Rich CLI
├── tests/                # Pytest suite (with intentional gaps)
├── data/
│   ├── sales_data.csv    # 24 sales records for data analysis demos
│   └── sample_tasks.json # Seed data the CLI loads on first run
├── .github/workflows/
│   └── ci.yml            # GitHub Actions: Ruff + Pytest
└── pyproject.toml
```

## Tech Stack

| Layer | Tools |
|-------|-------|
| API | FastAPI, Pydantic v2, Uvicorn |
| CLI | Typer, Rich |
| Data | Pandas |
| Testing | Pytest |
| Linting | Ruff |
| Package Manager | UV |

---

## Demo Scenarios

### 1. Bug Fixing (4 intentional bugs in `src/services/task_service.py`)

| Bug | Method | Symptom |
|-----|--------|---------|
| Case-sensitive search | `search_tasks()` | Searching `"report"` doesn't match `"Quarterly Report"` |
| Missing `updated_at` | `update_task()` | Timestamp never changes after update |
| Reversed comparison | `get_overdue_tasks()` | Returns future tasks instead of past-due ones |
| Division by zero | `get_stats()` | Crashes on `ZeroDivisionError` when no tasks exist |

**How to demo:** Ask Devin to "find and fix the bugs in task_service.py" or "write missing tests and fix the failures."

### 2. Writing Missing Tests

The test suite in `tests/test_task_service.py` intentionally omits:
- `TestUpdateTask` — would catch the `updated_at` bug
- `TestSearchTasks` — would catch the case-sensitivity bug
- `TestGetOverdueTasks` — would catch the date comparison bug
- `TestGetStats` — would catch the division-by-zero bug

**How to demo:** Ask Devin to "increase test coverage for TaskService."

### 3. Code Refactoring (`src/utils/text_processing.py`)

The text processing module works correctly but has poor code quality:
- Regular expressions compiled on every call (should use `re.compile`)
- Manual frequency counting (should use `collections.Counter`)
- Overly nested helper functions in `analyze_text()` (should be flattened)

**How to demo:** Ask Devin to "refactor text_processing.py for performance and readability."

### 4. Feature Development

Ideas for new feature demos:
- Add task tagging (many-to-many relationship)
- Add task assignment (assign to users)
- Add recurring tasks
- Add a `/tasks/export` endpoint that returns CSV
- Add task dependencies (blocked-by relationship)

**How to demo:** Ask Devin to "add a tagging system to tasks" or any feature from the list above.

### 5. Data Analysis (`data/sales_data.csv`)

The sales data has 24 records across Electronics and Furniture categories, 4 regions, and 4 salespeople. The `data_processor.py` module provides helpers for:
- Loading and filtering CSV/JSON data
- Aggregating by columns (group-by + sum/mean)
- Summarizing data shape and types

**How to demo:** Ask Devin to "analyze sales_data.csv and generate a quarterly report."

### 6. DevOps & CI

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs:
1. **Lint** — `ruff check .` and `ruff format --check .`
2. **Test** — `pytest` (depends on lint passing)

**How to demo:** Ask Devin to "add code coverage reporting to CI" or "add a Docker deployment step."

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/tasks` | List tasks (filter: `?status=todo`) |
| GET | `/tasks/search` | Search by title/desc (`?q=...`) |
| GET | `/tasks/overdue` | Overdue tasks |
| GET | `/tasks/stats` | Aggregate statistics |
| GET | `/tasks/{id}` | Get single task |
| POST | `/tasks` | Create task |
| PATCH | `/tasks/{id}` | Update task |
| POST | `/tasks/{id}/complete` | Mark done |
| DELETE | `/tasks/{id}` | Delete task |

## CLI Commands

```bash
uv run python -m src.cli add "Task title" --priority high --due 2024-12-31
uv run python -m src.cli list --status todo
uv run python -m src.cli done 1
uv run python -m src.cli stats
```

---

## Contributing

This is a playground repo — feel free to experiment! The intentional bugs and gaps are there by design for demo purposes.
