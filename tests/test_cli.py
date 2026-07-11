"""Tests for the Typer CLI (``src/cli.py``).

These cover the CLI-specific behaviour: seeding from ``sample_tasks.json`` on
first run, persistence to ``cli_tasks.json``, and the ``add``/``list``/``done``
commands. Statistics aggregation is exercised by the service-layer suite.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from src import cli

runner = CliRunner()

SEED_DATA = [
    {
        "id": 1,
        "title": "Seeded todo",
        "description": "",
        "priority": "high",
        "status": "todo",
        "due_date": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    },
    {
        "id": 2,
        "title": "Seeded done",
        "description": "",
        "priority": "low",
        "status": "done",
        "due_date": None,
        "created_at": "2024-01-02T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
    },
]


@pytest.fixture()
def cli_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolate the CLI's data files and reset its cached service."""
    monkeypatch.setattr(cli, "DATA_FILE", tmp_path / "cli_tasks.json")
    monkeypatch.setattr(cli, "SEED_FILE", tmp_path / "sample_tasks.json")
    monkeypatch.setattr(cli, "_service", None)
    return tmp_path


def _write_seed(cli_env: Path) -> None:
    cli.SEED_FILE.write_text(json.dumps(SEED_DATA))


class TestListCommand:
    def test_list_empty_without_data_or_seed(self, cli_env: Path) -> None:
        result = runner.invoke(cli.app, ["list"])
        assert result.exit_code == 0
        assert "No tasks found." in result.stdout

    def test_list_seeds_from_sample_when_no_data_file(self, cli_env: Path) -> None:
        _write_seed(cli_env)
        result = runner.invoke(cli.app, ["list"])
        assert result.exit_code == 0
        assert "Seeded todo" in result.stdout
        assert "Seeded done" in result.stdout
        # Reading/seeding must not create the runtime data file.
        assert not cli.DATA_FILE.exists()

    def test_list_reads_data_file_over_seed(self, cli_env: Path) -> None:
        _write_seed(cli_env)
        cli.DATA_FILE.write_text(
            json.dumps(
                [
                    {
                        "id": 10,
                        "title": "Runtime task",
                        "description": "",
                        "priority": "medium",
                        "status": "todo",
                        "due_date": None,
                        "created_at": "2024-02-01T00:00:00Z",
                        "updated_at": "2024-02-01T00:00:00Z",
                    }
                ]
            )
        )
        result = runner.invoke(cli.app, ["list"])
        assert result.exit_code == 0
        assert "Runtime task" in result.stdout
        assert "Seeded todo" not in result.stdout

    def test_list_filters_by_status(self, cli_env: Path) -> None:
        _write_seed(cli_env)
        result = runner.invoke(cli.app, ["list", "--status", "done"])
        assert result.exit_code == 0
        assert "Seeded done" in result.stdout
        assert "Seeded todo" not in result.stdout


class TestAddCommand:
    def test_add_persists_to_data_file(self, cli_env: Path) -> None:
        result = runner.invoke(cli.app, ["add", "Brand new task", "--priority", "high"])
        assert result.exit_code == 0
        assert "Created task #1" in result.stdout
        assert cli.DATA_FILE.exists()
        stored = json.loads(cli.DATA_FILE.read_text())
        assert stored[0]["title"] == "Brand new task"
        assert stored[0]["priority"] == "high"

    def test_add_continues_ids_from_seed(self, cli_env: Path) -> None:
        _write_seed(cli_env)
        result = runner.invoke(cli.app, ["add", "Next task"])
        assert result.exit_code == 0
        assert "Created task #3" in result.stdout
        stored = {t["id"]: t for t in json.loads(cli.DATA_FILE.read_text())}
        assert stored[3]["title"] == "Next task"

    def test_add_with_due_date(self, cli_env: Path) -> None:
        result = runner.invoke(cli.app, ["add", "Dated task", "--due", "2024-12-31"])
        assert result.exit_code == 0
        stored = json.loads(cli.DATA_FILE.read_text())
        assert stored[0]["due_date"].startswith("2024-12-31")


class TestDoneCommand:
    def test_done_marks_task_and_persists(self, cli_env: Path) -> None:
        _write_seed(cli_env)
        result = runner.invoke(cli.app, ["done", "1"])
        assert result.exit_code == 0
        assert "marked as done" in result.stdout
        stored = {t["id"]: t for t in json.loads(cli.DATA_FILE.read_text())}
        assert stored[1]["status"] == "done"

    def test_done_missing_task_errors(self, cli_env: Path) -> None:
        _write_seed(cli_env)
        result = runner.invoke(cli.app, ["done", "999"])
        assert result.exit_code == 1
        assert "not found" in result.stdout
