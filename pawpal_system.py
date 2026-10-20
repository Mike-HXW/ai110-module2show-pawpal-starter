from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Optional

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
FREQUENCIES = ("once", "daily", "weekly")


def _to_dt(t: time) -> datetime:
    """Put a time of day on a fixed date so minutes can be added and compared."""
    return datetime.combine(date(2000, 1, 1), t)


def _add_minutes(t: time, minutes: int) -> datetime:
    """Return the datetime that is the given number of minutes after time t."""
    return _to_dt(t) + timedelta(minutes=minutes)


@dataclass
class Task:
    """A single pet care activity with a duration, priority and completion status."""

    id: str
    title: str
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"
    category: str  # e.g. walk, feeding, meds, enrichment, grooming
    preferred_time: Optional[time] = None
    completed: bool = False
    frequency: str = "daily"  # "once" | "daily" | "weekly"
    pet_name: str = ""  # set by Pet.add_task so the plan can say whose task it is

    def __post_init__(self) -> None:
        """Validate the task's fields right after it is created."""
        self._validate()

    def _validate(self) -> None:
        """Raise ValueError if priority, duration or frequency is invalid."""
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}, got {self.priority!r}")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {list(FREQUENCIES)}, got {self.frequency!r}")

    def edit(self, **fields) -> None:
        """Update this task's fields (title, duration_minutes, priority, ...)."""
        allowed = {"title", "duration_minutes", "priority", "category",
                   "preferred_time", "frequency"}
        unknown = set(fields) - allowed
        if unknown:
            raise ValueError(f"cannot edit unknown field(s): {sorted(unknown)}")
        old = {name: getattr(self, name) for name in fields}
        for name, value in fields.items():
            setattr(self, name, value)
        try:
            self._validate()
        except ValueError:
            for name, value in old.items():
                setattr(self, name, value)
            raise

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    """A pet and the care tasks assigned to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet and set task.pet_name. Reject duplicate task ids."""
        if any(t.id == task.id for t in self.tasks):
            raise ValueError(f"{self.name} already has a task with id {task.id!r}")
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id."""
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                del self.tasks[i]
                return
        raise ValueError(f"{self.name} has no task with id {task_id!r}")

    def get_pending_tasks(self) -> list[Task]:
        """Return the tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """A pet owner whose day window and available minutes both limit the plan."""

    name: str
    available_minutes: int
    day_start: time
    day_end: time
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner. Reject duplicate pet names."""
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"{self.name} already has a pet named {pet.name!r}")
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove the pet with the given name."""
        for i, p in enumerate(self.pets):
            if p.name == name:
                del self.pets[i]
                return
        raise ValueError(f"{self.name} has no pet named {name!r}")

    def get_all_tasks(self) -> list[Task]:
        """Return the pending (not completed) tasks of all of this owner's pets."""
        return [t for pet in self.pets for t in pet.get_pending_tasks()]


class Scheduler:
    """Builds a daily plan from all of an owner's pets' tasks."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that plans for the given owner."""
        self.owner = owner

    def build_plan(self) -> tuple[list[dict], list[dict]]:
        """Return (scheduled, skipped) lists of dicts for the owner's day."""
        # scheduled dicts: task, start_time, end_time, reason (in time order).
        # skipped dicts: task, reason.
        # Pass 1 picks tasks by priority until the time budget or day window is
        # full; pass 2 lays them out in time order, honouring preferred_time.
        owner = self.owner
        tasks = self.sort_tasks(owner.get_all_tasks())  # reads across ALL pets

        # Pass 1: choose what fits, highest priority first.
        chosen: list[Task] = []
        skipped: list[dict] = []
        remaining = owner.available_minutes
        used = 0
        for task in tasks:
            cursor = _add_minutes(owner.day_start, used).time()
            if self.fits_in_time(task, remaining, cursor):
                chosen.append(task)
                remaining -= task.duration_minutes
                used += task.duration_minutes
            else:
                skipped.append({"task": task, "reason": "did not fit in the available time"})

        # Pass 2: order chosen tasks by preferred time (unset last), then lay out.
        chosen.sort(key=lambda t: (t.preferred_time is None,
                                   t.preferred_time or time.min,
                                   PRIORITY_RANK[t.priority]))
        day_end = _to_dt(owner.day_end)
        scheduled: list[dict] = []
        cursor_dt = _to_dt(owner.day_start)
        for task in chosen:
            start = cursor_dt
            note = f"scheduled at {start.strftime('%H:%M')}"
            if task.preferred_time is not None:
                preferred = _to_dt(task.preferred_time)
                if preferred >= cursor_dt and preferred + timedelta(minutes=task.duration_minutes) <= day_end:
                    start = preferred
                    note = f"placed at its preferred time {start.strftime('%H:%M')}"
                else:
                    note = (f"preferred time {task.preferred_time.strftime('%H:%M')} "
                            f"not available, {note}")
            end = start + timedelta(minutes=task.duration_minutes)
            if end > day_end:
                skipped.append({"task": task, "reason": "no room left in the day after earlier tasks"})
                continue
            scheduled.append({
                "task": task,
                "start_time": start.time(),
                "end_time": end.time(),
                "reason": f"{self.explain_choice(task)}; {note}",
            })
            cursor_dt = end
        return scheduled, skipped

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (high, medium, low), then preferred time or duration."""
        return sorted(tasks, key=lambda t: (PRIORITY_RANK[t.priority],
                                            t.preferred_time is None,
                                            t.preferred_time or time.min,
                                            t.duration_minutes))

    def fits_in_time(self, task: Task, remaining: int, cursor: time) -> bool:
        """Return True if the task fits the remaining minutes and ends by day_end."""
        if task.duration_minutes > remaining:
            return False
        return _add_minutes(cursor, task.duration_minutes) <= _to_dt(self.owner.day_end)

    def explain_choice(self, task: Task) -> str:
        """Return the reason this task was chosen and placed where it was."""
        who = f" for {task.pet_name}" if task.pet_name else ""
        return f"{task.priority} priority {task.category}{who}"
