import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Pet, Task


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
