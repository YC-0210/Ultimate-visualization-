# Ultimate Visualization

A tool for **seeing** how backend code collaborates — how one interaction's data changes shape as it travels from a browser control to a database row and back.

Built because reading Django source tells you what each file contains, but not how a request actually moves through them, and not what happens to your data's *type* at each hop.

## Two folders

| | |
|---|---|
| **[`prototype/`](prototype/)** | ✅ Done. Proves the idea against one codebase ([`restautant-order-system`](https://github.com/YC-0210/restautant-order-system)) by recording real Django runs and replaying them in a published page. Throwaway, but everything it shows is real. |
| **[`supervisualizer/`](supervisualizer/)** | 🚧 To build. The real thing: runs on your own machine, watches your **live** backend, never goes stale. Django first, other frameworks after. Start at [`supervisualizer/ROADMAP.md`](supervisualizer/ROADMAP.md). |

The prototype recorded ahead of time because a cloud machine cannot reach a laptop. The tool has no such constraint, so it captures live instead — the recorder does not carry over, but the renderer does.

---

## What it does

Three columns, reacting to each other in real time:

| | |
|---|---|
| **App** | A working copy of the target project's pages, running that project's own JavaScript |
| **Pipeline** | The stages a request travels — `DOM → JavaScript → Browser Network → HTTP Request →` ⎯*network boundary*⎯ `→ URL Router → Middleware → View → Serializer → Database`, then back out |
| **Data structure** | The exact shape and **type** of the data at whichever stage the packet currently occupies |

Interact with the app and the pipeline animates. Two things it makes visible that are otherwise invisible:

- **The client/server boundary.** Ticking a checkbox lights only `DOM` and `JavaScript` and dims everything past the boundary — the server was never told.
- **Where data changes type.** `"2"` (string in the DOM) → `2` (number after `Number()`) → one JSON string → a Python dict where `true` became `True` → `"beef-short-plate"` becomes an actual `<meattype>` row → a `Decimal` computed server-side → back out as the *string* `"360.00"`.

All 20 endpoints the target project defines are covered — including the 14 that DRF generates but the project's own JavaScript never calls.

---

## Reading the code

Start with **[`prototype/HOW-IT-WORKS.md`](prototype/HOW-IT-WORKS.md)**. It covers the architecture, the one constraint that shaped every decision, an explicit ledger of what is real versus scaffolding, and where the seams for a general version are.

Then:

| File | Role |
|---|---|
| [`prototype/extract_all.py`](prototype/extract_all.py) | The recorder — boots the target Django project and observes every endpoint |
| [`prototype/pipeline-lab.src.html`](prototype/pipeline-lab.src.html) | The player — replica, pipeline and renderer (**edit this, not the `.html`**) |
| [`CONTEXT.md`](CONTEXT.md) | The glossary — the words this project uses and what they mean |

---

## The core idea

The visualization cannot call Django live, so it does not guess and it does not re-implement. It **runs the real code once and records what happened** — `validated_data`, the SQL Django emitted, the response body, the resolved route — then replays that recording in the browser.

Values are real because they were really produced. If your `create()` has a bug, the tool shows the bug.

It found two, both verified against real runs:

- `PUT /api/cart/item/<id>/` leaves `price` stale — the pricing logic lives only in `create()`, so updates never recompute it
- `PATCH /api/cart/<id>/` silently discards `table_number` — it is `read_only`, so the value is dropped without an error

---

## Known limits

- Menu rows are seeded (the target database ships empty)
- Quantity caps at 5 — the edge of the recorded input space
- The replica's markup is hand-rebuilt; only the *logic* is the project's own
- The API Console fires endpoints directly rather than showing them being called from real UI interaction
