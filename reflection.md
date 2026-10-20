# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design includes four classes: Owner, Pet, Task and Scheduler. The relationship between them is: An owner has one or more pets; A pet has zero or more tasks. Priority is a plain string ("low", "medium" or "high"). The Scheduler reads constraints and tasks from the Owner and returns the plan as a list of dicts.
- What classes did you include, and what responsibilities did you assign to each?
My initial UML design includes classes: owner, pet, task, scheduler. Owners have name, available minutes, day_start, day_end times preferences, and a list of pets. They can add and remove pets. Pets have their names, species, and a list of tasks. They can add and remove tasks. Tasks have its title, duration, priority, category and a completed flag. They can edit themselves. Scheduler builds the plan from the owner's constraints with an attribute of owner. They can build_plan, sort tasks and fit in time to arrange possible time slots.

**b. Design changes**

- Did your design change during implementation?
Yes.
- If yes, describe at least one change and why you made it.
After reviewing the class skeleton for missing relationships and logic bottlenecks, I made three changes. First, I added a `pet_name` field to Task, because a flat list of tasks could not say which pet each task belonged to, so the plan could not say whose task each entry was. Second, I decided that both of the owner's time limits apply: tasks must fall inside day_start to day_end and their total duration cannot exceed available_minutes, so `fits_in_time` now also takes the cursor time to check the end of the day. Third, `build_plan` now returns both the scheduled tasks and the skipped tasks with a reason, so the user can see what did not fit.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
It looks at the owner's available minutes, the day window (day_start to day_end), each task's priority, and an optional preferred time. It also warns when two tasks overlap, and skips tasks that are already done or not due yet
- How did you decide which constraints mattered most?
Time limits come first, because the owner really can't do more than they have time for. Priority is next, so meds and feeding don't get dropped for grooming. Preferred time is just a nice-to-have, so it can move if it has to.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
It picks tasks greedily by priority, then lays them out in time order. When two tasks clash, it only warns and pushes the later one back, so a task can end up away from its preferred time. It may also not find the best possible fit.
- Why is that tradeoff reasonable for this scenario?
A pet owner has only a handful of tasks a day, so a simple greedy plan is fast and easy to understand. Each task also comes with a reason, and clashes show up as warnings, so the owner can adjust things by hand.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I use AI tools to help brainstorm my design and check on my design by figuring out potential errors in my own design and improve it. It is also widly used to write codes in uml, main function and test cases. As the previously defined function is found not consistent to the guidance, it can refractor the code in all related files to correct it.
- What kinds of prompts or questions were most helpful?
The most useful prompts and questions are those with detailed target and object with clear guidance so that AI can handle this efficiently in the right direction as I sugguest without wasting computing power on wrong way.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
