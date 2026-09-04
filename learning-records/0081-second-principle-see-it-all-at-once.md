Altitude: structural

# A second principle: "if I can't see it all at once, I don't understand it yet"

After reading Bret Victor's *Learnable Programming* and *Inventing on Principle*, they named the felt problem precisely: they keep losing the high-level understanding of their own project. The diagnosis they accepted is that the workspace had a principle about **honesty** (capture is deterministic) and none about **visibility** — so the tool obeyed Victor while the learning system around it did not. Nineteen lessons, seventy-eight learning records and fifteen reference cards existed with no index, no map, and no page showing the whole; assembling them happened in their head, which is where the understanding was supposed to end up.

Adopted as principle 2 in `MISSION.md`, and acted on: [`MAP.html`](../MAP.html) now shows the whole request journey and the whole build at once, with three tenses, and every lesson links back to it.

**Implications for future sessions.** Two rules follow and both are now in the skill. A part is only promoted to "done" on the map when the underlying thing *works*, never because a lesson explained it — a future stage shows no data, because an empty stage says "nothing observed this" while a plausible-looking one asserts a fact nothing produced (the same argument as D2, applied to teaching). And a long run of `Altitude: mechanical` records is the signal that teaching has drifted down-altitude: stop and teach the whole.

**Correction they made to the proposed work.** The original suggestion was to feed real Trace JSON into lessons for an immediate change→effect loop. They rejected the framing — a true immediate connection between their code and its data needs something closer to a new IDE — and replaced it with a better one, from "coding is manipulating the data": what is needed is to *see the data at a broad granularity*, time-framed or event-driven rather than step-by-step, with past, present and future all on one axis. That is `assets/timeline.js`, and the future section is the part they have not written yet. Reach for that component, not a prose paragraph, whenever the subject is data moving through a system.
