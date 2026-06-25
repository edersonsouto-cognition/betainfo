"""Tests for the Typer CLI (src/cli.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from src.cli import _get_service, _persist, app
from src.models.task import TaskCreate
from src.services.task_service import TaskService

runner = CliRunner()


@pytest.fixture(autouse=True)
def _reset_service(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset the module-level _service and point DATA_FILE to tmp."""
    import src.cli as cli_module

    cli_module._service = None
    tmp_file = tmp_path / "cli_tasks.json"
    monkeypatch.setattr(cli_module, "DATA_FILE", tmp_file)


class TestGetService:
    """Tests for _get_service() lazy-load logic."""

    def test_returns_fresh_service(self) -> None:
        service = _get_service()
        assert isinstance(service, TaskService)
        assert service.list_tasks() == []

    def test_caches_service_on_second_call(self) -> None:
        s1 = _get_service()
        s2 = _get_service()
        assert s1 is s2

    def test_hydrates_from_disk(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import src.cli as cli_module

        tmp_file = tmp_path / "cli_tasks.json"
        data = [
            {
                "id": 5,
                "title": "Persisted task",
                "description": "",
                "status": "todo",
                "priority": "medium",
                "created_at": "2024-01-01T00:00:00+00:00",
                "updated_at": "2024-01-01T00:00:00+00:00",
                "due_date": None,
            }
        ]
        tmp_file.write_text(json.dumps(data))
        monkeypatch.setattr(cli_module, "DATA_FILE", tmp_file)
        cli_module._service = None

        service = _get_service()
        tasks = service.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Persisted task"
        assert tasks[0].id == 5
        # next_id should be incremented past existing max id
        assert service._next_id == 6


class TestPersist:
    """Tests for _persist() disk write logic."""

    def test_persist_writes_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import src.cli as cli_module

        tmp_file = tmp_path / "cli_tasks.json"
        monkeypatch.setattr(cli_module, "DATA_FILE", tmp_file)
        cli_module._service = None

        service = _get_service()
        service.create_task(TaskCreate(title="Persist me"))
        _persist()

        assert tmp_file.exists()
        data = json.loads(tmp_file.read_text())
        assert len(data) == 1
        assert data[0]["title"] == "Persist me"


class TestAddCommand:
    """Tests for the 'add' CLI command."""

    def test_add_basic(self) -> None:
        result = runner.invoke(app, ["add", "My new task"])
        assert result.exit_code == 0
        assert "Created task #1" in result.output
        assert "My new task" in result.output

    def test_add_with_priority(self) -> None:
        result = runner.invoke(app, ["add", "Urgent thing", "--priority", "high"])
        assert result.exit_code == 0
        assert "Created task #1" in result.output

    def test_add_with_due_date(self) -> None:
        result = runner.invoke(app, ["add", "Deadline task", "--due", "2025-12-31"])
        assert result.exit_code == 0
        assert "Created task #1" in result.output


class TestListCommand:
    """Tests for the 'list' CLI command."""

    def test_list_empty(self) -> None:
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No tasks found" in result.output

    def test_list_after_add(self) -> None:
        runner.invoke(app, ["add", "Task A"])
        runner.invoke(app, ["add", "Task B"])
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Task A" in result.output
        assert "Task B" in result.output

    def test_list_with_status_filter(self) -> None:
        runner.invoke(app, ["add", "Todo task"])
        result = runner.invoke(app, ["list", "--status", "todo"])
        assert result.exit_code == 0
        assert "Todo task" in result.output


class TestDoneCommand:
    """Tests for the 'done' CLI command."""

    def test_done_marks_complete(self) -> None:
        runner.invoke(app, ["add", "Finish me"])
        result = runner.invoke(app, ["done", "1"])
        assert result.exit_code == 0
        assert "marked as done" in result.output

    def test_done_missing_task(self) -> None:
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
        runner.invoke(app, ["add", "Task 1"])
        runner.invoke(app, ["add", "Task 2"])
        runner.invoke(app, ["done", "1"])
        result = runner.invoke(app, ["stats"])
        assert result.exit_code == 0
        assert "Total tasks" in result.output
        assert "Completion rate" in result.output
