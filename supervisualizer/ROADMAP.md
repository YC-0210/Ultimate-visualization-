# Roadmap — supervisualizer

> This folder is the **real tool**, built by hand, that runs on the developer's own machine and watches a live backend.
> `../prototype/` is the throwaway that proved the idea. Do not import from it — port ideas, not files.

---

## Status

```
Current phase:  Phase 0 — deciding
Next action:    P0.4a (OTel nested-value spike), then stage vocabulary
Last updated:   2026-08-27
```

<!-- AGENT: keep the three lines above accurate. Update them at the end of every
     working session: set "Current phase", set "Next action" to the first unchecked
     task ID, and stamp the date. Never mark a task [x] unless its phase's
     "Done when" is actually demonstrable. -->

### How to use this file

**For the Cursor agent.** At the start of a session, read the Status block, find the first unchecked task, and tell me where we are and what is next. Do not skip ahead — phases build on each other. When I finish something, update the checkbox *and* the Status block. If I ask for something that belongs to a later phase, say so and ask whether to reorder deliberately.

**For me.** Every phase ends in something I can *see* working. If a phase is dragging, the phase is too big — split it. Tasks marked 🔴 are the risky ones; do them early in their phase so failure is cheap.

**Decisions marked ❓ are mine to make.** The agent should ask rather than assume.

---

## The one principle

> **Capture is deterministic. The LLM explains; it never observes.**

You said this needs an LLM. Half right — and the half that is wrong matters more than the half that is right.

**An LLM must never be in the capture path.** The whole value of the prototype was that the numbers were real, because real code produced them. The moment a model *infers* what `validated_data` contained, the tool becomes a confident guesser and you cannot trust anything it shows you. Capturing is a solved problem in plain code: middleware, `connection.queries`, `type(v).__name__`. No intelligence required, and none wanted.

**Where the LLM genuinely earns its place:**

| Job | Why an LLM |
|---|---|
| **Explaining a stage** | The teaching notes in the prototype are prose I hand-wrote for *your* code. A model can write them for any code, from the captured facts. This is the big one. |
| **Answering follow-ups** | "Why is `price` a string here?" — chat grounded in the captured trace. |
| **Writing new framework adapters** | Given FastAPI's docs and the Trace schema, generate the adapter. Done once, at development time, by you in Cursor — not at runtime. |
| **Naming unfamiliar stages** | When a framework you don't know produces a call stack, group it into meaningful stages. |

**The test:** unplug the LLM and the tool must still capture and display everything correctly — just without prose. If removing it breaks the data, it is in the wrong place.

---

## Target architecture

```
  YOUR BROWSER                            YOUR DJANGO APP
┌──────────────────────────┐            ┌──────────────────────────┐
│  your app page           │            │  your views/serializers  │
│  ┌────────────────────┐  │ request +  │  ┌────────────────────┐  │
│  │ injected probe     │──┼─ trace-id ►│  │ capture middleware │  │
│  │ script             │  │            │  │  + serializer probe│  │
│  └────────────────────┘  │            │  │  + SQL probe       │  │
│   captures DOM,          │            │  └─────────┬──────────┘  │
│   payload, timing        │            │            │             │
└──────────────────────────┘            │       Trace (JSON)       │
                                        │            │             │
┌──────────────────────────┐            │            ▼             │
│  the panel               │◄─ SSE ─────┼──── trace buffer         │
│  /__supervisualizer__/   │            └──────────────────────────┘
│  (renderer ported        │
│   from prototype)        │            ┌──────────────────────────┐
│         │                │            │  explain service         │
│         └────────────────┼─ on demand►│  (LLM, cached, optional) │
└──────────────────────────┘            └──────────────────────────┘
```

Both halves of the story get stitched by a **trace id** the browser generates and sends as a header. That correlation is what makes `DOM → JavaScript → … → Database` one continuous story instead of two disconnected views.

**The seam that matters for your "all backends" goal:** everything right of the panel talks to it only through the **Trace schema**. Django is one *adapter* producing that schema. Framework #2 is a new adapter, not a new tool. Get the schema right in Phase 1 and Phase 6 is easy; get it wrong and Phase 6 is a rewrite.

