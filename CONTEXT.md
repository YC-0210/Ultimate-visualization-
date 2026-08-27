# Ultimate Visualization

An interactive prototype that helps a backend developer see how their Django code actually collaborates — how one real interaction's data changes shape as it moves from a browser control all the way to a database row and back — instead of only reading it as static source.

## Language

**Target Project**:
The real, external codebase being visualized. For this prototype, `YC-0210/restautant-order-system`, cloned read-only into this environment.
_Avoid_: the other repo, the backend

**Visualizer**:
This repo. Produces the Recorded Runs from a Target Project and renders the Lab.
_Avoid_: the tool, the app

**Lab**:
The split-screen page: the Replica on the left, the Pipeline on the right, reacting to each other in real time.
_Avoid_: the dashboard, the viewer

**Replica**:
A working copy of one of the Target Project's pages, running that page's own template markup, stylesheet, and JavaScript. It is not a mockup — the pricing logic and the request payload are built by the project's real code. Only its data is seeded and its `fetch` is intercepted, because a published page can reach neither the developer's machine nor their database.
_Avoid_: mock, demo page, sandbox

**Pipeline**:
The right-hand instrument: the ordered Stages a single interaction passes through, with the data's current shape shown at each one.
_Avoid_: the trace view, the graph

**Stage**:
One named place data occupies on its journey — `DOM`, `JavaScript`, `Browser Network`, `HTTP Request`, `URL Router`, `View`, `Serializer`, `Database`, and the four that carry the response back. A Stage is a *location*, not a step in time; the Packet is what moves between them.
_Avoid_: node, step, layer

**Packet**:
The moving marker representing the data itself as it travels the Pipeline. Exactly one exists at a time; its position is what the timeline scrubs.
_Avoid_: the dot, the cursor

**Network Boundary**:
The two points where data leaves and re-enters the browser, drawn explicitly because the invisibility of this line is a core part of the confusion being solved.
_Avoid_: the wire, the gap

**Client-only Interaction**:
An interaction the server never learns about — ticking a topping, changing quantity. It lights only the `DOM` and `JavaScript` Stages and dims everything past the Network Boundary. Distinguished from a **Request**, which travels the whole Pipeline.
_Avoid_: local change, no-op

**Recorded Run**:
One real execution of the Target Project's server code — captured by actually running `cartitemSerializer` against a throwaway database and keeping every intermediate (`validated_data`, the computed price, the emitted SQL, the response body). A Run exists for every combination of choices the Replica offers, so whatever the user picks resolves to genuine recorded behavior rather than a re-implementation.
_Avoid_: fixture, mock response, sample data
