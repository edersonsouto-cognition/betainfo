"""Tests for the Typer CLI (src/cli.py).

These cover the previously untested command-line surface: the add/list/done/
stats commands plus the on-disk seeding, hydration and persistence behaviour of
``_get_service`` / ``_persist``.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from src import cli
from src.models.task import Task, TaskPriority, TaskStatus

runner = CliRunner()


def _make_task(task_id: int, title: str, **overrides: object) -> dict[str, object]:
    now = datetime(2020, 1, 1, tzinfo=UTC)
    task = Task(
        id=task_id,
        title=title,
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        created_at=now,
        updated_at=now,
    )
    return {**task.model_dump(mode="json"), **overrides}


@pytest.fixture()
def cli_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the CLI at a temp data dir and reset its cached service.

    Returns the temp directory so tests can seed/inspect the JSON files.
    """
    data_file = tmp_path / "cli_tasks.json"
    seed_file = tmp_path / "sample_tasks.json"
    monkeypatch.setattr(cli, "DATA_FILE", data_file)
    monkeypatch.setattr(cli, "SEED_FILE", seed_file)
    monkeypatch.setattr(cli, "_service", None)
    return tmp_path


def _invoke(args: list[str]):
    """Run the CLI as a fresh process would: clear the cached service first."""
    cli._service = None
    return runner.invoke(cli.app, args)


def _write_seed(path: Path, tasks: list[dict[str, object]]) -> None:
    path.write_text(json.dumps(tasks, indent=2))


class TestAdd:
    def test_add_reports_and_persists(self, cli_env: Path) -> None:
        result = _invoke(["add", "Buy milk"])
        assert result.exit_code == 0
        assert "Created task #1" in result.stdout
        assert "Buy milk" in result.stdout

        stored = json.loads(cli.DATA_FILE.read_text())
        assert len(stored) == 1
        assert stored[0]["title"] == "Buy milk"
        assert stored[0]["priority"] == "medium"

    def test_add_with_priority_option(self, cli_env: Path) -> None:
        result = _invoke(["add", "Ship release", "--priority", "high"])
        assert result.exit_code == 0
        stored = json.loads(cli.DATA_FILE.read_text())
        assert stored[0]["priority"] == "high"

    def test_add_with_due_date(self, cli_env: Path) -> None:
        result = _invoke(["add", "Pay rent", "--due", "2030-06-01"])
        assert result.exit_code == 0
        stored = json.loads(cli.DATA_FILE.read_text())
        assert stored[0]["due_date"].startswith("2030-06-01")


class TestList:
    def test_list_empty_reports_no_tasks(self, cli_env: Path) -> None:
        result = _invoke(["list"])
        assert result.exit_code == 0
        assert "No tasks found" in result.stdout

    def test_list_shows_seeded_tasks(self, cli_env: Path) -> None:
        _write_seed(cli.SEED_FILE, [_make_task(1, "Seeded task")])
        result = _invoke(["list"])
        assert result.exit_code == 0
        assert "Seeded task" in result.stdout

    def test_list_status_filter(self, cli_env: Path) -> None:
        _write_seed(
            cli.SEED_FILE,
            [
                _make_task(1, "Open task", status="todo"),
                _make_task(2, "Finished task", status="done"),
            ],
        )
        result = _invoke(["list", "--status", "done"])
        assert result.exit_code == 0
        assert "Finished task" in result.stdout
        assert "Open task" not in result.stdout


class TestPersistence:
    def test_add_then_list_across_runs(self, cli_env: Path) -> None:
        _invoke(["add", "Persisted"])
        # A second, independent run must read the task back from disk.
        result = _invoke(["list"])
        assert "Persisted" in result.stdout

    def test_seed_used_only_until_first_write(self, cli_env: Path) -> None:
        _write_seed(cli.SEED_FILE, [_make_task(1, "From seed")])
        _invoke(["add", "From user"])
        stored = json.loads(cli.DATA_FILE.read_text())
        titles = {t["title"] for t in stored}
        # Seed hydrates the store, and the new task keeps a distinct id.
        assert titles == {"From seed", "From user"}
        assert {t["id"] for t in stored} == {1, 2}


class TestDone:
    def test_done_marks_task(self, cli_env: Path) -> None:
        _write_seed(cli.SEED_FILE, [_make_task(1, "Do the thing")])
        result = _invoke(["done", "1"])
        assert result.exit_code == 0
        assert "marked as done" in result.stdout
        stored = json.loads(cli.DATA_FILE.read_text())
        assert stored[0]["status"] == "done"

    def test_done_missing_task_exits_nonzero(self, cli_env: Path) -> None:
        result = _invoke(["done", "999"])
        assert result.exit_code == 1
        assert "not found" in result.stdout


class TestStats:
    def test_stats_empty_reports_nothing_to_compute(self, cli_env: Path) -> None:
        result = _invoke(["stats"])
        assert result.exit_code == 0
        assert "No tasks" in result.stdout

    def test_stats_reports_totals(self, cli_env: Path) -> None:
        _write_seed(
            cli.SEED_FILE,
            [
                _make_task(1, "A", status="done"),
                _make_task(2, "B", status="todo"),
            ],
        )
        result = _invoke(["stats"])
        assert result.exit_code == 0
        assert "Total tasks" in result.stdout
        assert "2" in result.stdout
