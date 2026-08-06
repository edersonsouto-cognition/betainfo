# Task Manager API – Devin Demo Playground

A feature-rich Task Manager project designed for **Devin demo recordings**. It includes refactor-worthy code and sample data — all set up to showcase testing, refactoring, feature development, and DevOps demos.

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
│   ├── services/         # Business logic
│   │   └── task_service.py
│   ├── utils/
│   │   ├── text_processing.py   # Refactor-worthy text helpers
│   │   └── data_processor.py    # CSV/JSON wrangling with pandas
│   └── cli.py            # Typer + Rich CLI
├── tests/                # Pytest suite
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
| Package Manager | uv |

---

## Demo Scenarios

### 1. Bug Fixing History (`src/services/task_service.py`)

The four original TaskService bugs (case-sensitive search, missing `updated_at` refresh, reversed overdue comparison, and division-by-zero in `get_stats`) have been fixed and are covered by tests in `tests/test_task_service.py`.

**How to demo:** Ask Devin to "show the git history of the fixed TaskService bugs" or "refactor task_service.py for clarity."

### 2. Writing Tests

`tests/test_task_service.py` now covers the TaskService CRUD and query methods (search, overdue detection, and statistics). New features are the best place to extend coverage.

**How to demo:** Ask Devin to "increase test coverage for a new feature."

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

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on pushes and pull requests targeting `main`:
1. **Lint** — `ruff check .` and `ruff format --check .`
2. **Test** — `pytest` (depends on lint passing)

`setup-uv` pins uv to `0.11.28` so the CI setup does not depend on a GitHub API "latest" lookup, which can fail due to rate limits.

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

This is a playground repo — feel free to experiment! The remaining refactor-worthy code and sample data are there by design for demo purposes.
