"""In-memory task service.

NOTE FOR DEMOS: this module intentionally contains four bugs that are used in
Devin demo recordings. Each one is flagged with a ``# BUG:`` comment describing
the intended (correct) behaviour. The accompanying test suite intentionally
omits the tests that would catch them.

    1. search_tasks()      -> should be case-insensitive
    2. update_task()       -> should refresh updated_at
    3. get_overdue_tasks() -> date comparison is reversed
    4. get_stats()         -> divides by zero when there are no tasks
"""

from __future__ import annotations

from datetime import UTC, datetime

from src.models.task import (
    Task,
    TaskCreate,
    TaskStats,
    TaskStatus,
    TaskUpdate,
)


def _utcnow() -> datetime:
    return datetime.now(UTC)


class TaskNotFoundError(Exception):
    """Raised when a task with the given id does not exist."""

    def __init__(self, task_id: int) -> None:
        super().__init__(f"Task {task_id} not found")
        self.task_id = task_id


class TaskService:
    """A simple in-memory CRUD store for tasks."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    # ------------------------------------------------------------------
    # Basic CRUD
    # ------------------------------------------------------------------
    def create_task(self, payload: TaskCreate) -> Task:
        """Create and store a new task."""
        now = _utcnow()
        task = Task(
            id=self._next_id,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            due_date=payload.due_date,
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id: int) -> Task:
        """Return a single task or raise ``TaskNotFoundError``."""
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def list_tasks(
        self,
        status: TaskStatus | None = None,
    ) -> list[Task]:
        """Return all tasks, optionally filtered by status."""
        tasks = list(self._tasks.values())
        if status is not None:
            tasks = [task for task in tasks if task.status == status]
        return sorted(tasks, key=lambda task: task.id)

    def update_task(self, task_id: int, payload: TaskUpdate) -> Task:
        """Apply a partial update to an existing task."""
        task = self.get_task(task_id)
        data = payload.model_dump(exclude_unset=True)
        updated = task.model_copy(update=data)
        # BUG: updated_at should be refreshed to the current time whenever a
        # task changes, but it is left untouched here.
        self._tasks[task_id] = updated
        return updated

    def delete_task(self, task_id: int) -> None:
        """Delete a task or raise ``TaskNotFoundError``."""
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]

    def complete_task(self, task_id: int) -> Task:
        """Mark a task as done."""
        return update_status(self, task_id, TaskStatus.DONE)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def search_tasks(self, query: str) -> list[Task]:
        """Search tasks whose title or description contains ``query``."""
        results = []
        for task in self._tasks.values():
            # BUG: this comparison is case-sensitive. Searching for "report"
            # should match a task titled "Quarterly Report", but it does not.
            if query in task.title or query in task.description:
                results.append(task)
        return sorted(results, key=lambda task: task.id)

    def get_overdue_tasks(self) -> list[Task]:
        """Return tasks that are past their due date and not yet done."""
        now = _utcnow()
        overdue = []
        for task in self._tasks.values():
            if task.due_date is None or task.status == TaskStatus.DONE:
                continue
            # BUG: the comparison is reversed. A task is overdue when its
            # due_date is in the past (due_date < now), not the future.
            if task.due_date > now:
                overdue.append(task)
        return sorted(overdue, key=lambda task: task.id)

    def get_stats(self) -> TaskStats:
        """Compute aggregate statistics across all tasks."""
        tasks = list(self._tasks.values())
        total = len(tasks)

        by_status: dict[str, int] = {status.value: 0 for status in TaskStatus}
        by_priority: dict[str, int] = {}
        for task in tasks:
            by_status[task.status.value] += 1
            by_priority[task.priority.value] = by_priority.get(task.priority.value, 0) + 1

        done = by_status[TaskStatus.DONE.value]
        # BUG: dividing by ``total`` raises ZeroDivisionError when there are no
        # tasks. The completion rate should be 0.0 for an empty task list.
        completion_rate = done / total

        return TaskStats(
            total=total,
            by_status=by_status,
            by_priority=by_priority,
            completion_rate=round(completion_rate, 4),
            overdue=len(self.get_overdue_tasks()),
        )


def update_status(service: TaskService, task_id: int, status: TaskStatus) -> Task:
    """Helper that updates only the status field of a task."""
    return service.update_task(task_id, TaskUpdate(status=status))
