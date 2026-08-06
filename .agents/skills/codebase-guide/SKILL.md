---
name: codebase-guide
description: Codebase architecture, directory layout, historical bugs that were fixed, refactoring opportunities, and demo scenario prompts. Use when navigating the code or understanding the project design.
---

# Skill: Codebase Architecture and Demo Scenarios

Use this skill to understand the project structure, key design decisions, and the refactoring opportunities built into this demo playground.

## Project Purpose

This is a **Task Manager API playground** designed for Devin demo recordings. It contains refactor-worthy code and sample data so that Devin can showcase testing, refactoring, feature development, and data analysis. The original `task_service.py` bugs have been fixed and are now covered by tests.

## Directory Layout

```
betainfo/
├── src/
│   ├── api/
│   │   └── main.py              # FastAPI app factory + route definitions
│   ├── models/
│   │   └── task.py              # Pydantic v2 schemas and enums
│   ├── services/
│   │   └── task_service.py      # In-memory CRUD service
│   ├── utils/
│   │   ├── text_processing.py   # Text helpers (intentionally refactor-worthy)
│   │   └── data_processor.py    # pandas CSV/JSON utilities
│   └── cli.py                   # Typer + Rich CLI
├── tests/
│   ├── conftest.py              # Shared fixtures (service, populated_service)
│   ├── test_api.py              # FastAPI endpoint integration tests
│   ├── test_cli.py              # Typer CLI commands and persistence
│   ├── test_data_processor.py   # Data processor tests
│   ├── test_models.py           # Pydantic model validation and serialization
│   ├── test_task_service.py     # TaskService CRUD operations and queries
│   └── test_text_processing.py  # Text utility tests
├── data/
│   ├── sales_data.csv           # 24 sales records (Electronics, Furniture across 4 regions)
│   └── sample_tasks.json        # 6 pre-populated tasks for demos
├── .github/workflows/
│   └── ci.yml                   # GitHub Actions: lint then test
└── pyproject.toml               # Dependencies, build config, tool settings
```

## Tech Stack

| Layer           | Technology                     |
|-----------------|--------------------------------|
| API Framework   | FastAPI + Uvicorn              |
| CLI Framework   | Typer + Rich                   |
| Data Models     | Pydantic v2                    |
| Data Processing | pandas                         |
| Testing         | pytest                         |
| Linting         | Ruff                           |
| Package Manager | uv                             |
| CI              | GitHub Actions                 |
| Build Backend   | Hatchling                      |

## Key Components

### TaskService (`src/services/task_service.py`)
The core business logic layer. Operates as an in-memory dict-based store (`self._tasks: dict[int, Task]`). Provides: `create_task`, `get_task`, `list_tasks`, `update_task`, `delete_task`, `complete_task`, `search_tasks`, `get_overdue_tasks`, `get_stats`.

### Pydantic Models (`src/models/task.py`)
- `TaskStatus` (StrEnum): `todo`, `in_progress`, `done`
- `TaskPriority` (StrEnum): `low`, `medium`, `high`
- `TaskCreate` / `TaskUpdate`: input schemas
- `Task`: persisted task with `id`, `status`, `created_at`, `updated_at`
- `TaskStats`: aggregate statistics model

### FastAPI App (`src/api/main.py`)
Uses an app factory pattern (`create_app()`). The shared `TaskService` instance is injected via `Depends(get_service)`. All routes are defined inside the factory function.

### CLI (`src/cli.py`)
Hydrates a `TaskService` from `data/cli_tasks.json` on first access. When that file does not exist yet (first run), it seeds from `data/sample_tasks.json` instead. After mutations (`add`, `done`), persists the state back to `data/cli_tasks.json`.

## Historical Bugs (fixed)

The original `task_service.py` contained four bugs that were fixed in a previous demo. The fixes and their tests now live in `tests/test_task_service.py`:

- Case-insensitive `search_tasks()`
- `updated_at` refresh in `update_task()`
- Correct date comparison in `get_overdue_tasks()`
- Zero-division guard in `get_stats()`

## Refactoring Opportunity (`src/utils/text_processing.py`)

The module works correctly but has intentionally poor code quality:
- Regular expressions are re-compiled on every function call (should use `re.compile` at module level).
- Word/character counting uses manual loops (should use `collections.Counter`).
- `analyze_text()` nests multiple helper functions unnecessarily (should be flattened to module-level).

## Demo Scenarios

| Scenario              | Prompt suggestion                                          |
|-----------------------|------------------------------------------------------------|
| Code refactoring      | "Refactor text_processing.py for performance/readability"  |
| Feature development   | "Add a tagging system to tasks"                            |
| Data analysis         | "Analyze sales_data.csv and generate a quarterly report"   |
| DevOps                | "Add code coverage reporting to CI"                        |

## Data Files

- **`data/sales_data.csv`**: 24 rows, 7 columns (`date`, `product`, `category`, `quantity`, `price`, `region`, `salesperson`). Categories: Electronics, Furniture. Regions: North, South, East, West.
- **`data/sample_tasks.json`**: 6 pre-populated tasks used by the CLI for demo hydration.