---

## Phase 0 — Decide and scaffold

Nothing is built yet. Close the questions that change everything downstream.

- [x] **P0.1** ❓ ~~Name the tool.~~ → **supervisualizer**. Folder renamed. Python package will be `supervisualizer`, Django app label `supervisualizer`, panel served at `/__supervisualizer__/`.
- [x] **P0.2** ❓ ~~Panel delivery.~~ → **A Django app the user installs**, serving the panel at `/__supervisualizer__/`. Not a project, not an extension: `pip install supervisualizer`, add to `INSTALLED_APPS` + `MIDDLEWARE`, done. The panel is just a view. No CORS, no second server, no store review. A browser extension would additionally work on apps you cannot modify, but it cannot see the server side at all — so the Django app would still be needed underneath. Revisit only if watching an unmodifiable app becomes a real requirement.
  - Consequence: panel HTML/CSS/JS must ship *inside* the package — `MANIFEST.in` and the app-template/static-file conventions are load-bearing, not boilerplate.
- [x] **P0.3** ❓ ~~Transport.~~ → **SSE** (`text/event-stream`). The panel only ever receives; WebSockets' second direction would sit unused while costing Channels + ASGI. Plain `StreamingHttpResponse` on the Django side, built-in `EventSource` with free reconnect on the browser side. One-off panel→server calls (e.g. "explain this stage") are ordinary POSTs.
  - Known cost: an open SSE connection holds a worker thread. Irrelevant for a dev tool on `runserver`; would matter under load.
- [ ] **P0.4** ❓ **Trace schema, v0.** The framework-neutral JSON every adapter emits. Three sub-decisions, two already settled:
  - [x] **Shape: a tree, not a flat list.** Each stage carries a `parent_id`. This matches OTel spans and is simply more truthful — the `SlugRelatedField` SQL happens *inside* serializer validation, not beside it. The panel renders depth as indentation, so nesting costs little visually.
  - [x] **Build on OpenTelemetry first**, customise only where it does not stretch. `opentelemetry-instrumentation-django` supplies request and DB spans free; a custom `SpanProcessor` receives finished spans in-process; our own probes attach the values.
  - [ ] 🔴 **P0.4a — the experiment that validates the OTel bet.** OTel attributes are flat scalars (string/number/bool/arrays of those) and **cannot hold a nested dict**. Our data is nested dicts. Spike it in an afternoon: capture one `validated_data` and try to carry it on a span — as a JSON-encoded string attribute, or as a span event. If it fights back, we keep OTel's *shape* and drop the dependency. Do this **before Phase 1**, not in Phase 6.
  - [ ] **Stage vocabulary.** Still open. `kind` = the job (stable, closed, framework-neutral); `label` = what this framework calls it. The panel reads only `kind`; adapters write `label`. Draft list: `receive_input`, `route`, `attach_context`, `authorize`, `validate_input`, `query_data`, `mutate_data`, `render_output`, `send_response`.
    - Prior art is **LSP's `SymbolKind`**, not OTel's `SpanKind` — OTel's classifies messaging role (server/client), not lifecycle job. Copy LSP's discipline: keep the enum small and closed, and make a framework whose concept does not fit **pick the nearest existing kind** rather than adding a new one. Go reports a struct as `Struct`; nobody extends the enum per language. That constraint is what keeps the panel simple.
- [ ] **P0.5** Scaffold an installable Python package (`pyproject.toml`, `pip install -e .`).
- [ ] **P0.6** Add the middleware to `restautant-order-system`'s settings and have it print one line per request.
- [ ] **P0.7** Write `DECISIONS.md` in this folder recording the answers to P0.1–P0.4 *and why*. Future-you will not remember.

**Done when:** `python manage.py runserver` on your restaurant project prints a line from your own middleware on every request.

---

## Phase 1 — Capture the server half

Pure Python. No UI yet. Output is a JSON file you read in a terminal.

