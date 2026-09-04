# Decisions

Why supervisualizer is built the way it is. One entry per decision that would be expensive to reverse. Add to this whenever a ❓ in `ROADMAP.md` is closed.

Format: what was decided, what else was considered, why this won, and what it costs.

---

## D1 — Runs on the developer's machine, live

**Decided:** supervisualizer watches a running backend on the developer's own machine and reports what it actually did.

**Considered:** the `prototype/` approach — run the target's code ahead of time, record every intermediate, replay the recording in a published page.

**Why:** the prototype recorded only because it was built on a cloud machine that could not reach the developer's laptop, and produced a page that could not either. That constraint does not exist here. Recording brings problems that live capture simply does not have — seeding a database, enumerating an input space that explodes on any free-text field, rebuilding the app's pages by hand, and going stale the moment the code changes.

**Cost:** the tool must be installed to be used. It cannot be shared as a link. If "explain this codebase to someone else" ever becomes a goal, that is a separate product built on an export, not this one.

---

## D2 — Capture is deterministic; the LLM explains, never observes

**Decided:** no model is ever in the path that produces a value the panel displays as fact. Values come from middleware, execute wrappers, and `type(v).__name__`. The LLM writes prose about facts already captured.

**Considered:** letting a model infer what happened from the code, which would need far fewer probes.

**Why:** the entire worth of the prototype was that its numbers were real, because real code produced them. A tool that *infers* what `validated_data` contained is a confident guesser, and nothing it shows can be trusted. Capture needs no intelligence — it is middleware and reflection.

**The test:** unplug the LLM and the tool must still capture and display everything correctly, just without prose. If removing it breaks the data, it is in the wrong place.

**Cost:** every framework needs hand-written probes. There is no shortcut where a model reads the source and skips that work.

---

## D3 — Ships as an installable Django app *(P0.2)*

**Decided:** a Python package. `pip install supervisualizer`, add to `INSTALLED_APPS` and `MIDDLEWARE`. The panel is a view the app serves at `/__supervisualizer__/`.

**Considered:** a browser extension.

**Why:** an app can already ship middleware, views, URLs, templates and static files, so the panel is just a view — no CORS, no second server, no store review. An extension would additionally work against apps you cannot modify, but it cannot see the server side at all, so the Django app would still be needed underneath it. It buys nothing yet.

**Cost:** the panel's assets ship *inside* the package, which makes `MANIFEST.in` and the app static/template conventions load-bearing rather than boilerplate. And it cannot watch an app whose settings you cannot edit.

---

## D4 — SSE, not WebSockets *(P0.3)*

**Decided:** traces reach the panel over Server-Sent Events.

**Considered:** WebSockets, and polling.

**Why:** only the server knows when a request finished, so it has to be able to speak first — which rules out plain request/response, and makes polling both laggy and wasteful. Between the two push options, the panel *only ever receives*; a WebSocket's second direction would sit unused while costing Django Channels and an ASGI deployment. SSE is a `StreamingHttpResponse` on one side and the browser's built-in `EventSource`, which reconnects for free, on the other. One-off panel→server calls such as "explain this stage" are ordinary POSTs.

**Cost:** an open SSE connection holds a worker thread. Irrelevant for a dev tool on `runserver`; would matter under load.

---

## D5 — Stages form a tree *(P0.4)*

**Decided:** each stage carries a `parent_id`. The trace is a tree, not a flat list.

**Considered:** a flat ordered list, as the prototype used.

**Why:** it is simply more truthful. The `SlugRelatedField` SQL happens *inside* serializer validation, not beside it, and a flat list cannot say so. It also matches OTel spans, which are trees. The panel renders depth as indentation, so the extra fidelity costs almost nothing visually.

**Cost:** slightly more care in the renderer, and probes must know their parent.

---

## D6 — Build on OpenTelemetry first *(P0.4)*

**Decided:** try depending on OTel — `opentelemetry-instrumentation-django` for request and DB spans, a custom `SpanProcessor` to receive finished spans in-process, our own probes for values — and customise only where it does not stretch.

**Considered:** borrowing OTel's *shape* (spans, tree, trace/parent ids, semantic-convention discipline) while emitting our own JSON.

**Why (as argued):** OTel already solved framework-neutral request description across dozens of languages, and ships auto-instrumentation for Django, FastAPI, Flask, Express and Rails. If it fits, Phase 6 gets much cheaper.

**✅ CONFIRMED by spike P0.4a — keep the dependency. But the reasoning above was wrong in two places, and the real justification is something it never mentioned.**

**What actually justifies it: context propagation.** Probes monkeypatched into DRF's `Serializer.is_valid` and `.save`, firing deep inside a real request, produced spans that **automatically parented under Django's request span with zero manual context threading**. Building that ourselves means contextvars, a span stack, and correct behaviour under async and threads — real work, easy to get subtly wrong, already done. *That* is what we are paying for.

