"""Tests for TaskService.

NOTE FOR DEMOS: this test suite intentionally omits the following test classes
so that they can be written during a Devin demo recording:

  - TestUpdateTask (would catch the updated_at bug)
  - TestSearchTasks (would catch the case-sensitivity bug)
  - TestGetOverdueTasks (would catch the reversed date comparison bug)
  - TestGetStats (would catch the division-by-zero bug)
"""

from __future__ import annotations

import pytest

from src.models.task import TaskCreate, TaskPriority, TaskStatus
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


# ---------------------------------------------------------------------------
# The following test classes are INTENTIONALLY ABSENT. Writing them is a key
# part of the demo workflow.
# ---------------------------------------------------------------------------
# class TestUpdateTask: ...
# class TestSearchTasks: ...
# class TestGetOverdueTasks: ...
# class TestGetStats: ...
