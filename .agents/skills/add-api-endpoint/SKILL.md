---
name: add-api-endpoint
description: Add a new FastAPI route to the Task Manager API following this repo's conventions. Use whenever adding or changing an endpoint in src/api/main.py.
---

## Steps

1. Add the route inside `create_app()` in `src/api/main.py`. All routes live in the app factory; do not create a new module or `APIRouter` unless the task asks for it.
2. Get the service through dependency injection: `service: TaskService = Depends(get_service)`. Never instantiate `TaskService()` inside a handler.
3. Define request/response shapes as Pydantic v2 models in `src/models/task.py` and set `response_model=` on the route. Do not return raw dicts.
4. Put business logic in `TaskService` (`src/services/task_service.py`), not in the handler. The CLI shares that service, so logic added there works for both interfaces.
5. Register static paths (e.g. `/tasks/search`, `/tasks/stats`) *before* `/tasks/{task_id}`, otherwise the path parameter route shadows them.
6. Raise `HTTPException(status_code=404, detail=...)` for missing tasks; use `status_code=201` for creates and `204` for deletes, matching the existing routes.
7. Add tests to `tests/test_api.py` using the existing `TestClient` pattern: one happy path and one failure path (404 or validation error).
8. Update the endpoint table in the `build-and-run` skill.
9. Run the `pre-pr-check` skill before opening the PR.
