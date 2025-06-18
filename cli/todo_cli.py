from datetime import datetime
from pathlib import Path
from typing import Optional

from colorama import init, Fore, Style

from cli.task_formatter import TaskFormatter
from services.todolist import ToDoList
from exceptions.invalid_date_error import InvalidDateError
from exceptions.task_not_found_error import TaskNotFoundError


class TodoCLI:
    def __init__(self, data_path="data/tasks.json", sync=True):
        init(autoreset=True)
        self.todo = ToDoList(Path(data_path), sync=sync)

    @staticmethod
    def prompt_date(prompt: str) -> Optional[str]:
        date_str = input(prompt).strip()
        return date_str if date_str else None

    def handle_add(self):
        description = input("Description: ")
        raw_due = input("Due date (YYYY-MM-DD or DD): ").strip()
        if raw_due.isdigit() and 1 <= int(raw_due) <= 31:
            today = datetime.now()
            due_date = f"{today.year}-{today.month:02d}-{int(raw_due):02d}"
        else:
            due_date = raw_due
        priority = input("Priority (low/medium/high): ")
        tags_input = input("Tags (comma separated, Enter to skip): ").strip()
        tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []
        recurrence = input("Recurrence (none/daily/weekly/monthly): ").strip().lower() or None
        try:
            self.todo.add_task(description, due_date, priority, tags, recurrence)
            print("Task added.")
        except (InvalidDateError, ValueError) as e:
            print(Fore.RED + f"Error: {e}")

    def handle_list(self):
        prio = input("Filter by priority (press Enter to skip): ").strip() or None
        before = self.prompt_date("Due before (YYYY-MM-DD, Enter to skip): ")
        after = self.prompt_date("Due after (YYYY-MM-DD, Enter to skip): ")
        tasks = self.todo.list_tasks(prio, before, after)
        TaskFormatter.display(tasks)

    def handle_complete(self):
        try:
            task_id = int(input("Task ID to complete: "))
            self.todo.complete_task(task_id)
            print("Task marked as completed.")
        except (ValueError, TaskNotFoundError) as e:
            print(Fore.RED + f"Error: {e}")

    def handle_delete(self):
        try:
            task_id = int(input("Task ID to delete: "))
            self.todo.delete_task(task_id)
            print("Task deleted.")
        except (ValueError, TaskNotFoundError) as e:
            print(Fore.RED + f"Error: {e}")

    def handle_search(self):
        keyword = input("Enter keyword or tag to search: ").strip()
        if not keyword:
            return
        tasks = self.todo.list_tasks(search_keywords=keyword, filter_tag=keyword)
        TaskFormatter.display(tasks)

    def run(self):
        upcoming = self.todo.tasks_due_within(24)
        if upcoming:
            print(Fore.RED + "Warning! You have tasks due within 24 hours!")
            for task in upcoming:
                print(f"[{task.id}] {task.description} due {task.due_date}")

        menu = (
            "\nTo-Do List Menu:\n"
            "1. Add task\n"
            "2. List tasks\n"
            "3. Complete task\n"
            "4. Delete task\n"
            "5. Search tasks\n"
            "6. Exit\n"
        )
        handlers = {
            "1": self.handle_add,
            "2": self.handle_list,
            "3": self.handle_complete,
            "4": self.handle_delete,
            "5": self.handle_search,
        }
        while True:
            print(Style.BRIGHT + Fore.CYAN + menu + Style.RESET_ALL)
            choice = input("Choose an option: ").strip()
            if choice == "6":
                break
            handler = handlers.get(choice)
            if handler:
                handler()
            else:
                print(Fore.RED + "Invalid choice. Please try again.")
