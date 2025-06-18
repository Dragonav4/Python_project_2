from datetime import datetime

from colorama import Fore

RECURRENCE_COLORS = {"daily": Fore.MAGENTA, "weekly": Fore.BLUE, "monthly": Fore.WHITE}
TAG_COLOR = Fore.CYAN

def parse_overdue(date_str: str) -> bool:
    try:
        due = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return False
    return due < datetime.now()