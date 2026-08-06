---
name: testing-and-linting
description: Running pytest, ruff lint/format, CI pipeline details, and a map of intentionally missing tests. Use when running tests, checking code quality, or debugging CI.
---

# Skill: Running Tests and Linting

Use this skill when running the test suite, checking code quality, or working with CI.

## Running Tests

```bash
uv run pytest
```

- Runs all tests in `tests/` (configured via `[tool.pytest.ini_options]` in `pyproject.toml`).
- The `-v` flag is applied automatically (set in `addopts`).
- 47 tests across 5 test files should pass on a clean checkout.

### Test Files

| File                          | What it covers                           |
|-------------------------------|------------------------------------------|
| `tests/test_task_service.py`  | `TaskService` CRUD operations            |
| `tests/test_api.py`           | FastAPI endpoint integration tests       |
| `tests/test_text_processing.py` | Text utility functions                |
| `tests/test_data_processor.py`  | CSV/JSON data utilities (uses `data/sales_data.csv`) |
| `tests/test_cli.py`           | Typer CLI commands and JSON persistence  |

### Shared Fixtures (`tests/conftest.py`)

- `service` - a fresh empty `TaskService` instance.
- `populated_service` - a `TaskService` pre-loaded with 3 sample tasks ("Write unit tests" HIGH, "Update README" LOW, "Deploy to production" HIGH).

### Running specific tests

```bash
# Single file
uv run pytest tests/test_task_service.py

# Single class
uv run pytest tests/test_task_service.py::TestCreateTask

# Single test
uv run pytest tests/test_task_service.py::TestCreateTask::test_create_returns_task_with_id

# With output capture disabled (see print statements)
uv run pytest -s
```

## Linting and Formatting

```bash
# Check for lint errors
uv run ruff check .

# Check formatting (dry-run)
uv run ruff format --check .

# Auto-fix lint issues
uv run ruff check . --fix

# Auto-format code
uv run ruff format .
```

### Ruff Configuration (in `pyproject.toml`)

- Line length: 100
- Target: Python 3.11
- Enabled rule sets: `E` (pycodestyle errors), `F` (pyflakes), `I` (isort), `UP` (pyupgrade), `B` (bugbear), `C4` (comprehensions)
- Per-file ignores:
  - `src/api/main.py`: `B008` (FastAPI uses `Query`/`Depends` in function defaults by design)
  - `src/utils/text_processing.py`: `C401`, `C416`, `B007` (intentionally refactor-worthy code for demos)

## CI Pipeline (`.github/workflows/ci.yml`)

GitHub Actions runs on push to `main` and on pull requests targeting `main`:

1. **`lint` job**: `uv sync --all-extras` then `ruff check .` and `ruff format --check .`
2. **`test` job** (depends on lint): `uv sync --all-extras` then `pytest`

Both jobs use `astral-sh/setup-uv@v3` to install `uv` and run on `ubuntu-latest`.

Always run both lint and tests locally before pushing:
```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest
```

## Intentionally Missing Tests

The test suite **intentionally omits** these test classes in `tests/test_task_service.py` (they are part of the demo workflow):

| Missing Test Class     | Would catch this bug in `task_service.py`       |
|------------------------|-------------------------------------------------|
| `TestUpdateTask`       | `update_task()` does not refresh `updated_at`   |
| `TestSearchTasks`      | `search_tasks()` is case-sensitive (should not be) |
| `TestGetOverdueTasks`  | `get_overdue_tasks()` has reversed date comparison |
| `TestGetStats`         | `get_stats()` raises `ZeroDivisionError` on empty task list |

When asked to improve test coverage, write tests for these classes first. The bugs are marked with `# BUG:` comments in `src/services/task_service.py`.
