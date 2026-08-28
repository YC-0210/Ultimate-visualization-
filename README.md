# Ultimate Visualization

A tool for **seeing** how backend code collaborates — how one interaction's data changes shape as it travels from a browser control to a database row and back.

I can write Django code. What I cannot see is the path a single request takes through the models, views and serializers I wrote — and what happens to my data's **type** at each hop. That gets worse as endpoints multiply. I am a visual learner, and reading source does not show me the journey.

So this is the tool I want to learn with, built to learn by building it.

**→ [`MISSION.md`](MISSION.md)** — the reason, what success looks like, and what is deliberately out of scope. Every decision here should trace back to it.

---

## Two folders

| | |
|---|---|
| **[`prototype/`](prototype/)** | ✅ **Done, and finished.** An AI-built proof that the idea was worth pursuing. Records real Django runs from [`restautant-order-system`](https://github.com/YC-0210/restautant-order-system) and replays them in a published page. Throwaway — but everything it shows is real. |
| **[`supervisualizer/`](supervisualizer/)** | 🚧 **To build, by hand.** The real tool: installs into your own Django project, watches your **live** backend, never goes stale. Django first, other frameworks after. Start at [`supervisualizer/ROADMAP.md`](supervisualizer/ROADMAP.md). |

They solve the same problem under opposite constraints. The prototype recorded ahead of time only because a cloud machine cannot reach a laptop. supervisualizer has no such constraint, so it captures live — **the recorder does not carry over, the renderer does.**

---

## What the prototype showed

Three columns, reacting to each other in real time: the **app**, the **pipeline** of stages a request travels, and the **data structure** at whichever stage the packet occupies.

Two things it makes visible that are otherwise invisible:

- **The client/server boundary.** Ticking a checkbox lights only `DOM` and `JavaScript` and dims everything past the boundary — the server was never told.
- **Where data changes type.** `"2"` (string in the DOM) → `2` (number after `Number()`) → one JSON string → a Python dict where `true` became `True` → `"beef-short-plate"` becomes an actual `<meattype>` row → a `Decimal` computed server-side → back out as the *string* `"360.00"`.

Its core move: it does not guess and it does not re-implement. It **runs the real code and records what happened**, then replays that. Values are real because they were really produced — so if your `create()` has a bug, the tool shows the bug. It found two in the target project, both verified against real runs:

- `PUT /api/cart/item/<id>/` leaves `price` stale — the pricing logic lives only in `create()`, so updates never recompute it
- `PATCH /api/cart/<id>/` silently discards `table_number` — it is `read_only`, so the value is dropped without an error

**Prototype limits** (all consequences of it being a recording, and all gone in supervisualizer): menu rows are seeded; quantity caps at 5 — the edge of the recorded input space; the replica's markup is hand-rebuilt, only the *logic* is the project's own; the API Console fires endpoints directly rather than showing them called from real UI.

---

## Where to start reading

| File | Role |
|---|---|
| [`MISSION.md`](MISSION.md) | **Why this exists.** Read first. |
| [`CONTEXT.md`](CONTEXT.md) | The glossary — the words this project uses and what they mean |
| [`RESOURCES.md`](RESOURCES.md) | Trusted sources, annotated with when to reach for them |
| [`prototype/HOW-IT-WORKS.md`](prototype/HOW-IT-WORKS.md) | How the prototype was built, its honesty ledger, and which seams generalise |
| [`supervisualizer/ROADMAP.md`](supervisualizer/ROADMAP.md) | The phased checklist for the real tool, with a live status block |
| [`supervisualizer/DECISIONS.md`](supervisualizer/DECISIONS.md) | Every architectural decision: what was considered, why it won, what it costs |
