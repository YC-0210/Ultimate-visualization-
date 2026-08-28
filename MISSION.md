# Mission: seeing how backend code actually runs

## Why

I can write Django code, but I have only a vague picture of how the pieces collaborate. I know what a model, a view and a serializer *are* — what I cannot see is the path a single request takes through them, and that gets worse as the project grows and endpoints multiply. I especially cannot see what happens to my **data's type** as it crosses from the browser to the server to the database and back, which is the thing that actually determines how the code parses it.

I am a heavy visual learner. Reading source tells me what each file contains; it does not show me the journey.

So I am building the tool I want to learn with — and building it myself, in Cursor, because instrumenting the request lifecycle is how I will finally understand it.

## Success looks like

- I can open supervisualizer beside my own Django project, click through any endpoint, and watch its real request travel stage by stage.
- I can point at any hop and say what type the data is there and why it changed — `"2"` in the DOM, `2` after `Number()`, `True` in Python, a `<meattype>` row after the serializer, `"360.00"` back out.
- I can tell, by looking, which interactions never leave the browser and which reach the database.
- I understand Django's request lifecycle well enough to have *instrumented* it — middleware, routing, serializers, the ORM — not just used it.
- The tool works on a backend I did not write, which is the proof it captures something general rather than something I memorised about my own project.

## Constraints

- **Learn by building.** The code in `supervisualizer/` is written by me. AI plans, explains, reviews and spikes; it does not hand me a finished tool. (`prototype/` was the deliberate exception — an AI-built proof that the idea was worth pursuing.)
- **Visual first.** Seeing the mechanism beats reading about it. Explanations should reach for a diagram or a worked example before prose.
- **One idea at a time.** One concept per exchange, one reference per concept, with a stated reason why it matters to this project.
- **Django first**, because I know it best. Other frameworks only once Django works end to end.
- Unfamiliar languages and tools are fine — that is part of the point.

## Out of scope

- Production monitoring and APM. This is a dev-time learning tool; the moment it needs auth, sampling and PII handling it has become a different product.
- Shareable recordings — the `prototype/` path, where a trace is captured and sent to someone else. Real, but a different product; parked deliberately (see `supervisualizer/DECISIONS.md` D1).
- Frameworks beyond Django, until Phase 6.
- Making the prototype nicer. It has done its job.

---

*Format follows [`.claude/skills/teach/MISSION-FORMAT.md`](.claude/skills/teach/MISSION-FORMAT.md). Every decision in `supervisualizer/DECISIONS.md` and every phase in `ROADMAP.md` should trace back to something above. When this mission stops being true, change it here first.*
