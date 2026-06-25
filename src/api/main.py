"""FastAPI application exposing CRUD endpoints for tasks."""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query, status

from src.models.task import (
    Task,
    TaskCreate,
    TaskStats,
    TaskStatus,
    TaskUpdate,
)
from src.services.task_service import TaskNotFoundError, TaskService

# A single shared in-memory service instance for the running app.
_service = TaskService()


def get_service() -> TaskService:
    """FastAPI dependency that returns the shared task service."""
    return _service


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="Task Manager API",
        description="A small Task Manager API used for Devin demo recordings.",
        version="0.1.0",
    )

    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/tasks", response_model=list[Task], tags=["tasks"])
    def list_tasks(
        status: TaskStatus | None = Query(default=None),
        service: TaskService = Depends(get_service),
    ) -> list[Task]:
        return service.list_tasks(status=status)

    @app.get("/tasks/search", response_model=list[Task], tags=["tasks"])
    def search_tasks(
        q: str = Query(..., min_length=1),
        service: TaskService = Depends(get_service),
    ) -> list[Task]:
        return service.search_tasks(q)

    @app.get("/tasks/overdue", response_model=list[Task], tags=["tasks"])
    def overdue_tasks(
        service: TaskService = Depends(get_service),
    ) -> list[Task]:
        return service.get_overdue_tasks()

    @app.get("/tasks/stats", response_model=TaskStats, tags=["tasks"])
    def stats(
        service: TaskService = Depends(get_service),
    ) -> TaskStats:
        return service.get_stats()

    @app.get("/tasks/{task_id}", response_model=Task, tags=["tasks"])
    def get_task(
        task_id: int,
        service: TaskService = Depends(get_service),
    ) -> Task:
        try:
            return service.get_task(task_id)
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post(
        "/tasks",
        response_model=Task,
        status_code=status.HTTP_201_CREATED,
        tags=["tasks"],
    )
    def create_task(
        payload: TaskCreate,
        service: TaskService = Depends(get_service),
    ) -> Task:
        return service.create_task(payload)

    @app.patch("/tasks/{task_id}", response_model=Task, tags=["tasks"])
    def update_task(
        task_id: int,
        payload: TaskUpdate,
        service: TaskService = Depends(get_service),
    ) -> Task:
        try:
            return service.update_task(task_id, payload)
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/tasks/{task_id}/complete", response_model=Task, tags=["tasks"])
    def complete_task(
        task_id: int,
        service: TaskService = Depends(get_service),
    ) -> Task:
        try:
            return service.complete_task(task_id)
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.delete(
        "/tasks/{task_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=["tasks"],
    )
    def delete_task(
        task_id: int,
        service: TaskService = Depends(get_service),
    ) -> None:
        try:
            service.delete_task(task_id)
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app


app = create_app()
