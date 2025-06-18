import pytest
from datetime import datetime, timedelta
from pathlib import Path

from services.todolist import ToDoList
from exceptions.invalid_date_error import InvalidDateError
from exceptions.task_not_found_error import TaskNotFoundError


@pytest.fixture
def todo(tmp_path):
    data_file = tmp_path / "tasks.json"
    return ToDoList(Path(data_file))


def _tomorrow():
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


def test_add_task_valid(todo):
    task = todo.add_task(
        description="unit test",
        due_date=_tomorrow(),
        priority="high",
        tags=["testing"],
        recurrence=None,
    )
    assert task.id == 1
    assert task.description == "unit test"
    assert task.priority == "high"
    assert task.recurrence is None
    assert len(todo.tasks) == 1
    assert todo.file_path.exists()
    assert todo.get_task(task.id) == task


def test_add_task_invalid_date(todo):
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    with pytest.raises(InvalidDateError):
        todo.add_task("Past task", yesterday, "low")


def test_list_tasks_filters(todo):
    now = datetime.now()
    task_home = todo.add_task(
        "Clean kitchen", (now + timedelta(days=2)).strftime("%Y-%m-%d"), "low", tags=["home"]
    )
    task_work = todo.add_task(
        "Prepare python project", (now + timedelta(days=3)).strftime("%Y-%m-%d"), "high", tags=["work"]
    )

    high_tasks = todo.list_tasks(filter_priority="high")
    assert [t.id for t in high_tasks] == [task_work.id]

    home_tasks = todo.list_tasks(filter_tag="home")
    assert [t.id for t in home_tasks] == [task_home.id]

    keyword_tasks = todo.list_tasks(search_keywords="project")
    assert [t.id for t in keyword_tasks] == [task_work.id]


def test_complete_task_recurring(todo):
    tomorrow = _tomorrow()
    task = todo.add_task("Daily exercise", tomorrow, "medium", recurrence="daily")
    todo.complete_task(task.id)

    rescheduled = todo.get_task(task.id)
    assert rescheduled.completed is False

    expected_due = (
        datetime.strptime(tomorrow, "%Y-%m-%d") + timedelta(days=1)
    ).strftime("%Y-%m-%d")
    assert rescheduled.due_date == expected_due


def test_delete_task(todo):
    task = todo.add_task("Delete me", _tomorrow(), "low")
    todo.delete_task(task.id)
    with pytest.raises(TaskNotFoundError):
        todo.get_task(task.id)
    assert len(todo.tasks) == 0


def test_tasks_due_within(todo):
    soon = (datetime.now() + timedelta(hours=12)).strftime("%Y-%m-%d")
    later = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

    task_soon = todo.add_task("Soon due", soon, "low")
    todo.add_task("Later due", later, "low")

    due_soon = todo.tasks_due_within(24)
    assert len(due_soon) == 1
    assert due_soon[0].id == task_soon.id
