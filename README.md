# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Today's plan for Jordan — pets: Mochi (dog), Luna (cat):
  07:30 — Morning walk (30 min) [priority: high] for Mochi
  08:15 — Breakfast (10 min) [priority: high] for Luna
  12:00 — Flea medicine (5 min) [priority: medium] for Luna
  17:30 — Laser pointer play (25 min) [priority: medium] for Luna
  19:00 — Brush coat (20 min) [priority: low] for Mochi

## 🧪 Testing PawPal+

```bash
# Test command
python -m pytest
```
Test Description:
Task basics (2): mark_complete flips the status, and add_task increases the pet's task count.
Sorting (4): sort_by_time returns chronological order with untimed tasks last. It leaves the input list unchanged and handles an empty list, midnight, and equal times (input order kept).
Filtering (1): filter_tasks by pet, by status, by both, and with an unknown pet.
Recurrence (6):
Daily and weekly completion create a follow-up task due the next day or the next week.
A "once" task doesn't recur.
A future-dated copy is excluded from today's tasks.
The next date counts from due_date across a year-end.
Completing an unknown id raises an error.
The daily follow-up is pending, has the right id, and is attached to the pet.
Conflict detection (4): Overlaps warn and back-to-back tasks don't. Same start time warns for the same pet and for different pets, and untimed tasks never conflict.
Plan building (4): Empty plans for an owner with no pets or a pet with no tasks. A task longer than the budget is skipped. A task that exactly fills the budget and day_end is scheduled. The plan is in time order at preferred times.
Validation (1): Bad duration or priority raises ValueError, and a failed edit() rolls back.

Sample test output:

test session starts 
platform darwin -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/mikewang/Desktop/CodePath/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 22 items     

tests/test_pawpal py ......[100%]

22 passed in 0.02s 

Confidence Level: 5 stars

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` uses `sorted()` with a lambda key on `preferred_time`, untimed tasks last; `Scheduler.sort_tasks()` orders by priority first | |
| Filtering | `Owner.filter_tasks(pet_name, completed)` returns tasks matching a pet and/or status; `None` skips that filter | |
| Conflict handling | `Scheduler.detect_conflicts()` returns a warning string for each pair of timed tasks that overlap, saved in `scheduler.warnings` | |
| Recurring tasks | `Task.mark_complete()` returns a copy due +1 day (daily) or +7 days (weekly) via `timedelta`; `Pet.complete_task()` adds it | |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

