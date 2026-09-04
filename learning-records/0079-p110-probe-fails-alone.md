Altitude: mechanical

# P1.10 done — a probe can fail without taking the request down

They can now tell a streamed `FileResponse` (no `.content`) from an `HttpResponse`, branch on `response.streaming` before reading the body, and wrap capture-only lines in `except Exception` that records to `capture_errors`. Evidence: `/media/menu/images.jpeg` returns 200; a forced `ValueError("x")` in `encode` left the menu page at 200 with `capture_errors: [{ "where": "renders.append", "error": "ValueError: x" }]`. Phase 1 is complete; P2.1 (serve the panel) is next.
