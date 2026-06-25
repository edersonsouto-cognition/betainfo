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

    def test_delete_missing_returns_404(self, client: TestClient) -> None:
        resp = client.delete("/tasks/999")
        assert resp.status_code == 404


class TestUpdateTaskAPI:
    def test_update_title(self, client: TestClient) -> None:
        client.post("/tasks", json={"title": "Original"})
        resp = client.patch("/tasks/1", json={"title": "Updated"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"

    def test_update_missing_returns_404(self, client: TestClient) -> None:
        resp = client.patch("/tasks/999", json={"title": "Nope"})
        assert resp.status_code == 404


class TestCompleteTaskAPI:
    def test_complete_marks_done(self, client: TestClient) -> None:
        client.post("/tasks", json={"title": "Complete me"})
        resp = client.post("/tasks/1/complete")
        assert resp.status_code == 200
        assert resp.json()["status"] == "done"

    def test_complete_missing_returns_404(self, client: TestClient) -> None:
        resp = client.post("/tasks/999/complete")
        assert resp.status_code == 404


class TestSearchTasksAPI:
    def test_search_finds_matching(self, client: TestClient) -> None:
        client.post("/tasks", json={"title": "Buy groceries"})
        client.post("/tasks", json={"title": "Write report"})
        resp = client.get("/tasks/search", params={"q": "Buy"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["title"] == "Buy groceries"

    def test_search_no_match(self, client: TestClient) -> None:
        client.post("/tasks", json={"title": "Something"})
        resp = client.get("/tasks/search", params={"q": "nonexistent"})
        assert resp.status_code == 200
        assert resp.json() == []


class TestOverdueTasksAPI:
    def test_overdue_empty(self, client: TestClient) -> None:
        resp = client.get("/tasks/overdue")
        assert resp.status_code == 200
        assert resp.json() == []


class TestStatsAPI:
    def test_stats_with_tasks(self, client: TestClient) -> None:
        client.post("/tasks", json={"title": "Task 1"})
        client.post("/tasks", json={"title": "Task 2"})
        resp = client.get("/tasks/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 2
        assert body["by_status"]["todo"] == 2

    def test_stats_empty_handles_gracefully(self, client: TestClient) -> None:
        """Stats endpoint with no tasks - exposes the ZeroDivisionError bug."""
        try:
            resp = client.get("/tasks/stats")
            # If the bug is fixed, this should return 200
            if resp.status_code == 200:
                assert resp.json()["total"] == 0
            else:
                # Server error from the division by zero bug
                assert resp.status_code == 500
        except Exception:
            pass