- [ ] **P1.1** Capture request basics: method, path, headers, body.
- [ ] **P1.2** Capture the resolved route (`request.resolver_match` — pattern, url_name, view class, kwargs).
- [ ] **P1.3** Capture post-middleware state: `request.user`, session keys, auth.
- [ ] **P1.4** Capture view facts: class, `permission_classes`, `serializer_class`, queryset model.
- [ ] **P1.5** Capture SQL. Note `connection.queries` only populates when `DEBUG=True`; use an execute wrapper instead so it works either way.
- [ ] **P1.6** Capture the response: status, headers, body, size.
- [ ] **P1.7** 🔴 **Probe the serializer.** Capture `validated_data` *and the types inside it* — the string-becomes-model-instance moment. This is the single most valuable thing the tool shows and the most likely to fight you. Wrap `Serializer.is_valid` / `.save` / `.to_representation`. Try it on one endpoint before generalising.
- [ ] **P1.8** Capture template render + context for non-DRF views.
- [ ] **P1.9** Serialise everything to the Trace schema and write it to a file per request.
- [ ] **P1.10** 🔴 Make capture safe: never let a probe crash a real request. Wrap every hook in try/except and drop the trace on failure rather than 500ing the app.

**Done when:** `POST /api/cart/item/` on your running restaurant app produces a Trace JSON containing `validated_data` with real model instances and the SQL Django emitted.

---

## Phase 2 — Panel renders one trace

First visual payoff. Static — you refresh manually.

- [ ] **P2.1** Serve the panel at `/__supervisualizer__/` (dev-only; guard on `DEBUG`).
- [ ] **P2.2** Port `stages_for()` — derive stages from Trace facts, never hardcode them.
- [ ] **P2.3** Port the renderers: `kvRow`, `jsonHtml`, `sqlHtml`, the wire view. These carry over almost unchanged.
- [ ] **P2.4** Port the three-column layout and the type-badge treatment.
- [ ] **P2.5** Load and render the most recent trace.
- [ ] **P2.6** Port stage stepping + the packet animation.

**Done when:** you hit an endpoint in your app, refresh `/__supervisualizer__/`, and see its pipeline with real data at each stage.

---

## Phase 3 — Live

- [ ] **P3.1** Keep the last N traces in memory (ring buffer, capped — do not grow forever).
- [ ] **P3.2** SSE endpoint that pushes new traces.
- [ ] **P3.3** Panel subscribes and renders arrivals with no refresh.
- [ ] **P3.4** A trace list — pick any recent request, not just the newest.
- [ ] **P3.5** Filter out the panel's own requests, or you will watch yourself watching yourself.

**Done when:** the panel is open in one tab, your app in another, and clicking around the app makes pipelines appear live.

---

## Phase 4 — The client half, stitched

**This is the phase that makes it the tool you actually wanted.** Until now it is a nicer Debug Toolbar; after this it tells the whole story.

- [ ] **P4.1** Middleware injects a small probe script into HTML responses (DDT does exactly this — read how).
- [ ] **P4.2** Probe wraps `fetch` and `XMLHttpRequest`.
- [ ] **P4.3** 🔴 **Correlation.** Probe generates a trace id per request, sends it as a header; middleware reads it and stamps the server trace with it. Everything downstream depends on this working.
- [ ] **P4.4** Probe captures the client stages: DOM values read, the JS object built, the JSON string, byte length.
- [ ] **P4.5** Probe posts its client-side half to the tool; server joins the two by trace id.
- [ ] **P4.6** Panel renders one continuous pipeline across the network boundary.
- [ ] **P4.7** Report **client-only interactions** — a checkbox tick that never becomes a request. Lights DOM + JavaScript, dims the rest. Do not skip this; it is where the client/server boundary becomes obvious.
- [ ] **P4.8** ❓ Decide what happens for a JS-framework frontend (React/Vue) where "DOM value" is not where state lives.

**Done when:** ticking a checkbox lights only the client stages; submitting the form shows one unbroken story from DOM to database row and back.

---

## Phase 5 — Explanation (the LLM)

Only now, and only on top of data that is already correct.

