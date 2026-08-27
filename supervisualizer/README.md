# supervisualizer

The real tool: runs on your own machine, watches your **live** backend, shows what each request actually did as it happens.

Hand-built. Not generated. This folder is currently empty except for planning docs — that is expected.

## Start here

**[`ROADMAP.md`](ROADMAP.md)** — the phased checklist. It carries a Status block at the top; the Cursor agent reads it to work out where we are and what is next.

## Why this is separate from `../prototype/`

They solve the same problem under opposite constraints.

|  | `../prototype/` | `supervisualizer/` (here) |
|---|---|---|
| Runs where | a cloud machine, then a published page | your laptop |
| Server data | recorded ahead of time, replayed | captured live, as it happens |
| Goes stale | yes — needs re-recording | no |
| Works for | one hardcoded project | any Django project, then other frameworks |
| Status | done, works, throwaway | to build |

The prototype's **recorder** exists only because a cloud machine cannot reach your laptop. That constraint is gone here, so the recorder does not come with us.

The prototype's **renderer** — the stage rail, the typed-value rows, the JSON and SQL formatting — is good and transfers almost unchanged. Port it deliberately, file by file, as Phase 2 calls for it. Do not import across folders.

## Ground rule

> Capture is deterministic. The LLM explains; it never observes.

If an LLM is ever in the path that produces a value the panel displays as fact, the tool has become a guesser. See the roadmap's "The one principle" for the full argument.
