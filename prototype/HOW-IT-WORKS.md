# How the prototype works

This walks through every real decision in the Request Pipeline Lab: what it does, why it is built this way, and — most importantly — **which parts are honest and which parts are scaffolding that a general version would throw away.**

Read `CONTEXT.md` at the repo root first for the vocabulary (Replica, Pipeline, Stage, Packet, Recorded Run). This document assumes those words.

---

## 1. The constraint that shaped everything

I built this on a cloud machine. It cannot reach your laptop, so `127.0.0.1:8000` does not exist for me. And the output is a page served from `claude.ai`, opened in *your* browser — which also cannot reach your laptop.

That single fact rules out the obvious design (a live debugger attached to your running server) and forces a question:

> If the visualization cannot call Django, how can it show what Django genuinely does?

Three answers were possible:

| Approach | What it means | Why I rejected / chose it |
|---|---|---|
| **Parse the source** | Read `.py` files with `ast`, infer behaviour | ✗ Silently wrong on anything dynamic. `SlugRelatedField` resolving a string to a row is invisible to a parser. The exact thing you wanted to see is the thing static analysis cannot see. |
| **Re-implement the logic** | Port the pricing formula to JavaScript | ✗ Then the visualization shows *my* code, not yours. If your `create()` had a bug, the tool would hide it. |
| **Record and replay** | Actually run Django once, capture every intermediate, replay it in the browser | ✓ Chosen. The values shown are real because they were really produced. |

**This is the load-bearing idea in the whole prototype.** Everything else is consequence.

---

## 2. Two halves, split at the network boundary

```
┌─────────────────────────────┬──────────────────────────────┐
│   CLIENT HALF               │   SERVER HALF                │
│   runs live, right now      │   recorded earlier, replayed │
│                             │                              │
│   DOM                       │   URL Router                 │
│   JavaScript                │   Middleware                 │
│   Browser Network           │   View                       │
│   HTTP Request              │   Serializer                 │
│                             │   Database                   │
└─────────────────────────────┴──────────────────────────────┘
                    ▲
          the split is exactly the
          network boundary the UI draws
```

The **client half is genuinely live**. When you tick a checkbox, real DOM properties change and the project's own `totalPrice()` runs in your browser. When you submit, the payload is built by the project's own submit handler. Nothing is simulated.

The **server half is a recording**. It was produced by really running Django — just at build time instead of at click time.

The nice accident: the seam between "live" and "recorded" falls on exactly the line the tool is trying to teach you about. The boundary is honest in both senses.

---

## 3. The recorder — `extract_all.py`

### 3.1 Booting someone else's Django project

```python
sys.path.insert(0, TARGET_REPO)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurant.settings")
django.setup()
```

That is the whole trick. `django.setup()` populates the app registry, and from that moment the target project's models, serializers and views are ordinary importable Python objects. No parsing, no subprocess — the real classes, in memory.

Then the database is redirected to a throwaway file **before** any query runs:

```python
_tmp_db = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
settings.DATABASES["default"]["NAME"] = _tmp_db.name
call_command("migrate", run_syncdb=True, verbosity=0)
```

Your real `db.sqlite3` is never opened. The recorder builds its own from your migrations.

### 3.2 Issuing a real request and watching it

Everything the visualization shows about the server comes from one function, `perform()`:

```python
with CaptureQueriesContext(connection) as ctx:
    response = fn(path, **kwargs)
```

Django's test `Client` runs the **entire** stack — middleware, URL resolution, the view, DRF's serializer, the ORM. It is not a mock. What comes back out is observed, not asserted:

| Stage shown in the UI | Where the data actually comes from |
|---|---|
| URL Router | `django.urls.resolve(path)` against the real urlconf |
| Middleware | `response.wsgi_request` — `.user`, `.session`, `.method` after middleware ran |
| View | `view_cls.permission_classes`, `.serializer_class`, `.queryset.model` read off the class |
| Serializer (in) | the saved model instance's real related objects |
| Database | `CaptureQueriesContext` — the literal SQL Django emitted |
| Serializer (out) | `response.data` |
| Template | `response.templates` and `response.context` |
| HTTP Response | `response.status_code`, `len(response.content)` |

### 3.3 Source excerpts that cannot go stale

An early version hardcoded line numbers (`serializers.py`, lines 41–75). That breaks the moment you edit the file. It now uses reflection:

