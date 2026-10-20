from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def show(heading: str, tasks: list[Task]) -> None:
    print(f"\n{heading}")
    if not tasks:
        print("  (none)")
    for t in tasks:
        when = f"{t.preferred_time:%H:%M}" if t.preferred_time else "--:--"
        status = "done" if t.completed else "todo"
        due = f"  due {t.due_date}" if t.due_date else ""
        print(f"  {when}  {t.title:<20} {t.pet_name:<6} [{status}]{due}")


def main() -> None:
    owner = Owner(
        name="Jordan",
        available_minutes=120,
        day_start=time(7, 0),
        day_end=time(21, 0),
    )

    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added deliberately out of time order.
    mochi.add_task(Task("1", "Brush coat", 20, "low", "grooming", preferred_time=time(19, 0)))
    luna.add_task(Task("2", "Laser pointer play", 25, "medium", "enrichment", preferred_time=time(17, 30)))
    mochi.add_task(Task("3", "Morning walk", 30, "high", "walk", preferred_time=time(7, 30)))
    luna.add_task(Task("4", "Flea medicine", 5, "medium", "meds", preferred_time=time(12, 0)))
    luna.add_task(Task("5", "Breakfast", 10, "high", "feeding", preferred_time=time(8, 15)))
    mochi.add_task(Task("6", "Vet call", 10, "medium", "admin"))  # no preferred time
    luna.add_task(Task("7", "Window perch time", 20, "low", "enrichment", preferred_time=time(7, 45)))  # overlaps walk

    # Exact same start time: two for the same pet, and one that clashes with another pet.
    mochi.add_task(Task("8", "Training session", 15, "medium", "enrichment", preferred_time=time(12, 0)))
    mochi.add_task(Task("9", "Lunch", 10, "high", "feeding", preferred_time=time(12, 0)))

    mochi.complete_task("1")  # daily task: marks done and queues tomorrow's copy
    luna.complete_task("5")  # Breakfast done too

    scheduler = Scheduler(owner)

    show("All tasks (insertion order):", owner.filter_tasks())
    show("Sorted by time:", scheduler.sort_by_time(owner.filter_tasks()))
    show("Luna only:", owner.filter_tasks(pet_name="Luna"))
    show("Pending only:", owner.filter_tasks(completed=False))
    show("Completed only:", owner.filter_tasks(completed=True))
    show("Mochi + pending:", owner.filter_tasks(pet_name="Mochi", completed=False))
    show("Unknown pet:", owner.filter_tasks(pet_name="Rex"))

    scheduled, skipped = scheduler.build_plan()

    pets = ", ".join(f"{p.name} ({p.species})" for p in owner.pets)
    print(f"\nToday's plan for {owner.name} — pets: {pets}:")
    for item in scheduled:
        task = item["task"]
        print(
            f"  {item['start_time']:%H:%M}-{item['end_time']:%H:%M} — {task.title} "
            f"({task.duration_minutes} min) [priority: {task.priority}] for {task.pet_name}"
        )

    if skipped:
        print("\nSkipped:")
        for item in skipped:
            task = item["task"]
            print(f"  {task.title} for {task.pet_name} — {item['reason']}")

    if scheduler.warnings:
        print("\nWarnings:")
        for w in scheduler.warnings:
            print(f"  {w}")

    total = sum(item["task"].duration_minutes for item in scheduled)
    print(f"\nTotal care time: {total} of {owner.available_minutes} min")


if __name__ == "__main__":
    main()
