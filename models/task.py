from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")

@dataclass
class Task:
    id: int
    description: str
    due_date: str
    priority: str
    tags: List[str] = field(default_factory=list)# df to separate and make UNIQUE list 
    recurrence: Optional[str] = None
    completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "tags": self.tags,
            "recurrence": self.recurrence,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(
            id=data["id"],
            description=data["description"],
            due_date=data["due_date"],
            priority=data["priority"],
            tags=data.get("tags", []),
            recurrence=data.get("recurrence"),
            completed=data.get("completed", False),
        )
