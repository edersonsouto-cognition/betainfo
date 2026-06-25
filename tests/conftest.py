"""Shared test fixtures."""

from __future__ import annotations

import pytest

from src.models.task import TaskCreate, TaskPriority
from src.services.task_service import TaskService


@pytest.fixture()
def service() -> TaskService:
    """Return a fresh TaskService instance."""
    return TaskService()


@pytest.fixture()
def populated_service(service: TaskService) -> TaskService:
    """Return a TaskService pre-loaded with sample tasks."""
    service.create_task(TaskCreate(title="Write unit tests", priority=TaskPriority.HIGH))
    service.create_task(TaskCreate(title="Update README", priority=TaskPriority.LOW))
    service.create_task(
        TaskCreate(
            title="Deploy to production",
            description="Ship the v0.1 release",
            priority=TaskPriority.HIGH,
        )
    )
    return service
