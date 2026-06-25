"""Tests for the CLI (src/cli.py).

Covers all four Typer commands: add, list, done, stats.
Uses CliRunner and patches the persistent TaskService / data file.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from src.cli import _get_service, app
from src.models.task import TaskPriority
from src.services.task_service import TaskService

runner = CliRunner()


@pytest.fixture(autouse=True)
def _reset_service():
    """Ensure each test starts with a fresh service singleton."""
    import src.cli as cli_module

    cli_module._service = None
    yield
    cli_module._service = None


@pytest.fixture()
def fake_data_file(tmp_path: Path) -> Path:
    """Provide a temporary data file path and patch DATA_FILE to use it."""
    return tmp_path / "cli_tasks.json"


@pytest.fixture(autouse=True)
def _patch_data_file(fake_data_file: Path):
    """Patch DATA_FILE to a temporary location so disk isn't touched."""
    with patch("src.cli.DATA_FILE", fake_data_file):
        yield


class TestGetService:
    """Tests for the lazy-loading _get_service helper."""

    def test_returns_task_service(self) -> None:
        service = _get_service()
        assert isinstance(service, TaskService)

    def test_singleton_returns_same_instance(self) -> None:
        s1 = _get_service()
        s2 = _get_service()
        assert s1 is s2

    def test_loads_existing_data_file(self, fake_data_file: Path) -> None:
        now = datetime.now(UTC)
        tasks_data = [
            {
                "id": 5,
                "title": "Persisted task",
                "description": "",
                "priority": "medium",
                "status": "todo",
                "due_date": None,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }
        ]
        fake_data_file.parent.mkdir(parents=True, exist_ok=True)
        fake_data_file.write_text(json.dumps(tasks_data))

        service = _get_service()
        task = service.get_task(5)
        assert task.title == "Persisted task"
        # next_id should be set past the max existing id
        assert service._next_id == 6


class TestAddCommand:
    """Tests for the 'add' CLI command."""

    def test_add_basic_task(self) -> None:
        result = runner.invoke(app, ["add", "Buy groceries"])
        assert result.exit_code == 0
        assert "Created task #1" in result.output
        assert "Buy groceries" in result.output

    def test_add_with_priority(self) -> None:
        result = runner.invoke(app, ["add", "Urgent fix", "--priority", "high"])
        assert result.exit_code == 0
        assert "Created task #1" in result.output

        service = _get_service()
        task = service.get_task(1)
        assert task.priority == TaskPriority.HIGH

    def test_add_with_due_date(self) -> None:
        result = runner.invoke(app, ["add", "Deadline task", "--due", "2025-12-31"])
        assert result.exit_code == 0
        assert "Created task #1" in result.output

        service = _get_service()
        task = service.get_task(1)
        assert task.due_date is not None
        assert task.due_date.year == 2025

    def test_add_persists_to_file(self, fake_data_file: Path) -> None:
        runner.invoke(app, ["add", "Persisted"])
        assert fake_data_file.exists()
        data = json.loads(fake_data_file.read_text())
        assert len(data) == 1
        assert data[0]["title"] == "Persisted"


class TestListCommand:
    """Tests for the 'list' CLI command."""

    def test_list_empty(self) -> None:
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No tasks found" in result.output

    def test_list_shows_tasks(self) -> None:
        runner.invoke(app, ["add", "Task A"])
        runner.invoke(app, ["add", "Task B"])
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Task A" in result.output
        assert "Task B" in result.output

    def test_list_filter_by_status(self) -> None:
        runner.invoke(app, ["add", "First task"])
        runner.invoke(app, ["add", "Second task"])
        runner.invoke(app, ["done", "1"])
        result = runner.invoke(app, ["list", "--status", "done"])
        assert result.exit_code == 0
        assert "First task" in result.output
        # "Second task" should not appear in the done-filtered output
        assert "Second task" not in result.output

    def test_list_shows_due_date(self) -> None:
        runner.invoke(app, ["add", "With due", "--due", "2025-06-15"])
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "2025-06-15" in result.output


class TestDoneCommand:
    """Tests for the 'done' CLI command."""

    def test_mark_task_done(self) -> None:
        runner.invoke(app, ["add", "Complete me"])
        result = runner.invoke(app, ["done", "1"])
        assert result.exit_code == 0
        assert "marked as done" in result.output

    def test_done_persists(self, fake_data_file: Path) -> None:
        runner.invoke(app, ["add", "Finish this"])
        runner.invoke(app, ["done", "1"])
        data = json.loads(fake_data_file.read_text())
        assert data[0]["status"] == "done"

    def test_done_nonexistent_task(self) -> None:
        result = runner.invoke(app, ["done", "999"])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestStatsCommand:
    """Tests for the 'stats' CLI command."""

    def test_stats_empty(self) -> None:
        result = runner.invoke(app, ["stats"])
        assert result.exit_code == 0
        assert "No tasks to compute stats from" in result.output

    def test_stats_with_tasks(self) -> None:
        runner.invoke(app, ["add", "Task A", "--priority", "high"])
        runner.invoke(app, ["add", "Task B", "--priority", "low"])
        runner.invoke(app, ["done", "1"])
        result = runner.invoke(app, ["stats"])
        assert result.exit_code == 0
        assert "Total tasks" in result.output
        assert "Completion rate" in result.output

    def test_stats_shows_priority_breakdown(self) -> None:
        runner.invoke(app, ["add", "High prio", "--priority", "high"])
        runner.invoke(app, ["add", "Low prio", "--priority", "low"])
        result = runner.invoke(app, ["stats"])
        assert result.exit_code == 0
        assert "priority:" in result.output
