"""Tests for TaskService."""

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

    def test_partial_update_applies_fields(self, populated_service: TaskService) -> None:
        task = populated_service.update_task(1, TaskUpdate(title="Renamed"))
        assert task.title == "Renamed"
        assert task.priority == TaskPriority.HIGH
        assert populated_service.get_task(1).title == "Renamed"

    def test_update_refreshes_updated_at(self, populated_service: TaskService) -> None:
        created = populated_service.get_task(1)
        updated = populated_service.update_task(1, TaskUpdate(status=TaskStatus.IN_PROGRESS))
        assert updated.created_at == created.created_at
        assert updated.updated_at > created.created_at

    def test_update_missing_raises(self, service: TaskService) -> None:
        with pytest.raises(TaskNotFoundError):
            service.update_task(42, TaskUpdate(title="Nope"))


class TestSearchTasks:
    """Tests for TaskService.search_tasks()."""

    def test_search_is_case_insensitive(self, service: TaskService) -> None:
        service.create_task(TaskCreate(title="Quarterly Report"))
        service.create_task(TaskCreate(title="Standup", description="Discuss the REPORT"))
        service.create_task(TaskCreate(title="Unrelated"))
        results = service.search_tasks("report")
        assert [task.id for task in results] == [1, 2]

    def test_results_sorted_by_id(self, service: TaskService) -> None:
        for index in range(5):
            service.create_task(TaskCreate(title=f"Report {index}"))
        results = service.search_tasks("REPORT")
        assert [task.id for task in results] == [1, 2, 3, 4, 5]

    def test_empty_query_matches_all(self, populated_service: TaskService) -> None:
        results = populated_service.search_tasks("")
        assert [task.id for task in results] == [1, 2, 3]

    def test_no_match_returns_empty(self, populated_service: TaskService) -> None:
        assert populated_service.search_tasks("nonexistent") == []


class TestGetOverdueTasks:
    """Tests for TaskService.get_overdue_tasks()."""

    def test_past_due_task_is_overdue(self, service: TaskService) -> None:
        past = datetime.now(UTC) - timedelta(days=1)
        service.create_task(TaskCreate(title="Late", due_date=past))
        assert [task.id for task in service.get_overdue_tasks()] == [1]

    def test_future_due_task_is_not_overdue(self, service: TaskService) -> None:
        future = datetime.now(UTC) + timedelta(days=1)
        service.create_task(TaskCreate(title="Upcoming", due_date=future))
        assert service.get_overdue_tasks() == []

    def test_done_and_undated_tasks_excluded(self, service: TaskService) -> None:
        past = datetime.now(UTC) - timedelta(days=1)
        service.create_task(TaskCreate(title="Late but done", due_date=past))
        service.complete_task(1)
        service.create_task(TaskCreate(title="No due date"))
        service.create_task(TaskCreate(title="Late", due_date=past))
        assert [task.id for task in service.get_overdue_tasks()] == [3]


class TestGetStats:
    """Tests for TaskService.get_stats()."""

    def test_empty_service_has_zero_completion_rate(self, service: TaskService) -> None:
        stats = service.get_stats()
        assert stats.total == 0
        assert stats.completion_rate == 0.0
        assert stats.overdue == 0

    def test_populated_stats(self, populated_service: TaskService) -> None:
        populated_service.complete_task(1)
        stats = populated_service.get_stats()
        assert stats.total == 3
        assert stats.by_status == {"todo": 2, "in_progress": 0, "done": 1}
        assert stats.by_priority == {"high": 2, "low": 1}
        assert stats.completion_rate == round(1 / 3, 4)