- [ ] **P5.1** Define the explanation contract: input is `(stage kind, shape before, shape after, code excerpt)`, output is 1–2 sentences. Structured in, structured out.
- [ ] **P5.2** ❓ Pick a provider and where the key lives. Never commit a key; never send code to a model without the developer opting in explicitly.
- [ ] **P5.3** 🔴 Cache by content hash. Same stage + same shapes = same explanation, fetched once, forever. Without this it is slow and expensive and you will turn it off.
- [ ] **P5.4** Ask-a-question box, grounded in the current trace only.
- [ ] **P5.5** Graceful degradation: no key, no network, or an API error → generic notes derived from field types, tool fully usable.
- [ ] **P5.6** Mark generated prose visibly as generated. It is the one part of the tool that can be wrong.

**Done when:** a stage in a codebase you have never opened gets a genuinely useful explanation, the second view of it is instant, and pulling the key out breaks nothing but the prose.

---

## Phase 6 — Beyond Django

Do not start this before Phase 4 is solid. A second adapter written against an unproven schema is wasted work.

- [ ] **P6.1** Freeze Trace schema v1. Write it down properly, with examples.
- [ ] **P6.2** Extract the Django code behind an explicit `Adapter` interface.
- [ ] **P6.3** Prove the panel is framework-blind: hand it a Trace JSON you wrote by hand for a fictional framework and confirm it renders.
- [ ] **P6.4** ❓ Choose adapter #2. **FastAPI** is closest (Python, ASGI middleware, Pydantic gives the same string→object moment as DRF). **Express** teaches you the JS server ecosystem. Pick by what you want to learn.
- [ ] **P6.5** Write adapter #2 — with the LLM, in Cursor, from the schema and that framework's docs.
- [ ] **P6.6** Zero panel changes required. If the panel needed edits, the schema was wrong — fix the schema, not the panel.

**Done when:** the same panel renders a trace from a non-Django app and you changed no panel code to make it work.

---

## Trace schema — starting point

Not final. Argue with it in P0.4.

```jsonc
{
  "trace_id": "…",              // stitches client and server halves
  "framework": "django",        // which adapter produced this
  "started_at": "…",
  "endpoint": {
    "method": "POST",
    "path": "/api/cart/item/",
    "route_pattern": "api/cart/item/",
    "handler": "cartitemList"
  },
  "stages": [                   // ordered; the panel renders these blindly
    {
      "id": "serializer_in",
      "kind": "serializer",     // panel styles by kind, not by name
      "side": "server",
      "label": "Serializer (in)",
      "data": { /* typed values */ },
      "source": { "file": "…", "line": 41, "code": "…" }
    }
  ],
  "sql": [ { "text": "…", "duration_ms": 0.4 } ],
  "notes": []                   // LLM output attaches here, never inline
}
```

Two things to get right: **`kind` is a closed vocabulary** the panel understands (so a FastAPI "dependency" stage can map onto something known), and **explanations live in a separate list**, so a trace is valid and complete with the LLM switched off.

---

## Open questions worth deciding early

- **Production or dev only?** Dev-only is far simpler — no auth, no PII, no performance budget. Recommended, and say so in the README.
- **Overhead budget.** Probes cost time. What slowdown makes you stop using your own tool?
- **Sensitive data.** Traces contain request bodies — passwords, tokens. Redaction rules, before you demo this to anyone.
- **Who else is this for?** Building it only for yourself is a legitimate answer and simplifies every decision above.

---

## Read these first

| What | Why |
|---|---|
| **Django Debug Toolbar** (source) | The closest existing thing. Middleware capture, HTML injection, panel UI — all solved there. Read it before writing P1 or P4.1. |
| **OpenTelemetry** trace/span model | The industry answer to "framework-neutral trace schema". Read before P0.4. |
| **django-silk** | Another capture approach, different trade-offs. |
| **`../prototype/HOW-IT-WORKS.md`** | Why record-and-replay existed and what carries over. |
| **`../CONTEXT.md`** | The vocabulary. Keep using it so the two folders stay talking about the same things. |
