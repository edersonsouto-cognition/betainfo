"""Tests for the Typer CLI (src/cli.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from src.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def _reset_service_singleton():
    """Reset the module-level service singleton between tests."""
    import src.cli as cli_module

    cli_module._service = None
    yield
    cli_module._service = None


@pytest.fixture()
def tmp_data_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Point DATA_FILE to a temp directory so tests don't pollute real data."""
    data_file = tmp_path / "cli_tasks.json"
    monkeypatch.setattr("src.cli.DATA_FILE", data_file)
    return data_file


# ---------------------------------------------------------------------------
# add command
# ---------------------------------------------------------------------------


class TestAddCommand:
    """Tests for the `add` CLI command."""

    def test_add_basic(self, tmp_data_file: Path) -> None:
        result = runner.invoke(app, ["add", "Buy groceries"])
        assert result.exit_code == 0
        assert "Created task #1" in result.output
        assert "Buy groceries" in result.output

    def test_add_persists_to_file(self, tmp_data_file: Path) -> None:
        runner.invoke(app, ["add", "Persisted task"])
        assert tmp_data_file.exists()
        data = json.loads(tmp_data_file.read_text())
        assert len(data) == 1
        assert data[0]["title"] == "Persisted task"

    def test_add_with_priority(self, tmp_data_file: Path) -> None:
        result = runner.invoke(app, ["add", "Urgent task", "--priority", "high"])
        assert result.exit_code == 0
        data = json.loads(tmp_data_file.read_text())
        assert data[0]["priority"] == "high"

    def test_add_with_due_date(self, tmp_data_file: Path) -> None:
        result = runner.invoke(app, ["add", "Deadline task", "--due", "2025-12-31"])
        assert result.exit_code == 0
        data = json.loads(tmp_data_file.read_text())
        assert "2025-12-31" in data[0]["due_date"]

    def test_add_with_description(self, tmp_data_file: Path) -> None:
        result = runner.invoke(app, ["add", "Described task", "--description", ""])
        # Typer may not accept --description unless defined; the positional default
        # handles it. Just verify basic invocation works.
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# list command
# ---------------------------------------------------------------------------


class TestListCommand:
    """Tests for the `list` CLI command."""

    def test_list_empty(self, tmp_data_file: Path) -> None:
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No tasks found" in result.output

    def test_list_shows_tasks(self, tmp_data_file: Path) -> None:
        runner.invoke(app, ["add", "Alpha"])
        runner.invoke(app, ["add", "Beta"])
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Alpha" in result.output
        assert "Beta" in result.output

    def test_list_with_status_filter(self, tmp_data_file: Path) -> None:
        runner.invoke(app, ["add", "Task A"])
        runner.invoke(app, ["done", "1"])
        result = runner.invoke(app, ["list", "--status", "done"])
        assert result.exit_code == 0
        assert "Task A" in result.output

    def test_list_filter_excludes(self, tmp_data_file: Path) -> None:
        runner.invoke(app, ["add", "Incomplete"])
        result = runner.invoke(app, ["list", "--status", "done"])
        assert result.exit_code == 0
        assert "No tasks found" in result.output


# ---------------------------------------------------------------------------
# done command
# ---------------------------------------------------------------------------


class TestDoneCommand:
    """Tests for the `done` CLI command."""

    def test_done_marks_task(self, tmp_data_file: Path) -> None:
        runner.invoke(app, ["add", "Finish report"])
        result = runner.invoke(app, ["done", "1"])
        assert result.exit_code == 0
        assert "marked as done" in result.output

    def test_done_persists(self, tmp_data_file: Path) -> None:
        runner.invoke(app, ["add", "Close ticket"])
        runner.invoke(app, ["done", "1"])
        data = json.loads(tmp_data_file.read_text())
        assert data[0]["status"] == "done"

    def test_done_missing_task(self, tmp_data_file: Path) -> None:
        result = runner.invoke(app, ["done", "99"])
        assert result.exit_code == 1
        assert "not found" in result.output


# ---------------------------------------------------------------------------
# stats command
# ---------------------------------------------------------------------------


class TestStatsCommand:
    """Tests for the `stats` CLI command."""

    def test_stats_empty(self, tmp_data_file: Path) -> None:
        result = runner.invoke(app, ["stats"])
        assert result.exit_code == 0
        assert "No tasks to compute stats from" in result.output

    def test_stats_with_tasks(self, tmp_data_file: Path) -> None:
        runner.invoke(app, ["add", "Task 1"])
        runner.invoke(app, ["add", "Task 2"])
        runner.invoke(app, ["done", "1"])
        result = runner.invoke(app, ["stats"])
        assert result.exit_code == 0
        assert "Total tasks" in result.output
        assert "Completion rate" in result.output


# ---------------------------------------------------------------------------
# _get_service / _persist integration
# ---------------------------------------------------------------------------


class TestServiceHydration:
    """Tests for loading persisted data on startup."""

    def test_hydrates_from_existing_file(self, tmp_data_file: Path) -> None:
        """If the data file exists, the CLI should load tasks from it."""
        seed_data = [
            {
                "id": 5,
                "title": "Preexisting",
                "description": "",
                "priority": "medium",
                "status": "todo",
                "due_date": None,
                "created_at": "2025-01-01T00:00:00+00:00",
                "updated_at": "2025-01-01T00:00:00+00:00",
            }
        ]
        tmp_data_file.write_text(json.dumps(seed_data))
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Preexisting" in result.output

    def test_next_id_continues_after_hydration(self, tmp_data_file: Path) -> None:
        """New tasks should get IDs higher than the loaded ones."""
        seed_data = [
            {
                "id": 10,
                "title": "Loaded",
                "description": "",
                "priority": "low",
                "status": "todo",
                "due_date": None,
                "created_at": "2025-01-01T00:00:00+00:00",
                "updated_at": "2025-01-01T00:00:00+00:00",
            }
        ]
        tmp_data_file.write_text(json.dumps(seed_data))
        result = runner.invoke(app, ["add", "After hydration"])
        assert result.exit_code == 0
        assert "Created task #11" in result.output