```python
lines, start = inspect.getsourcelines(target)
path = os.path.relpath(inspect.getsourcefile(target), TARGET_REPO)
```

The excerpt is located by *identity*, not position. Rename or move `cartitemSerializer` and the excerpt follows it.

### 3.4 Covering the whole input space

For a form-driven endpoint, the user can pick things. Every distinct choice is a different real run, so the recorder enumerates the whole space:

```
3 products × 3 meats × 4 topping subsets × 2 doublemeat × 5 quantities = 360 runs
```

Each keyed by a string like `classic-original|beef-short-plate|mushroom-ball,squid|0|2`. At click time the browser computes the same key from the live form and looks up the matching run. So whatever you pick, you are looking at output Django genuinely produced for exactly those inputs.

**`notes` is the one exception.** It is free text — unenumerable. The recorder submits a sentinel `__NOTE__`, and the player substitutes your typed text into the displayed values. This is only sound because `notes` is a verified pure passthrough (nothing in `create()` reads it). Any field the server *computes with* could never be handled this way.

### 3.5 Stages are derived, not hardcoded

```python
def stages_for(kind, has_body, has_serializer, triggered_by_ui):
```

An endpoint's pipeline is assembled from facts about that endpoint. A DRF endpoint gets `Serializer` stages and no `Template`; a plain Django HTML view gets the reverse; a `GET` skips `Serializer (in)` because there is no input to validate.

This is why the structural contrast is visible in the UI at all — and it is one of the few parts of the recorder that is already general.

---

## 4. The player — `pipeline-lab.src.html`

### 4.1 The replica runs the project's real logic

`totalPrice()`, `getSelectedIngredients()` and the submit handler are the project's own functions from `menudetail.js`. Not a re-description — the same code.

The original prototype went further and used a scope shim so the handler was *byte-identical*:

```js
(function () {
  const fetch = recordedFetch;   // real Django is unreachable from a published page
  ... the project's verbatim submit handler ...
})();
```

The project's code called `fetch(...)` exactly as written; only the environment underneath it was swapped. That is the most honest interception point available — the code does not know it is being observed. (The current multi-endpoint version calls the recorded lookup directly, since it must also serve endpoints the project's JS never calls.)

### 4.2 One function decides what each stage means

```js
function payloadFor(stage, ep, run, live) { switch (stage.id) { ... } }
```

Every stage returns the same envelope: `{ rows, json, wire, sql, note, srcKey, hot }`. The renderer knows nothing about Django — it just draws whatever shape it is handed. Adding a stage means adding one `case`, not touching the UI.

`live` is present only for the client half. That is the entire live/recorded distinction, in one parameter.

### 4.3 Rendering is structured, never a text dump

Data is never `JSON.stringify`'d into a paragraph:

- **Objects** → indented, syntax-lit via `jsonHtml()`, with types coloured distinctly
- **HTTP messages** → start line (bold), headers (muted), separator, then the body rendered as JSON
- **SQL** → broken onto keyword lines and highlighted by `sqlHtml()`
- **Typed values** → `key: [type] value` rows, with changed fields highlighted

The `[type]` badge is the point of the whole tool, so it is a first-class visual element rather than text in a blob.

### 4.4 Build step

`pipeline-lab.src.html` contains the placeholder `__ENDPOINTS_JSON__`. The build inlines `endpoints.json` into it to produce `pipeline-lab.html` (~1.7 MB, fully self-contained — a published page can load no external files).

**Edit `.src.html`, never `.html`.** The latter is generated.

```bash
python3 - <<'EOF'
html = open('pipeline-lab.src.html').read()
data = open('endpoints.json').read().replace('</script>', '<\\/script>')
open('pipeline-lab.html','w').write(html.replace('__ENDPOINTS_JSON__', data))
EOF
```

---

## 5. Honesty ledger

Being explicit about this matters more than the code.

**Genuinely real**
- All server values: `validated_data`, computed prices, SQL, response bodies, status codes, query counts
- URL resolution, middleware effects, permission classes, template names
- Source excerpts (located by reflection at record time)
- All client values: DOM state, the built payload, the JSON string, its byte length
- The pricing logic on both sides — your JS in the browser, your Python in the recording

