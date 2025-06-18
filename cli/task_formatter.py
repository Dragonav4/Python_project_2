from colorama import Style, Fore

from cli.utils import parse_overdue, RECURRENCE_COLORS, TAG_COLOR


class TaskFormatter:
    _PRIORITY_COLOURS = {
        "high": Fore.RED,
        "medium": Fore.YELLOW,
        "low": Fore.CYAN,
    }

    @staticmethod
    def _priority_colour(task) -> str:
        if task.completed:
            return Fore.GREEN

        return TaskFormatter._PRIORITY_COLOURS.get(task.priority, "")
    
    @staticmethod
    def display(tasks) -> None:
        separator = f"{Style.DIM}{'-' * 60}{Style.RESET_ALL}"

        for task in tasks:
            colour = TaskFormatter._priority_colour(task)
            if parse_overdue(task.due_date) and not task.completed:
                colour = Fore.RED

            recurrence_colour = RECURRENCE_COLORS.get(task.recurrence, "")

            print(separator)
            print(f"{Style.BRIGHT}{colour}[{task.id}] {task.description}{Style.RESET_ALL}")
            print(
                f"    {Fore.BLUE}Due: {task.due_date}{Style.RESET_ALL}    "
                f"{Fore.YELLOW}Prio: {task.priority}{Style.RESET_ALL}    "
                f"{recurrence_colour}Recur: {task.recurrence or 'none'}{Style.RESET_ALL}"
            )
            if task.tags:
                print(f"    {TAG_COLOR}Tags:{Style.RESET_ALL} {', '.join(task.tags)}")

            status_colour = Fore.GREEN if task.completed else Fore.RED
            status_text = "done" if task.completed else "pending"
            print(f"    Status: {status_colour}{status_text}{Style.RESET_ALL}")

        print(separator)
