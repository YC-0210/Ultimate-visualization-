Altitude: mechanical

# P1.1: request basics are already captured in middleware

The user can read `request.method`, `request.path`, `request.headers`, and `request.body` in `SupervisualizerMiddleware.__call__` *before* `get_response`, JSON-encode them, and print one line per request. Binary bodies are replaced with a length placeholder instead of crashing.

This is now the floor. P1.2 must not re-teach how to build a `captured` dict. It must teach the facts that do **not** exist at that same moment — starting with `request.resolver_match`.
