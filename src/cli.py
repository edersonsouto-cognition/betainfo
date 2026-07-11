"""Command-line interface for the task manager (Typer + Rich)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from src.models.task import Task, TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from src.services.task_service import TaskNotFoundError, TaskService

app = typer.Typer(name="taskman", help="A simple task manager CLI.")
console = Console()

DATA_FILE = Path("data/cli_tasks.json")
SEED_FILE = Path("data/sample_tasks.json")
_service: TaskService | None = None


def _get_service() -> TaskService:
    """Lazy-load the shared TaskService, hydrating from disk.

    Runtime state lives in ``DATA_FILE`` (gitignored). On first run, when it
    does not exist yet, seed the store from ``SEED_FILE`` so the demo starts
    with sample data; subsequent writes persist to ``DATA_FILE``.
    """
    global _service  # noqa: PLW0603
    if _service is not None:
        return _service
    _service = TaskService()
    source = DATA_FILE if DATA_FILE.exists() else SEED_FILE
    if source.exists():
        raw = json.loads(source.read_text())
        for item in raw:
            task = Task.model_validate(item)
            _service._tasks[task.id] = task
            if task.id >= _service._next_id:
                _service._next_id = task.id + 1
    return _service


def _persist() -> None:
    """Write the service's tasks to disk."""
    service = _get_service()
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = [task.model_dump(mode="json") for task in service._tasks.values()]
    DATA_FILE.write_text(json.dumps(data, indent=2, default=str))


@app.command()
def add(
    title: str,
    description: str = "",
    priority: Annotated[TaskPriority, typer.Option("--priority", "-p")] = TaskPriority.MEDIUM,
    due: Annotated[str | None, typer.Option("--due", "-d")] = None,
) -> None:
    """Add a new task."""
    due_date = None
    if due:
        due_date = datetime.fromisoformat(due).replace(tzinfo=UTC)
    service = _get_service()
    payload = TaskCreate(title=title, description=description, priority=priority, due_date=due_date)
    task = service.create_task(payload)
    _persist()
    console.print(f"[green]Created task #{task.id}:[/green] {task.title}")


@app.command("list")
def list_tasks(
    status: Annotated[TaskStatus | None, typer.Option("--status", "-s")] = None,
) -> None:
    """List all tasks (optionally filtered by status)."""
    service = _get_service()
    tasks = service.list_tasks(status=status)
    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    table = Table(title="Tasks")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Title")
    table.add_column("Status", style="magenta")
    table.add_column("Priority")
    table.add_column("Due")

    for task in tasks:
        due_str = task.due_date.strftime("%Y-%m-%d") if task.due_date else "—"
        table.add_row(
            str(task.id),
            task.title,
            task.status.value,
            task.priority.value,
            due_str,
        )
    console.print(table)


@app.command()
def done(
    task_id: int,
) -> None:
    """Mark a task as done."""
    service = _get_service()
    try:
        task = service.update_task(task_id, TaskUpdate(status=TaskStatus.DONE))
        _persist()
        console.print(f"[green]Task #{task.id} marked as done.[/green]")
    except TaskNotFoundError:
        console.print(f"[red]Task #{task_id} not found.[/red]")
        raise typer.Exit(code=1) from None


@app.command()
def stats() -> None:
    """Show task statistics."""
    service = _get_service()
    tasks = service.list_tasks()
    if not tasks:
        console.print("[yellow]No tasks to compute stats from.[/yellow]")
        return
    s = service.get_stats()
    table = Table(title="Task Statistics")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    table.add_row("Total tasks", str(s.total))
    table.add_row("Completion rate", f"{s.completion_rate:.1%}")
    table.add_row("Overdue", str(s.overdue))
    for st, count in s.by_status.items():
        table.add_row(f"  status: {st}", str(count))
    for pr, count in s.by_priority.items():
        table.add_row(f"  priority: {pr}", str(count))
    console.print(table)


if __name__ == "__main__":
    app()
