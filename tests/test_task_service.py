"""Tests for TaskService.

These classes cover the four methods that previously held intentional demo
bugs (now fixed): update_task (updated_at), search_tasks (case-insensitivity),
get_overdue_tasks (date comparison), and get_stats (empty-list division).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from src.models.task import TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from src.services.task_service import TaskNotFoundError, TaskService


class TestCreateTask:
    """Tests for TaskService.create_task()."""

    def test_create_returns_task_with_id(self, service: TaskService) -> None:
        payload = TaskCreate(title="My first task")
        task = service.create_task(payload)
        assert task.id == 1
        assert task.title == "My first task"
        assert task.status == TaskStatus.TODO

    def test_create_increments_id(self, service: TaskService) -> None:
        service.create_task(TaskCreate(title="Task A"))
        task_b = service.create_task(TaskCreate(title="Task B"))
        assert task_b.id == 2

    def test_create_with_priority(self, service: TaskService) -> None:
        payload = TaskCreate(title="Urgent", priority=TaskPriority.HIGH)
        task = service.create_task(payload)
        assert task.priority == TaskPriority.HIGH


class TestGetTask:
    """Tests for TaskService.get_task()."""

    def test_get_existing_task(self, populated_service: TaskService) -> None:
        task = populated_service.get_task(1)
        assert task.title == "Write unit tests"

    def test_get_missing_task_raises(self, service: TaskService) -> None:
        with pytest.raises(TaskNotFoundError):
            service.get_task(999)


class TestListTasks:
    """Tests for TaskService.list_tasks()."""

    def test_list_all(self, populated_service: TaskService) -> None:
        tasks = populated_service.list_tasks()
        assert len(tasks) == 3

    def test_list_with_status_filter(self, populated_service: TaskService) -> None:
        populated_service.complete_task(1)
        done_tasks = populated_service.list_tasks(status=TaskStatus.DONE)
        assert len(done_tasks) == 1
        assert done_tasks[0].id == 1


class TestDeleteTask:
    """Tests for TaskService.delete_task()."""

    def test_delete_existing(self, populated_service: TaskService) -> None:
        populated_service.delete_task(1)
        assert len(populated_service.list_tasks()) == 2

    def test_delete_missing_raises(self, service: TaskService) -> None:
        with pytest.raises(TaskNotFoundError):
            service.delete_task(42)


class TestCompleteTask:
    """Tests for TaskService.complete_task()."""

    def test_complete_changes_status(self, populated_service: TaskService) -> None:
        task = populated_service.complete_task(2)
        assert task.status == TaskStatus.DONE


class TestUpdateTask:
    """Tests for TaskService.update_task()."""

    def test_update_changes_fields(self, populated_service: TaskService) -> None:
        updated = populated_service.update_task(1, TaskUpdate(title="Renamed"))
        assert updated.title == "Renamed"

    def test_update_missing_raises(self, service: TaskService) -> None:
        with pytest.raises(TaskNotFoundError):
            service.update_task(999, TaskUpdate(title="Nope"))

    def test_update_refreshes_updated_at(self, populated_service: TaskService) -> None:
        original = populated_service.get_task(1)
        updated = populated_service.update_task(1, TaskUpdate(title="Renamed"))
        assert updated.updated_at > original.updated_at


class TestSearchTasks:
    """Tests for TaskService.search_tasks()."""

    def test_search_matches_title(self, populated_service: TaskService) -> None:
        results = populated_service.search_tasks("README")
        assert [task.id for task in results] == [2]

    def test_search_matches_description(self, populated_service: TaskService) -> None:
        results = populated_service.search_tasks("v0.1 release")
        assert [task.id for task in results] == [3]

    def test_search_is_case_insensitive(self, populated_service: TaskService) -> None:
        results = populated_service.search_tasks("readme")
        assert [task.id for task in results] == [2]

    def test_search_no_match(self, populated_service: TaskService) -> None:
        assert populated_service.search_tasks("nonexistent") == []


class TestGetOverdueTasks:
    """Tests for TaskService.get_overdue_tasks()."""

    def test_returns_past_due_tasks(self, service: TaskService) -> None:
        past = datetime.now(UTC) - timedelta(days=1)
        service.create_task(TaskCreate(title="Late", due_date=past))
        overdue = service.get_overdue_tasks()
        assert [task.title for task in overdue] == ["Late"]

    def test_excludes_future_due_tasks(self, service: TaskService) -> None:
        future = datetime.now(UTC) + timedelta(days=1)
        service.create_task(TaskCreate(title="Upcoming", due_date=future))
        assert service.get_overdue_tasks() == []

    def test_excludes_done_tasks(self, service: TaskService) -> None:
        past = datetime.now(UTC) - timedelta(days=1)
        task = service.create_task(TaskCreate(title="Done late", due_date=past))
        service.complete_task(task.id)
        assert service.get_overdue_tasks() == []

    def test_excludes_tasks_without_due_date(self, service: TaskService) -> None:
        service.create_task(TaskCreate(title="No due date"))
        assert service.get_overdue_tasks() == []


class TestGetStats:
    """Tests for TaskService.get_stats()."""

    def test_stats_empty_service(self, service: TaskService) -> None:
        stats = service.get_stats()
        assert stats.total == 0
        assert stats.completion_rate == 0.0
        assert stats.overdue == 0

    def test_stats_counts_by_status(self, populated_service: TaskService) -> None:
        populated_service.complete_task(1)
        stats = populated_service.get_stats()
        assert stats.total == 3
        assert stats.by_status[TaskStatus.DONE.value] == 1
        assert stats.by_status[TaskStatus.TODO.value] == 2

    def test_stats_completion_rate(self, populated_service: TaskService) -> None:
        populated_service.complete_task(1)
        stats = populated_service.get_stats()
        assert stats.completion_rate == round(1 / 3, 4)

    def test_stats_counts_by_priority(self, populated_service: TaskService) -> None:
        stats = populated_service.get_stats()
        assert stats.by_priority[TaskPriority.HIGH.value] == 2
        assert stats.by_priority[TaskPriority.LOW.value] == 1