**Two claimed benefits that do not exist:**
- **"Free Django instrumentation" is one span.** `DjangoInstrumentor` emits exactly one span per request carrying `http.method`, `http.route`, `http.status_code`. The request boundary and nothing else — no view internals, no serializer stages. Every stage that matters is ours to build.
- **"Free DB spans" are not free for Django.** `SQLite3Instrumentor` installs cleanly and captures **zero** ORM queries: Django's ORM uses its own connection wrapper, which `sqlite3` instrumentation never sees. Use `connection.execute_wrapper` (already planned in P1.5).

**Honest summary:** OTel is a context-propagation library we are using as one, plus a tree format. It is **not** an instrumentation shortcut. Do not expect framework #2 to arrive cheaply just because OTel supports that framework — it buys one HTTP span there too.

**Nested values: solved.** A `{type, value}` encoder JSON-dumped into a single string attribute round-trips intact — model instances, non-ASCII, nested lists, 743 chars for a real `validated_data`. No truncation (`max_attribute_length` defaults to `None`; limits are 128 attributes and 128 events per span).

**Overhead:** +3% per request (2.13 ms vs 2.06 ms). Not a concern.

**Consequence, permanent:** OTel does **not** raise on a nested value — it logs a warning and silently drops the attribute. Never conclude a probe worked because no exception was raised. Assert on what is actually present on the finished span.

**Evidence:** `spikes/P0.4a-otel-nested-values.md` and the runnable scripts in `spikes/P0.4a-code/`.

---

## D7 — `kind` and `label` are separate fields *(P0.4)*

**Decided:** every stage carries a `kind` (the job it does — a small closed vocabulary) and a `label` (what this framework calls it). The panel reads only `kind`. Adapters write `label`.

**Considered:** one name field, using the framework's own word.

**Why:** Django says Serializer, FastAPI says Pydantic model, Rails says strong parameters — four words, one job. If the framework's vocabulary leaks into the schema, a second adapter must either impersonate Django or teach the panel a second vocabulary, and that is a rewrite rather than an adapter.

The prior art is **LSP's `SymbolKind`**, not OTel's `SpanKind` — OTel's classifies messaging role (server/client), not lifecycle job. LSP is the proof the pattern works: VS Code knows no Python, the language server sends `kind: 5`, the editor draws a class icon. The historically important part is the arithmetic — LSP turned editor support from M×N into M+N, which is the only reason "works for all backends" is tractable for one person.

**Values are strings, not LSP-style integers.** LSP numbers because it is a high-frequency wire protocol between processes; neither compactness nor name-independent stability applies to traces a human reads while debugging. `"validate_input"` is self-describing; `7` needs a lookup table. OTel uses strings for the same reason.

**The four properties that matter** — none of them numeric: **closed** (fixed list, never free text), **agreed** (panel and every adapter share exactly one list), **stable** (never repurpose a shipped value), **nearest-fit** (a framework whose concept does not fit picks the nearest existing kind rather than adding one). Go reports a struct as `Struct`; nobody extends the enum per language. The last is the easiest to break and the most expensive to undo.

**Cost:** discipline. Every new framework is a temptation to add a kind.

### Verified against the LSP 3.17 spec