**Scaffolding**
- **Menu rows are seeded.** Your database ships empty. Prices match your screenshots; meat types are invented.
- **`notes` is substituted** into recorded output (sound only because it is a passthrough — see 3.4).
- **Quantity caps at 5** — the edge of the recorded space, not a real constraint.
- **The replica's markup is hand-written** to match your templates. The *logic* is yours; the HTML is a rebuild.
- **Teaching notes are hand-written** per stage.
- **The cart page shows two fixed line items** — the ones the recorder seeded.

**Two real findings**, verified against recorded runs and surfaced as endpoint notes:
- `PUT /api/cart/item/<id>/` leaves `price` stale — the pricing logic lives only in `create()`, so updates never recompute it.
- `PATCH /api/cart/<id>/` silently discards `table_number` — it is `read_only` on `cartSerializer`. No error; the value is dropped.

---

## 6. What a general version would change

This is the conversation to have next. Sorted by how hard each part is.

### Already general
- `stages_for()` — derives stages from endpoint facts
- `source_of()` — reflection-based excerpts, no project knowledge
- `perform()` — issues any request and observes it
- The entire renderer — it draws envelopes, not Django

### Mechanical to generalize
- **Endpoint discovery.** Currently a hand-written list of 20. Django can enumerate its own routes by walking `get_resolver().url_patterns` recursively. This should be automatic.
- **Model/serializer discovery.** `apps.get_models()` already gives every model; DRF views expose `serializer_class`. No hardcoding needed.
- **Teaching notes.** Currently prose I wrote. Many could be derived from field types: *any* `SlugRelatedField` does the string→instance resolution, so the note can be generated from the field class rather than authored per project.

### The genuinely hard parts

**1. Seed data.** The recorder needs rows to exist. Options: generate from model introspection (fragile with constraints), read the developer's actual dev database (real data, privacy questions), or ask the developer for a fixture. No clean answer.

**2. The input space explodes.** 360 runs works for one form with small discrete choices. A form with a free-text field that the server *computes with*, or a date range, or an ID, cannot be enumerated at all. Record-and-replay has a hard ceiling here.

**3. The replica.** Hand-rebuilding each page does not scale past a demo. Realistic options:
   - **Iframe the developer's actual running app** at `localhost:8000` — real UI, zero rebuild, but the tool must then live on their machine
   - **Proxy the real server** and observe traffic — no rebuild, and it captures *real* interactions
   - **Drop the replica** and become a devtools panel over the app they already have open

### The insight that changes everything

**If the tool runs on the developer's own machine, recording becomes unnecessary.**

Every constraint above exists because I am in the cloud. A tool installed as Django middleware — or a small `pip`-installable app — could instrument **live** requests:

- No seed data problem (the real dev database is right there)
- No input-space explosion (it observes whatever actually happened)
- No replica problem (they use their own app in their own browser)
- No staleness (it reflects the code as it is this second)

The recorder then collapses into something much simpler: a middleware that, per request, captures the same intermediates `perform()` captures now and streams them to an open panel. Roughly:

```
django-pipeline-lab/
├── middleware.py     # capture per request (what perform() does, live)
├── probes.py         # hook DRF serializer + ORM to catch intermediates
├── panel/            # the renderer from this prototype, mostly unchanged
└── urls.py           # serve the panel at /__pipeline__/
```

**The renderer built here transfers almost entirely.** The recorder is the throwaway part — it is an elaborate workaround for a constraint the real product will not have.

That is the argument I would want stress-tested before writing any of it.

---

## 7. File map

| File | Role |
|---|---|
| `extract_all.py` | The recorder. Boots the target project, issues every endpoint, captures everything. Produces `endpoints.json`. |
| `endpoints.json` | 20 endpoints, 380+ recorded runs, deduped SQL pool. Generated — do not hand-edit. |
| `pipeline-lab.src.html` | **The source you edit.** Replica + pipeline + renderer, with a `__ENDPOINTS_JSON__` placeholder. |
| `pipeline-lab.html` | Generated build with the JSON inlined. Self-contained. |
| `kitchen-docket.html` | The first attempt — a static structure map. Kept as a record of what the design moved away from and why. |
| `../CONTEXT.md` | The glossary. |

### Reproducing from scratch

```bash
# Python 3.12+ (the target pins Django==6.1, which needs >=3.12)
python3.12 -m venv /tmp/venv
/tmp/venv/bin/pip install -r /path/to/restautant-order-system/requirements.txt

TARGET_REPO=/path/to/restautant-order-system \
  /tmp/venv/bin/python extract_all.py > endpoints.json

# then inline the JSON (see 4.4)
```
