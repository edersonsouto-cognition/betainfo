"""Tests for the Pydantic task models."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.models.task import (
    Task,
    TaskCreate,
    TaskPriority,
    TaskStats,
    TaskStatus,
    TaskUpdate,
)


def test_task_status_values() -> None:
    assert TaskStatus.TODO == "todo"
    assert TaskStatus.IN_PROGRESS == "in_progress"
    assert TaskStatus.DONE == "done"


def test_task_priority_values() -> None:
    assert TaskPriority.LOW == "low"
    assert TaskPriority.MEDIUM == "medium"
    assert TaskPriority.HIGH == "high"


class TestTaskCreate:
    """Tests for TaskCreate validation."""

    def test_defaults(self) -> None:
        task = TaskCreate(title="A task")
        assert task.description == ""
        assert task.priority == TaskPriority.MEDIUM
        assert task.due_date is None

    def test_with_all_fields(self) -> None:
        due = datetime(2030, 1, 1, tzinfo=UTC)
        task = TaskCreate(
            title="A task",
            description="A description",
            priority=TaskPriority.HIGH,
            due_date=due,
        )
        assert task.priority == TaskPriority.HIGH
        assert task.due_date == due

    def test_title_required(self) -> None:
        with pytest.raises(ValidationError):
            TaskCreate()

    def test_title_empty(self) -> None:
        with pytest.raises(ValidationError, match="at least 1 character"):
            TaskCreate(title="")

    def test_title_too_long(self) -> None:
        with pytest.raises(ValidationError, match="at most 200 characters"):
            TaskCreate(title="x" * 201)

    def test_description_too_long(self) -> None:
        with pytest.raises(ValidationError, match="at most 2000 characters"):
            TaskCreate(title="Valid", description="x" * 2001)

    def test_invalid_priority(self) -> None:
        with pytest.raises(ValidationError):
            TaskCreate(title="Valid", priority="urgent")


class TestTaskUpdate:
    """Tests for partial update payloads."""

    def test_empty_update_valid(self) -> None:
        update = TaskUpdate()
        assert update.title is None
        assert update.description is None
        assert update.status is None
        assert update.priority is None
        assert update.due_date is None

    def test_partial_update(self) -> None:
        due = datetime(2030, 1, 1, tzinfo=UTC)
        update = TaskUpdate(
            title="New title",
            status=TaskStatus.DONE,
            due_date=due,
        )
        assert update.title == "New title"
        assert update.status == TaskStatus.DONE
        assert update.due_date == due

    def test_empty_title_in_update_raises(self) -> None:
        with pytest.raises(ValidationError, match="at least 1 character"):
            TaskUpdate(title="")

    def test_invalid_status(self) -> None:
        with pytest.raises(ValidationError):
            TaskUpdate(status="blocked")


class TestTask:
    """Tests for the persisted Task model."""

    def test_defaults(self) -> None:
        before = datetime.now(UTC)
        task = Task(id=1, title="A task")
        after = datetime.now(UTC)

        assert task.status == TaskStatus.TODO
        assert task.description == ""
        assert task.priority == TaskPriority.MEDIUM
        assert task.due_date is None
        assert before <= task.created_at <= after
        assert (task.updated_at - task.created_at).total_seconds() < 1

    def test_model_validate_from_dict(self) -> None:
        raw = {
            "id": 42,
            "title": "Hydrated task",
            "description": "Loaded from JSON",
            "status": "in_progress",
            "priority": "high",
            "created_at": "2020-01-01T00:00:00Z",
            "updated_at": "2020-01-02T00:00:00+00:00",
            "due_date": "2025-12-31T23:59:00Z",
        }
        task = Task.model_validate(raw)
        assert task.id == 42
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH
        assert task.created_at == datetime(2020, 1, 1, tzinfo=UTC)
        assert task.updated_at == datetime(2020, 1, 2, tzinfo=UTC)
        assert task.due_date == datetime(2025, 12, 31, 23, 59, tzinfo=UTC)

    def test_model_dump_json_serializes_datetimes(self) -> None:
        created = datetime(2020, 1, 1, tzinfo=UTC)
        task = Task(
            id=1,
            title="A task",
            created_at=created,
            updated_at=created,
        )
        dumped = task.model_dump(mode="json")
        assert dumped["created_at"] == "2020-01-01T00:00:00Z"
        assert dumped["updated_at"] == "2020-01-01T00:00:00Z"

    def test_task_status_default(self) -> None:
        task = Task(id=1, title="Default status")
        assert task.status == TaskStatus.TODO


class TestTaskStats:
    """Tests for aggregate statistics model."""

    def test_fields(self) -> None:
        stats = TaskStats(
            total=3,
            by_status={"todo": 2, "done": 1},
            by_priority={"high": 3},
            completion_rate=0.3333,
            overdue=1,
        )
        assert stats.total == 3
        assert stats.by_status["done"] == 1
        assert stats.by_priority["high"] == 3
        assert stats.completion_rate == 0.3333
        assert stats.overdue == 1