Read after the fact from the official spec — [Document Symbols Request](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_documentSymbol), [`DocumentSymbol`](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#documentSymbol), [`SymbolKind`](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#symbolKind) — and the [LSP overview](https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/). Three corrections and one addition.

- ✅ **`SymbolKind.Class = 5`** — the claim above is literally true.
- 🔑 **The prior art is tighter than "inspired by `SymbolKind`."** LSP's `DocumentSymbol` carries *both* fields, exactly as we do: `name` ("The name of this symbol. Will be displayed in the user interface") and `kind: SymbolKind` ("The kind of this symbol"), plus an optional `detail`. Our `label`/`kind` pair is that structure, not merely an analogy to its enum.
- ⚠️ **"Closed" does not mean frozen.** LSP grew the enum from `File`–`Array` (18 values, the initial version) to 26. What is forbidden is *per-language* extension and repurposing a shipped value — growth happens centrally, by protocol version. D8's "provisional until P6.4" is therefore normal protocol practice, not a weakness.
- ➕ **Unknown kinds must degrade gracefully — a rule we had not written down.** LSP makes it a client guarantee: a client declaring which kinds it supports "also guarantees that it will handle values outside its set gracefully and falls back to a default value when unknown." **Consequence for P2.2: the panel must render an unrecognised `kind` in some default way rather than break.** Without that, adding a kind in v2 breaks every older panel.
- **Bonus, supporting D5:** LSP went the same way on trees. `SymbolInformation[]` is "a flat list" and is now deprecated in favour of `DocumentSymbol[]`, "a hierarchy" — "Servers should whenever possible return `DocumentSymbol` since it is the richer data structure." The flat type's own docs admit it "can therefore not be used to re-construct a hierarchy." Two projects reached D5 independently.

---

## D8 — The vocabulary covers the whole round trip *(P0.4)*

**Decided:** fourteen kinds spanning client and server, listed in `ROADMAP.md` under P0.4.

**Considered:** the nine server-lifecycle verbs first drafted.

**Why:** the nine covered only the server's half. Phase 4 adds stages captured by the injected browser probe — reading the DOM, building the payload, `fetch`, parsing the response, updating the page — and none of them fit `receive_input` or `route`. Freezing at nine would have forced Phase 4 to abuse a verb or extend the vocabulary, which is exactly what D7's nearest-fit rule forbids.

**Status: provisional.** The Django column is grounded; the FastAPI and Express columns are reasoned, not verified. A vocabulary that only fits Django is worthless, so this is not frozen as v1 until P6.4 tests it against a framework we did not design it around.

---

## D9 — The learner's state is read from the Daylog, never stored here

**Decided:** the account of what has been learned lives in the **Daylog** — dated entries written by hand on the personal website, one per day of a Project, stored in Supabase. This workspace reads it and stores nothing of its own about the learner. `learning-records/` is deleted, and `LEARNING-RECORD-FORMAT.md` with it. Two things count as evidence that something was learned: **it works** (code that runs, a roadmap "done when" that is demonstrable), or **the learner produced the understanding themselves** — wrote it in the Daylog, or explained it back in their own words unprompted. An agent's summary of a session is neither.

**Considered:** keeping the 81 learning records and fixing their format — adding a date, a source, an evidence field, a supersession discipline, and a generated one-page digest for the agent to read at the start of a session.

**Why:** the records were the wrong shape, not badly filled in. They are the third appearance of a pattern already rejected twice on the personal website. `atoms.hours_spent` was removed there as "a number the Owner types into a form and nothing else in the site ever checks — unfalsifiable, stale the moment it is entered"; the Learning State followed it in ADR-0010 as "the same kind of value: a claim the Owner sets by hand, that nothing verifies, that goes stale silently." A learning record is that value again, and worse in two ways. Hours at least only grew, and hours were at least the learner's own claim; a learning record is the *teacher's* claim about the learner, which is the party with the least standing to make it. The evidence: 81 records, 79 with no date at all, and two supersessions in the whole set — so nothing could be located in time and almost nothing was ever retracted. Meanwhile the Daylog held a live blocker, written plainly, that no record mentioned.

The same argument settles what replaces them: nothing. ADR-0011 derives a Project's visibility and its last-logged date rather than storing them, on the grounds that a stored second answer drifts from the first. A `STATE.md` digest would be exactly that second answer. The Daylog is dated, the code either runs or does not, and both are read at the start of a session — so there is nothing left for a derived file to add that it would not eventually get wrong.

This is D2 pointed at the teaching rather than the tool. Capture is deterministic; the LLM explains and never observes. The Daylog and the working code are the capture. A lesson is prose over facts already captured — and so, it turns out, was every learning record, except that nothing marked it as prose.

**How it works:**

- `bin/pull-daylog.py` caches entries to `./daylog/YYYY-MM-DD.md`. Read-only, stdlib-only, gitignored. The Daylog is the source; the cache is disposable.
- Weighting, in order: working code · an idea used correctly in the Daylog · a claim made in the Daylog ("I think I get X"), which is a self-report and not a demonstration · nothing, for anything the agent concluded by itself. **A stated confusion overrides all of them** on that topic, however recent the apparent progress.
- Confusion is stated **in words**, in prose, unmarked. No tags, no highlight, no syntax. A marker was considered and rejected by the learner: the writing should not bend to make the agent's job easier, and a convention that has to be remembered mid-sentence is one more thing to go stale.
- **The agent never writes to the Daylog** — not through the API, not through a script. Its whole value is that it is the learner's own output; a Daylog an agent can write is just another thing the agent said. The loop closes by **paste**: at the end of a session the agent hands over a short paragraph for that day's entry, and the learner pastes it, edits it, or ignores it.

**Cost:**

- **81 records are gone, and some held real corrections** — the analogy ban, the attribute-versus-method confusion, the `kind`-is-not-a-span question. What survived was re-stated in `NOTES.md` as a standing preference, which is where a rule belongs; the rest is accepted as lost. It was the teacher's memory, not the learner's, and keeping a directory "just for the good ones" reintroduces the file that goes stale.
- **A session now costs a network read**, and the workspace depends on a second system. Offline, the agent has the roadmap, the map and the code, and must say plainly that it cannot see the Daylog rather than guess from the repo.
- **Nothing survives a session that the learner did not write or build.** That is the point, and it means a session that produced neither produced nothing. The teaching has to end in output — code that runs, or something the learner writes — or it does not count.
