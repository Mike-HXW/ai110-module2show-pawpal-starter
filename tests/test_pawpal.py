import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, time, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def make_task(task_id: str = "1") -> Task:
    return Task(task_id, "Morning walk", 30, "high", "walk")


def test_mark_complete_changes_task_status():
    task = make_task()
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(make_task("1"))
    assert len(pet.tasks) == 1

    pet.add_task(make_task("2"))
    assert len(pet.tasks) == 2


def make_owner() -> Owner:
    owner = Owner("Jordan", 120, time(7, 0), time(21, 0))
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("1", "Late", 20, "low", "grooming", preferred_time=time(19, 0)))
    mochi.add_task(Task("2", "Untimed", 10, "low", "admin"))
    luna.add_task(Task("3", "Early", 30, "high", "walk", preferred_time=time(7, 30)))
    return owner


def test_sort_by_time_puts_untimed_last():
    owner = make_owner()
    titles = [t.title for t in Scheduler(owner).sort_by_time(owner.filter_tasks())]
    assert titles == ["Early", "Late", "Untimed"]


def test_filter_by_pet_status_and_unknown():
    owner = make_owner()
    owner.pets[0].tasks[0].completed = True
    assert [t.id for t in owner.filter_tasks(pet_name="Luna")] == ["3"]
    assert [t.id for t in owner.filter_tasks(completed=True)] == ["1"]
    assert [t.id for t in owner.filter_tasks(pet_name="Mochi", completed=False)] == ["2"]
    assert owner.filter_tasks(pet_name="Rex") == []


def test_daily_and_weekly_completion_create_next_task():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("1", "Walk", 30, "high", "walk", frequency="daily"))
    pet.add_task(Task("2", "Bath", 30, "low", "grooming", frequency="weekly"))
    daily, weekly = pet.complete_task("1"), pet.complete_task("2")
    assert daily.due_date == date.today() + timedelta(days=1)
    assert weekly.due_date == date.today() + timedelta(days=7)
    assert not daily.completed and len(pet.tasks) == 4


def test_once_task_does_not_recur():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("1", "Vet", 30, "high", "meds", frequency="once"))
    assert pet.complete_task("1") is None
    assert len(pet.tasks) == 1


def test_future_dated_task_excluded_from_todays_tasks():
    owner = make_owner()
    owner.pets[0].complete_task("1")
    assert all(t.due_date is None for t in owner.get_all_tasks())


def test_overlap_warns_but_back_to_back_does_not():
    owner = make_owner()
    scheduler = Scheduler(owner)
    owner.pets[1].add_task(Task("4", "Overlap", 20, "low", "play", preferred_time=time(7, 45)))
    assert len(scheduler.detect_conflicts(owner.get_all_tasks())) == 1
    owner.pets[1].remove_task("4")
    owner.pets[1].add_task(Task("5", "Adjacent", 20, "low", "play", preferred_time=time(8, 0)))
    assert scheduler.detect_conflicts(owner.get_all_tasks()) == []


# --- Sorting correctness -----------------------------------------------------

def test_sort_by_time_is_chronological_and_leaves_input_unchanged():
    tasks = [
        Task("a", "C", 10, "low", "x", preferred_time=time(18, 0)),
        Task("b", "A", 10, "low", "x", preferred_time=time(6, 0)),
        Task("c", "B", 10, "low", "x", preferred_time=time(12, 30)),
    ]
    original = list(tasks)
    result = Scheduler(Owner("J", 60, time(6), time(20))).sort_by_time(tasks)
    assert [t.title for t in result] == ["A", "B", "C"]
    assert tasks == original


def test_sort_by_time_handles_empty_list_and_midnight():
    scheduler = Scheduler(Owner("J", 60, time(6), time(20)))
    assert scheduler.sort_by_time([]) == []
    midnight = Task("m", "Midnight", 5, "low", "x", preferred_time=time(0, 0))
    morning = Task("n", "Morning", 5, "low", "x", preferred_time=time(8, 0))
    assert scheduler.sort_by_time([morning, midnight]) == [midnight, morning]


def test_sort_by_time_keeps_input_order_for_equal_times():
    first = Task("a", "First", 10, "low", "x", preferred_time=time(9, 0))
    second = Task("b", "Second", 10, "low", "x", preferred_time=time(9, 0))
    result = Scheduler(Owner("J", 60, time(6), time(20))).sort_by_time([first, second])
    assert result == [first, second]


