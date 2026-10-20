from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Enter your details and your pets, add care tasks, and generate today's plan.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

# The "vault": create the Owner once per session, then reuse it on every rerun.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        available_minutes=120,
        day_start=time(7, 0),
        day_end=time(21, 0),
    )
if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

owner: Owner = st.session_state.owner

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.name)
available_minutes = st.number_input(
    "Available care minutes today", min_value=1, max_value=1440, value=owner.available_minutes
)
col_start, col_end = st.columns(2)
with col_start:
    day_start = st.time_input("Day starts", value=owner.day_start)
with col_end:
    day_end = st.time_input("Day ends", value=owner.day_end)

if st.button("Save owner"):
    if not owner_name.strip():
        st.error("Owner name cannot be empty.")
    elif day_start >= day_end:
        st.error("The day must start before it ends.")
    else:
        owner.name = owner_name.strip()
        owner.available_minutes = int(available_minutes)
        owner.day_start = day_start
        owner.day_end = day_end
        st.success("Owner saved.")

st.divider()

st.subheader("Pets")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Pet name cannot be empty.")
    else:
        try:
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
            st.success(f"Added {pet_name.strip()}.")
        except ValueError as e:
            st.error(str(e))

if owner.pets:
    st.write("Your pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Tasks")
if not owner.pets:
    st.info("Add a pet before adding tasks.")
else:
    target_pet_name = st.selectbox("Task for", [p.name for p in owner.pets])

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        category = st.selectbox(
            "Category", ["walk", "feeding", "meds", "enrichment", "grooming", "other"]
        )
    with col5:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

    use_preferred = st.checkbox("Set a preferred time")
    preferred_time = st.time_input("Preferred time", value=time(8, 0)) if use_preferred else None

    if st.button("Add task"):
        if not task_title.strip():
            st.error("Task title cannot be empty.")
        else:
            pet = next(p for p in owner.pets if p.name == target_pet_name)
            try:
                task = Task(
                    id=str(st.session_state.next_task_id),
                    title=task_title.strip(),
                    duration_minutes=int(duration),
                    priority=priority,
                    category=category,
                    preferred_time=preferred_time,
                    frequency=frequency,
                )
                pet.add_task(task)
                st.session_state.next_task_id += 1
                st.success(f"Added '{task.title}' for {pet.name}.")
            except ValueError as e:
                st.error(str(e))

task_rows = [
    {
        "Pet": pet.name,
        "Task": t.title,
        "Minutes": t.duration_minutes,
        "Priority": t.priority,
        "Category": t.category,
        "Preferred time": t.preferred_time.strftime("%H:%M") if t.preferred_time else "-",
        "Frequency": t.frequency,
        "Done": "yes" if t.completed else "no",
    }
    for pet in owner.pets
    for t in pet.tasks
]
if task_rows:
    st.write("Current tasks:")
    st.table(task_rows)
elif owner.pets:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Plans every pet's pending tasks within your available time and day window.")

if st.button("Generate schedule"):
    scheduled, skipped = Scheduler(owner).build_plan()

    if not scheduled and not skipped:
        st.info("No pending tasks to schedule. Add some tasks first.")
    else:
        st.success(f"Today's plan for {owner.name}")
        if scheduled:
            st.table(
                [
                    {
                        "Time": f"{s['start_time']:%H:%M}-{s['end_time']:%H:%M}",
                        "Task": s["task"].title,
                        "Pet": s["task"].pet_name,
                        "Minutes": s["task"].duration_minutes,
                        "Priority": s["task"].priority,
                        "Why": s["reason"],
                    }
                    for s in scheduled
                ]
            )
            total = sum(s["task"].duration_minutes for s in scheduled)
            st.caption(f"Total care time: {total} of {owner.available_minutes} minutes")
        for s in skipped:
            st.warning(f"Skipped '{s['task'].title}' for {s['task'].pet_name}: {s['reason']}")
