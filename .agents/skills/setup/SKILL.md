---
name: setup
description: Setting up the Task Manager API development environment (Python 3.11+, uv, dependencies). Use when a session needs a working dev environment.
---

# Skill: Setting Up the Development Environment

Use this skill when setting up the Task Manager API project for the first time, or when a new Devin session needs a working dev environment.

## Prerequisites

- Python 3.11+ (check with `python3 --version`)
- `uv` package manager (check with `uv --version`; install via `curl -LsSf https://astral.sh/uv/install.sh | sh` if missing)

## Steps

1. **Clone the repo** (skip if already cloned):
   ```bash
   git clone https://github.com/edersonsouto-cognition/betainfo.git
   cd betainfo
   ```

2. **Install all dependencies** (including dev extras for pytest and ruff):
   ```bash
   uv sync --all-extras
   ```
   This creates a `.venv/` virtual environment and installs both runtime and dev dependencies. The `--all-extras` flag is required to get `pytest` and `ruff`.

3. **Verify the install** by running the test suite:
   ```bash
   uv run pytest
   ```
   All 47 tests should pass.

4. **Verify linting** passes:
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   ```

## Key details

- The project uses `uv` (not pip/poetry/pipenv). Always prefix commands with `uv run` to use the managed virtualenv.
- `pyproject.toml` defines all dependencies and tool configuration (ruff, pytest).
- The `[project.scripts]` entry registers a `taskman` CLI, but during development use `uv run python -m src.cli` instead.
- There is no `.env` file or environment variables required for basic setup.
- The `.venv/` directory is gitignored and created automatically by `uv sync`.

## Troubleshooting

- If `uv sync` fails, ensure Python >= 3.11 is available. `uv` will auto-detect the Python version.
- If tests fail on import errors, ensure you ran `uv sync --all-extras` (not just `uv sync`), since pytest and ruff are in the `[project.optional-dependencies] dev` group.
