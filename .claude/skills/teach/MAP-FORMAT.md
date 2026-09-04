# MAP.html Format

`MAP.html` lives at the workspace root. It is the **one page that shows the whole topic at
once**: every part, how the parts connect, what the learner has covered, what they are
working on now, and what has not been reached yet — with every lesson and reference
document hung off the part it explains.

It exists because of one principle:

> **If I can't see it all at once, I don't understand it yet.**

A part understood in isolation is a part the learner will lose. Every other artifact in
this workspace is either *purpose* (`MISSION.md`) or *detail* (`lessons/`, `reference/`,
`learning-records/`). Without a map, assembling those into a whole happens in the learner's
head — which is where the understanding was supposed to end up, not where the filing should
happen.

## When a workspace earns one

Build a map as soon as **either** is true:

- The topic is a **system** — something with parts that pass work to each other. A request
  lifecycle, a compiler, a protocol stack, a metabolic pathway, a supply chain. If the
  learner will ever ask "where does this bit sit?", they need a map.
- The workspace has **more than about eight lessons**. Past that, a directory listing has
  stopped being a map and the learner is navigating by filename.

Do not build one for a topic that is a flat list of independent skills (a stretching
routine, a vocabulary set). There is no whole to see.

## What goes on it

1. **The principles**, at the top. Whatever the project has decided is non-negotiable.
   The map is where they get re-read.
2. **The spine** — the parts, in the order work passes through them, drawn once.
3. **A timeline of the subject** at the granularity the learner thinks in — stages, phases,
   events — *not* line-by-line steps. See [Tense](#tense).
4. **Where everything hangs** — a table mapping every lesson and reference document to the
   part it explains. Empty cells are the point: they show what has no lesson yet.
5. **The words**, by tier, if the topic has coined vocabulary. Which tier a word belongs to
   tells the learner whether official docs exist to search for.
6. **Links out** to `MISSION.md`, the roadmap, the glossary, the resources.

## Tense

Every part on the map carries one of three tenses, and they must be visually distinct:

| Tense | Means | Rule |
|---|---|---|
| `past` | Built, or learned, and demonstrated | Show the real data or the real artifact |
| `present` | The thing being worked on right now | Exactly one region should be present |
| `future` | Not reached yet | **Show no data** |

The third is load-bearing and the easiest to get wrong. A future part must never be drawn
the same way as a completed one, and must never carry example data that looks captured. An
empty future part says "nothing has observed this yet," which is true; a plausible-looking
one asserts a fact nothing produced.

Promote a part from `future` to `past` only when the underlying thing **actually works** —
the same bar the roadmap's "done when" sets. A lesson explaining a part does not move it.

## The map is a mirror, not a source

When the workspace has a roadmap, **the roadmap owns status** and the map reflects it. Say
so on the page itself. Update the roadmap first, then the map. Never let the map become a
second, competing record of progress — that is the failure the roadmap section of
[SKILL.md](./SKILL.md#orienting-to-a-project-roadmap) already warns about, and a map is the
most tempting place to commit it.

## Keeping it alive

A stale map is worse than no map, because it is believed.

- **Every lesson links back to it.** Put the link in the lesson's "Where this fits" block.
  One click from any part to the whole.
- **Every lesson updates it.** When a lesson lands, hang it off the part it explains.
  When a roadmap task lands, move the tense. This is not optional bookkeeping; it is the
  lesson's last step.
- **Read it at the start of a session**, alongside the roadmap's Status block. It is the
  fastest way to answer "where are we" and it is what you state back to the learner.

## Build it from components

The map is HTML in `./lessons/`' house style — link the workspace stylesheet so it reads as
part of one course. Anything reusable on it (a timeline scrubber, a spine diagram) belongs
in `./assets/` like any other component, so lessons can use the same widget on a smaller
scale. A map built from one-off inline code is a map nobody will update.