# --- Recurrence logic --------------------------------------------------------

def test_completing_daily_task_creates_pending_copy_for_tomorrow():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("1", "Walk", 30, "high", "walk", frequency="daily"))
    follow_up = pet.complete_task("1")
    tomorrow = date.today() + timedelta(days=1)
    assert pet.tasks[0].completed is True
    assert follow_up is not None and follow_up in pet.tasks
    assert follow_up.due_date == tomorrow
    assert follow_up.completed is False
    assert follow_up.id == f"1-{tomorrow.isoformat()}"
    assert follow_up.pet_name == "Mochi"


def test_recurrence_counts_from_due_date_across_month_end():
    task = Task("1", "Walk", 30, "high", "walk", frequency="daily", due_date=date(2026, 12, 31))
    assert task.mark_complete().due_date == date(2027, 1, 1)


def test_complete_task_with_unknown_id_raises():
    with pytest.raises(ValueError):
        Pet("Mochi", "dog").complete_task("nope")


# --- Conflict detection ------------------------------------------------------

def test_same_start_time_same_pet_is_flagged():
    owner = Owner("J", 120, time(7), time(21))
    mochi = Pet("Mochi", "dog")
    owner.add_pet(mochi)
    mochi.add_task(Task("1", "Training", 15, "medium", "x", preferred_time=time(12, 0)))
    mochi.add_task(Task("2", "Lunch", 10, "high", "x", preferred_time=time(12, 0)))
    warnings = Scheduler(owner).detect_conflicts(owner.get_all_tasks())
    assert len(warnings) == 1
    assert "Training" in warnings[0] and "Lunch" in warnings[0]


def test_same_start_time_different_pets_is_flagged():
    owner = Owner("J", 120, time(7), time(21))
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("1", "Walk", 30, "high", "x", preferred_time=time(8, 0)))
    luna.add_task(Task("2", "Feed", 10, "high", "x", preferred_time=time(8, 0)))
    scheduler = Scheduler(owner)
    scheduler.build_plan()
    assert len(scheduler.warnings) == 1
    assert "Mochi" in scheduler.warnings[0] and "Luna" in scheduler.warnings[0]


def test_untimed_tasks_never_conflict():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("1", "A", 10, "low", "x"))
    pet.add_task(Task("2", "B", 10, "low", "x"))
    assert Scheduler(Owner("J", 60, time(7), time(21))).detect_conflicts(pet.tasks) == []


# --- Empty / boundary data ---------------------------------------------------

def test_pet_with_no_tasks_and_owner_with_no_pets_give_empty_plan():
    owner = Owner("J", 60, time(7), time(21))
    assert Scheduler(owner).build_plan() == ([], [])
    owner.add_pet(Pet("Mochi", "dog"))
    assert owner.get_all_tasks() == []
    assert Scheduler(owner).build_plan() == ([], [])


def test_task_longer_than_available_time_is_skipped():
    owner = Owner("J", 30, time(7), time(21))
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("1", "Long", 45, "high", "x"))
    scheduled, skipped = Scheduler(owner).build_plan()
    assert scheduled == [] and [s["task"].id for s in skipped] == ["1"]


def test_task_exactly_filling_budget_and_day_end_is_scheduled():
    owner = Owner("J", 60, time(7), time(8))
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("1", "Hour", 60, "high", "x"))
    scheduled, skipped = Scheduler(owner).build_plan()
    assert skipped == []
    assert scheduled[0]["start_time"] == time(7) and scheduled[0]["end_time"] == time(8)


def test_plan_places_tasks_at_preferred_times_in_order():
    owner = make_owner()
    scheduled, skipped = Scheduler(owner).build_plan()
    starts = [item["start_time"] for item in scheduled]
    assert starts == sorted(starts)
    assert scheduled[0]["task"].title == "Early" and starts[0] == time(7, 30)


def test_invalid_task_fields_raise_and_failed_edit_rolls_back():
    with pytest.raises(ValueError):
        Task("1", "Bad", 0, "high", "x")
    with pytest.raises(ValueError):
        Task("1", "Bad", 10, "urgent", "x")
    task = make_task()
    with pytest.raises(ValueError):
        task.edit(title="New", duration_minutes=-5)
    assert task.title == "Morning walk" and task.duration_minutes == 30
