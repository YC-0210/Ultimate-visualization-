# Ultimate Visualization

An interactive prototype that helps a backend developer see how their Django code actually collaborates — how a request's data changes shape as it moves through models, serializers, and views — instead of only reading it as static source.

## Language

**Target Project**:
The real, external codebase being visualized. For this prototype, `YC-0210/restautant-order-system`, cloned read-only into this environment.
_Avoid_: the other repo, the backend

**Visualizer**:
This repo. Produces the Snapshot from a Target Project and renders it as an interactive HTML page.
_Avoid_: the tool, the app

**Snapshot**:
A JSON extraction of a Target Project's real structure and sample behavior, produced once by running Django/DRF's own reflection (`apps.get_models()`, `Serializer().get_fields()`, URL resolution) against that project, plus actually executing chosen endpoints against sample data in a throwaway in-memory database. Not hand-typed fixture data. Refreshed by re-running the extraction script, not automatically.
_Avoid_: fixture data, mock data

**Structure Map**:
The static diagram view: how a Target Project's models, serializers, views, and URLs relate to each other.
_Avoid_: architecture diagram, graph

**Flow Trace**:
The step-by-step view of how one real request's data changes shape/type as it moves through a single Focus Endpoint's code — captured by actually running that endpoint against sample data, not inferred from reading source alone. Opens on the same screen as the Structure Map, expanding from the node clicked, never a separate tab.
_Avoid_: data flow diagram, sequence diagram

**Focus Endpoint**:
One of the three endpoints chosen from the Target Project for this prototype, each demonstrating a distinct kind of complexity:
- `GET /menuitem/<slug>/` — the simple baseline (plain `ModelSerializer`, no relations)
- `POST /cart/item/` — data reshaping (client-sent slug strings resolved to model instances; a `price` field computed server-side that the client never sent)
- `GET /cart_list/` — a non-API case: no serializer, ends in a server-rendered HTML template; multi-table join via `select_related`/`prefetch_related`; different rows shown to a manager vs. a customer
