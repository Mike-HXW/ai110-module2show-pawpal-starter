import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, time, timedelta

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
