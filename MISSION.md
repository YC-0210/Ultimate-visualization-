# Mission: Capture a live Django request by hand

## Why
You are building **supervisualizer** — a tool that watches your own restaurant app and shows what each request actually did. The panel is only trustworthy if every value on it came from code that observed the request, not from a model guessing. You are learning Django's request lifecycle by writing those observers yourself, starting with the URL Router stage.

## Success looks like
- On a real request to the restaurant app, you can print the resolved route: pattern, `url_name`, view class, and kwargs.
- You know *when* in middleware those facts exist, and you do not read them at a moment Django has not filled them in yet.
- Later stages (user, SQL, serializer) plug into the same capture habit: observe, serialise, never infer.

## Constraints
- Teaching files live at this repository root (`MISSION.md`, `lessons/`, `assets/`, …), **not** inside `supervisualizer/` — that directory is the installable Python package.
- Project roadmap: [`supervisualizer/ROADMAP.md`](supervisualizer/ROADMAP.md)
- Phases build on each other — do not skip ahead to the panel.
- Capture stays deterministic: no LLM in the path that produces a displayed fact.
- Work against the live restaurant project, not a toy app.
- Teach the logic of how the software actually runs. Syntax is secondary.

## Out of scope
- Panel UI (Phase 2), live SSE (Phase 3), the browser probe (Phase 4), LLM explanations (Phase 5), a second framework (Phase 6).
