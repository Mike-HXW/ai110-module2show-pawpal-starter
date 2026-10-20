from dataclasses import dataclass, field
from datetime import time
from typing import Optional


@dataclass
class Task:
    id: str
    title: str
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"
    category: str  # e.g. walk, feeding, meds, enrichment, grooming
    preferred_time: Optional[time] = None
    completed: bool = False

    def edit(self, **fields) -> None:
        """Update this task's fields (title, duration_minutes, priority, ...)."""
        pass

    def mark_done(self) -> None:
        """Mark this task as completed."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        pass

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id."""
        pass

    def get_pending_tasks(self) -> list[Task]:
        """Return the tasks that are not yet completed."""
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    day_start: time
    day_end: time
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        pass

    def remove_pet(self, name: str) -> None:
        """Remove the pet with the given name."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return the tasks of all of this owner's pets."""
        pass


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def build_plan(self) -> list[dict]:
        """Build the daily plan as a list of dicts (task, start_time, end_time, reason)."""
        pass

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (then duration or preferred time)."""
        pass

    def fits_in_time(self, task: Task, remaining: int) -> bool:
        """Return True if the task fits in the remaining minutes."""
        pass

    def explain_choice(self, task: Task) -> str:
        """Return the reason this task was chosen and placed where it was."""
        pass
