---
name: add-new-cli-command
description: Add a new Typer CLI command following this repo's conventions.
---

## Steps

1. Add the command to the existing Typer app in `src/cli.py` with `@app.command()` (one command per function); do not create a new Typer app or module.
2. Use typed arguments and `Annotated[..., typer.Option("--flag", "-f")]` options with help text; never parse `sys.argv` manually.
3. Get the shared service with `_get_service()` and call `_persist()` after any mutation, matching `add` and `done`.
4. Put business logic in `TaskService` (`src/services/task_service.py`) so the API gets it too; the command should only handle input, output, and errors.
5. Print user-facing output with `console.print` (Rich `Table` for tabular data). On failure, print a message and `raise typer.Exit(code=1)` so the exit code is non-zero.
6. Add tests in `tests/test_cli.py` using the existing `CliRunner` pattern (success and failure cases), reusing the `cli_env` fixture so the command runs against an isolated `tmp_path` data file.
7. Update the CLI section of the README with the new command and an example, and the CLI command list in the `build-and-run` skill.
8. Run the `run-quality-checks-before-pr` skill before opening the PR.
