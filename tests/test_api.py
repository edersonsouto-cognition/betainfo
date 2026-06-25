"""Basic tests for the FastAPI endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app, get_service
from src.services.task_service import TaskService


@pytest.fixture()
def client() -> TestClient:
    """Return a TestClient wired to a fresh TaskService."""
    app = create_app()
    fresh_service = TaskService()
    app.dependency_overrides[get_service] = lambda: fresh_service
    return TestClient(app)


class TestHealth:
    def test_health(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestCreateTaskAPI:
    def test_create_task(self, client: TestClient) -> None:
        resp = client.post("/tasks", json={"title": "Learn FastAPI"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["id"] == 1
        assert body["title"] == "Learn FastAPI"
        assert body["status"] == "todo"

    def test_create_task_validation(self, client: TestClient) -> None:
        resp = client.post("/tasks", json={"title": ""})
        assert resp.status_code == 422


class TestListTasksAPI:
    def test_list_empty(self, client: TestClient) -> None:
        resp = client.get("/tasks")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_after_create(self, client: TestClient) -> None:
        client.post("/tasks", json={"title": "Task 1"})
        client.post("/tasks", json={"title": "Task 2"})
        resp = client.get("/tasks")
        assert len(resp.json()) == 2


class TestGetTaskAPI:
    def test_get_existing(self, client: TestClient) -> None:
        client.post("/tasks", json={"title": "Existing"})
        resp = client.get("/tasks/1")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Existing"

    def test_get_missing_returns_404(self, client: TestClient) -> None:
        resp = client.get("/tasks/999")
        assert resp.status_code == 404


class TestDeleteTaskAPI:
    def test_delete_returns_204(self, client: TestClient) -> None:
        client.post("/tasks", json={"title": "Delete me"})
        resp = client.delete("/tasks/1")
        assert resp.status_code == 204
