# Ultimate Visualization — glossary

The canonical language for this repo. Use these words in code, commits and docs; when a definition here stops being true, change it here first.

See [`MISSION.md`](MISSION.md) for why the project exists.

---

## Core language

Used across both `prototype/` and `supervisualizer/`.

**Target Project**:
The real, external codebase being observed. Currently `YC-0210/restautant-order-system`.
_Avoid_: the other repo, the backend

**Pipeline**:
The ordered Stages one interaction's data passes through, with its shape shown at each.
_Avoid_: the trace view, the graph

**Stage**:
One named place data occupies on its journey — `DOM`, `JavaScript`, `Browser Network`, `HTTP Request`, `URL Router`, `Middleware`, `View`, `Serializer`, `Database`, `Template`, and the ones carrying the response back. A Stage is a *location*, not a step in time; the Packet is what moves between them.

Which Stages exist is a property of the endpoint, not a fixed list: a DRF endpoint has `Serializer` stages and no `Template`; a plain Django HTML view has the reverse. That contrast is a thing the tool teaches rather than hides.
_Avoid_: node, step, layer

**Kind / Label**:
Every Stage carries both. **Kind** is the job it does — a small, closed, framework-neutral vocabulary (`validate_input`, `route`, `query_data`…). **Label** is what this particular framework calls it ("Serializer (in)", "Pydantic model"). The Panel reads only Kind; Adapters write Label. See D7/D8 in [`supervisualizer/DECISIONS.md`](supervisualizer/DECISIONS.md).
_Avoid_: type, category, stage name

**Packet**:
The moving marker representing the data itself as it travels the Pipeline. Exactly one exists at a time; its position is what the timeline scrubs.
_Avoid_: the dot, the cursor

**Network Boundary**:
The two points where data leaves and re-enters the browser, drawn explicitly because the invisibility of this line is a core part of the confusion being solved.
_Avoid_: the wire, the gap

**Client-only Interaction**:
An interaction the server never learns about — ticking a topping, changing quantity. Lights only the client Stages and dims everything past the Network Boundary. Distinguished from a **Request**, which travels the whole Pipeline.
_Avoid_: local change, no-op

**Data Panel**:
The column that always shows the exact shape and type of the data at whichever Stage the Packet occupies — never behind a click. Source code is the one thing it keeps folded away, because the data is the subject and the code is the explanation.
_Avoid_: the inspector, the detail pane

---

## supervisualizer language

The live tool. See [`supervisualizer/ROADMAP.md`](supervisualizer/ROADMAP.md).

**Probe**:
A small piece of code slipped in beside real code to watch it run, without changing what it does. The **browser probe** is JavaScript injected into outgoing HTML that wraps `fetch`; **server probes** are the monkeypatched `Serializer.is_valid` / `.save`. The defining rule: **remove a Probe and the app behaves identically.** If it changes an answer it is a bug, not a Probe.
_Avoid_: hook, interceptor, patch

**Trace**:
The record of one interaction, assembled in the server's memory as a tree of Stages sharing a trace id. Never travels from browser to server — only the id does, in a header. Joined from the server Probes' spans and the browser probe's separate report.
_Avoid_: log, capture, session

**Panel**:
The page supervisualizer serves at `/__supervisualizer__/`, in a tab of its own. Receives finished Traces over SSE. Reads only the Trace schema — it knows nothing about Django.
_Avoid_: the dashboard, the UI

**Adapter**:
The per-framework code that produces Traces in the schema. Django is one Adapter. A second framework is a new Adapter, not a new tool — that is the entire bet behind the Kind/Label split.
_Avoid_: driver, plugin, backend

---

## prototype language *(historical)*

Terms belonging to `prototype/` only. They do not apply to supervisualizer, and both exist only because a cloud machine could not reach the developer's laptop.

**Replica**:
A working copy of one of the Target Project's pages, running that page's own markup, stylesheet and JavaScript. Not a mockup — the pricing logic and request payload are built by the project's real code; only the data is seeded and `fetch` is intercepted. **supervisualizer has no Replica**: the developer uses their own running app.
_Avoid_: mock, demo page, sandbox

**Recorded Run**:
One real execution of one endpoint, captured ahead of time by issuing the request through Django's test client against a throwaway database and keeping everything observable about it. A Run exists for every combination the Replica offers, so any choice resolves to genuine recorded behaviour rather than a re-implementation. **supervisualizer has no Recorded Runs**: it captures live.
_Avoid_: fixture, mock response, sample data

**Lab**:
The prototype's three-column page — Replica, Pipeline, Data Panel.
_Avoid_: the dashboard, the viewer

**API Console**:
The prototype's list of every endpoint the Target Project defines, each firable directly. It exists because most endpoints DRF generates have no UI at all — nothing in the project's JavaScript ever calls them — and an endpoint with no trigger is still worth understanding.
_Avoid_: the endpoint list, the API browser
