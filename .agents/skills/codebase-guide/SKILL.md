---
name: codebase-guide
description: Codebase architecture, directory layout, refactoring opportunities, and demo scenario prompts. Use when navigating the code or understanding the project design.
---

# Skill: Codebase Architecture and Demo Scenarios

Use this skill to understand the project structure, key design decisions, and the refactoring opportunities built into this demo playground.

## Project Purpose

This is a **Task Manager API playground** designed for Devin demo recordings. It contains refactor-worthy code and sample data so that Devin can showcase testing, refactoring, and feature development capabilities.

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
│   ├── test_task_service.py     # Service tests (CRUD and query methods)
│   ├── test_api.py              # FastAPI endpoint tests
│   ├── test_text_processing.py  # Text utility tests
│   ├── test_data_processor.py   # Data processor tests
│   └── test_cli.py              # Typer CLI tests
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

## Historical TaskService Bugs (Fixed)

`src/services/task_service.py` previously contained four intentional demo bugs. They have since been fixed and are covered by `tests/test_task_service.py`:

1. **Case-sensitive search** (`search_tasks`) — now case-insensitive.
2. **Missing `updated_at` refresh** (`update_task`) — now refreshes `updated_at` on every change.
3. **Reversed overdue comparison** (`get_overdue_tasks`) — now correctly identifies past-due tasks.
4. **Division by zero** (`get_stats`) — now returns `0.0` for an empty task list.

The remaining refactor-worthy area is `src/utils/text_processing.py`.

## Refactoring Opportunity (`src/utils/text_processing.py`)

The module works correctly but has intentionally poor code quality:
- Regular expressions are re-compiled on every function call (should use `re.compile` at module level).
- Word/character counting uses manual loops (should use `collections.Counter`).
- `analyze_text()` nests multiple helper functions unnecessarily (should be flattened to module-level).

## Demo Scenarios

| Scenario              | Prompt suggestion                                          |
|-----------------------|------------------------------------------------------------|
| Bug fixing history    | "Show the git history of the fixed TaskService bugs"       |
| Writing tests         | "Increase test coverage for new features"                  |
| Code refactoring      | "Refactor text_processing.py for performance/readability"  |
| Feature development   | "Add a tagging system to tasks"                            |
| Data analysis         | "Analyze sales_data.csv and generate a quarterly report"   |
| DevOps                | "Add code coverage reporting to CI"                        |

## Data Files

- **`data/sales_data.csv`**: 24 rows, 7 columns (`date`, `product`, `category`, `quantity`, `price`, `region`, `salesperson`). Categories: Electronics, Furniture. Regions: North, South, East, West.
- **`data/sample_tasks.json`**: 6 pre-populated tasks used by the CLI for demo hydration.
