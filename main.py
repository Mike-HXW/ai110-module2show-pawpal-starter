from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


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

    mochi.add_task(Task("1", "Morning walk", 30, "high", "walk", preferred_time=time(7, 30)))
    mochi.add_task(Task("2", "Brush coat", 20, "low", "grooming", preferred_time=time(19, 0)))
    luna.add_task(Task("3", "Breakfast", 10, "high", "feeding", preferred_time=time(8, 15)))
    luna.add_task(Task("4", "Flea medicine", 5, "medium", "meds", preferred_time=time(12, 0)))
    luna.add_task(Task("5", "Laser pointer play", 25, "medium", "enrichment", preferred_time=time(17, 30)))

    scheduled, skipped = Scheduler(owner).build_plan()

    pets = ", ".join(f"{p.name} ({p.species})" for p in owner.pets)
    print(f"Today's plan for {owner.name} — pets: {pets}:")
    for item in scheduled:
        task = item["task"]
        print(
            f"  {item['start_time']:%H:%M} — {task.title} ({task.duration_minutes} min) "
            f"[priority: {task.priority}] for {task.pet_name}"
        )

    if skipped:
        print("\nSkipped:")
        for item in skipped:
            task = item["task"]
            print(f"  {task.title} for {task.pet_name} — {item['reason']}")

    total = sum(item["task"].duration_minutes for item in scheduled)
    print(f"\nTotal care time: {total} of {owner.available_minutes} min")


if __name__ == "__main__":
    main()
