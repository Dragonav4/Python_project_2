import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from google_drive_sync.drive_sync import DriveSync
from models.task import Task, parse_date
from exceptions.invalid_date_error import InvalidDateError
from exceptions.task_not_found_error import TaskNotFoundError


class ToDoList:

    ALLOWED_PRIORITIES = {"low", "medium", "high"}
    ALLOWED_RECURRENCES = {None, "daily", "weekly", "monthly"}

    def __init__(self,file_path: Path, sync: bool = True):
        self.file_path = file_path
        self.syncer = DriveSync(local_path=str(file_path)) if sync else None
        if self.syncer:
            self.syncer.download_file()
        self.tasks: List[Task] = []
        self._load_tasks()

    def _ensure_file_exists(self) -> None:
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f) # json

    def _load_tasks(self) -> None:
        self._ensure_file_exists()
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.tasks = [Task.from_dict(item) for item in data] #from dict to task

    def _save_tasks(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=2,ensure_ascii=False)
        if self.syncer:
            self.syncer.upload_file()

    def _next_id(self) -> int:
        return max((task.id for task in self.tasks), default=0) + 1

    def add_task(
        self,
        description: str,
        due_date: str,
        priority: str,
        tags: Optional[List[str]] = None,
        recurrence: Optional[str] = None,
    ) -> Task:
        try:
            due = parse_date(due_date)
        except ValueError as exc:
            raise InvalidDateError("Date must be in YYYY-MM-DD format") from exc
        if due < datetime.now():
            raise InvalidDateError("Due date cannot be in the past")
        if priority.lower() not in self.ALLOWED_PRIORITIES:
            raise ValueError(f"Priority must be one of {self.ALLOWED_PRIORITIES}")
        if recurrence not in self.ALLOWED_RECURRENCES:
            raise ValueError("Recurrence must be daily, weekly, monthly or None")
        if tags is None:
            tags = []
        task = Task(
            id=self._next_id(),
            description=description,
            due_date=due_date,
            priority=priority.lower(),
            tags=tags,
            recurrence=recurrence,
            completed=False,
        )
        self.tasks.append(task)
        self._save_tasks()
        return task

    def list_tasks(
        self,
        filter_priority: Optional[str] = None,
        due_before: Optional[str] = None,
        due_after: Optional[str] = None,
        search_keywords: Optional[str] = None,
        filter_tag: Optional[str] = None,
    ) -> List[Task]:
        result = self.tasks
        if filter_priority:
            result = self._filter_by_priority(result, filter_priority)
        if due_before:
            result = self._filter_by_due_before(result, due_before)
        if due_after:
            result = self._filter_by_due_after(result, due_after)
        if filter_tag:
            result = self._filter_by_tag(result, filter_tag)
        if search_keywords:
            result = self._filter_by_keywords(result, search_keywords)
        return result

    def _filter_by_priority(self, tasks: List[Task], priority: str) -> List[Task]:
        return [t for t in tasks if t.priority == priority.lower()]

    def _filter_by_due_before(self, tasks: List[Task], due_before: str) -> List[Task]:
        before = parse_date(due_before)
        return [t for t in tasks if parse_date(t.due_date) <= before]

    def _filter_by_due_after(self, tasks: List[Task], due_after: str) -> List[Task]:
        after = parse_date(due_after)
        return [t for t in tasks if parse_date(t.due_date) >= after]

    def _filter_by_tag(self, tasks: List[Task], tag: str) -> List[Task]:
        return [t for t in tasks if any(tag.lower() == tg.lower() for tg in t.tags)]

    def _filter_by_keywords(self, tasks: List[Task], keywords: str) -> List[Task]:
        kw = keywords.lower()
        return [t for t in tasks if kw in t.description.lower() or any(kw in tag.lower() for tag in t.tags)]

    def get_task(self, task_id: int) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"Task with id {task_id} not found")

    def complete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        task.completed = True
        if task.recurrence:
            due = parse_date(task.due_date)
            if task.recurrence == "daily":
                due += timedelta(days=1)
            elif task.recurrence == "weekly":
                due += timedelta(weeks=1)
            elif task.recurrence == "monthly":
                due += timedelta(days=30)
            task.due_date = due.strftime("%Y-%m-%d")
            task.completed = False
        self._save_tasks()

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        self.tasks.remove(task)
        self._save_tasks()

    def tasks_due_within(self, hours: int) -> List[Task]:
        upcoming = datetime.now() + timedelta(hours=hours)
        return [t for t in self.tasks if parse_date(t.due_date) <= upcoming and not t.completed]
