"""Tests for TaskService."""

from __future__ import annotations

import time
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

    def test_update_refreshes_updated_at(self, service: TaskService) -> None:
        task = service.create_task(TaskCreate(title="Original title"))
        original_updated_at = task.updated_at
        time.sleep(0.01)
        updated = service.update_task(task.id, TaskUpdate(title="New title"))
        assert updated.title == "New title"
        assert updated.updated_at > original_updated_at

    def test_update_persists_change(self, service: TaskService) -> None:
        task = service.create_task(TaskCreate(title="Original title"))
        service.update_task(task.id, TaskUpdate(priority=TaskPriority.HIGH))
        assert service.get_task(task.id).priority == TaskPriority.HIGH

    def test_partial_update_keeps_other_fields(self, populated_service: TaskService) -> None:
        updated = populated_service.update_task(1, TaskUpdate(title="Renamed"))
        assert updated.title == "Renamed"
        assert updated.priority == TaskPriority.HIGH
        assert updated.created_at == populated_service.get_task(1).created_at

    def test_update_missing_raises(self, service: TaskService) -> None:
        with pytest.raises(TaskNotFoundError):
            service.update_task(42, TaskUpdate(title="Nope"))


class TestSearchTasks:
    """Tests for TaskService.search_tasks()."""

    def test_search_title_is_case_insensitive(self, service: TaskService) -> None:
        task = service.create_task(TaskCreate(title="Quarterly Report"))
        results = service.search_tasks("report")
        assert [found.id for found in results] == [task.id]

    def test_search_description_is_case_insensitive(self, service: TaskService) -> None:
        task = service.create_task(
            TaskCreate(title="Untitled", description="Ship the V0.1 RELEASE")
        )
        results = service.search_tasks("release")
        assert [found.id for found in results] == [task.id]

    def test_search_no_match(self, service: TaskService) -> None:
        service.create_task(TaskCreate(title="Quarterly Report"))
        assert service.search_tasks("invoice") == []

    def test_results_sorted_by_id(self, service: TaskService) -> None:
        for index in range(5):
            service.create_task(TaskCreate(title=f"Report {index}"))
        results = service.search_tasks("REPORT")
        assert [found.id for found in results] == [1, 2, 3, 4, 5]

    def test_empty_query_matches_all(self, populated_service: TaskService) -> None:
        results = populated_service.search_tasks("")
        assert [found.id for found in results] == [1, 2, 3]


class TestGetOverdueTasks:
    """Tests for TaskService.get_overdue_tasks()."""

    def test_past_due_task_is_overdue(self, service: TaskService) -> None:
        now = datetime.now(UTC)
        task = service.create_task(TaskCreate(title="Late task", due_date=now - timedelta(days=1)))
        assert [found.id for found in service.get_overdue_tasks()] == [task.id]

    def test_future_due_task_is_not_overdue(self, service: TaskService) -> None:
        now = datetime.now(UTC)
        service.create_task(TaskCreate(title="Future task", due_date=now + timedelta(days=1)))
        assert service.get_overdue_tasks() == []

    def test_done_task_is_not_overdue(self, service: TaskService) -> None:
        now = datetime.now(UTC)
        task = service.create_task(
            TaskCreate(title="Late but done", due_date=now - timedelta(days=1))
        )
        service.complete_task(task.id)
        assert service.get_overdue_tasks() == []

    def test_task_without_due_date_is_not_overdue(self, service: TaskService) -> None:
        service.create_task(TaskCreate(title="No due date"))
        assert service.get_overdue_tasks() == []


class TestGetStats:
    """Tests for TaskService.get_stats()."""

    def test_empty_service_has_zero_completion_rate(self, service: TaskService) -> None:
        stats = service.get_stats()
        assert stats.total == 0
        assert stats.completion_rate == 0.0

    def test_populated_completion_rate(self, populated_service: TaskService) -> None:
        populated_service.complete_task(1)
        stats = populated_service.get_stats()
        assert stats.total == 3
        assert stats.by_status[TaskStatus.DONE.value] == 1
        assert stats.completion_rate == pytest.approx(1 / 3, abs=1e-4)

    def test_status_and_priority_breakdown(self, populated_service: TaskService) -> None:
        populated_service.complete_task(1)
        stats = populated_service.get_stats()
        assert stats.by_status == {"todo": 2, "in_progress": 0, "done": 1}
        assert stats.by_priority == {"high": 2, "low": 1}
        assert stats.overdue == 0
