# Resources

Trusted sources for this project. Every one has been read or run against — nothing here is a guess. Annotated with *when to reach for it*, because a bare link is useless in three months.

Format follows [`.claude/skills/teach/RESOURCES-FORMAT.md`](.claude/skills/teach/RESOURCES-FORMAT.md).

## Knowledge

- [**Django — Advanced tutorial: How to write reusable apps**](https://docs.djangoproject.com/en/stable/intro/reusable-apps/)
  The official walkthrough of turning an app that lives inside one project into an installable package. Use for: **P0.5** (`pyproject.toml`, `pip install -e .`), and for the distinction between a Django *project* and a Django *app* that shapes supervisualizer's whole delivery model. Also covers how an app finds its own templates and static files once inside someone else's project — which is where the panel's HTML and JS will live. *Read.*

- [**MDN — Using server-sent events**](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)
  The mechanism that turns Phase 2 ("refresh to see") into Phase 3 ("it appears as you click"). Use for: the `StreamingHttpResponse` side and the browser's `EventSource` side. The wire format is `data: {...}` plus a blank line — no library needed. `retry:` and `Last-Event-ID` only matter once you care about resuming after disconnect. *Read.*

- [**Language Server Protocol — `SymbolKind`**](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#symbolKind)
  The proof that the `kind` / `label` split works, from the protocol that made "one editor, many languages" possible. Use for: the Trace schema's stage vocabulary (D7, D8). Copy the discipline — a small closed enum where an ill-fitting concept picks the *nearest* kind rather than adding a new one. Also the source of the M×N → M+N argument that makes one adapter per framework tractable for one person. *Read.*

- [**OpenTelemetry — Traces (Concepts)**](https://opentelemetry.io/docs/concepts/signals/traces/)
  The industry answer to "describe one request in a framework-neutral way". Use for: the span/tree model behind D5, and the semantic-conventions discipline. Note the correction recorded in D7: OTel's `SpanKind` classifies *messaging role* (server/client), **not** lifecycle job — it is not the prior art for our `kind` field. *Read.*

- [**Django Debug Toolbar**](https://github.com/django-debug-toolbar/django-debug-toolbar) (source)
  The closest existing thing to supervisualizer, and the reference implementation for two mechanisms we need. Use for: **P1** (middleware capture) and especially **P4.1** (injecting a script into outgoing HTML responses — how the browser probe gets into the page without the developer editing their JavaScript). *Not yet read — do this before Phase 1.*

## Wisdom (Communities)

Not yet explored. Worth finding before Phase 4, where the browser-probe and correlation problems are the kind of thing others have solved:

- Django Forum (`forum.djangoproject.com`) — for questions about middleware, the ORM's `execute_wrapper`, and app packaging.
- The OpenTelemetry Python repo's discussions — for the "carrying rich values on spans" question, where our answer (JSON-encoded attributes) is probably not unique.

*No preference stated yet on joining communities. Ask before assuming.*

## Gaps

Areas the mission needs where no trusted source has been found yet:

- **Probing DRF specifically.** P0.4a proved monkeypatching `Serializer.is_valid` / `.save` works, but that was arrived at by experiment, not from a source. If a documented extension point exists, it would be more durable than a monkeypatch.
- **Correlating a browser interaction with a server trace.** The `X-SV-Trace` header approach (P4.3) is reasoned, not sourced. Distributed tracing solved this with W3C Trace Context — worth reading before building it.
- **Framework-neutral lifecycle vocabularies.** LSP proves the *pattern*; nobody found doing it for web request lifecycles. If no prior art exists, D8's list stays provisional until P6.4 tests it.
