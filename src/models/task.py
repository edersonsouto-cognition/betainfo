"""Pydantic v2 models for the Task Manager API."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


def _utcnow() -> datetime:
    return datetime.now(UTC)


class TaskStatus(StrEnum):
    """Lifecycle status of a task."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(StrEnum):
    """Relative importance of a task."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskBase(BaseModel):
    """Fields shared between create/update/read models."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    """Payload for creating a task."""


class TaskUpdate(BaseModel):
    """Payload for partially updating a task. All fields optional."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    due_date: datetime | None = None


class Task(TaskBase):
    """A persisted task."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: TaskStatus = TaskStatus.TODO
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class TaskStats(BaseModel):
    """Aggregate statistics across all tasks."""

    total: int
    by_status: dict[str, int]
    by_priority: dict[str, int]
    completion_rate: float
    overdue: int
