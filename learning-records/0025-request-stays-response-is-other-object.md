# After get_response, two objects: request still here, response just arrived

They applied the onion correctly (outward is the response coming back) and then asked why `getattr` reads `request`, not `response`. Correction: `get_response(request)` returns a new `HttpResponse` (the plate). The `request` parameter is still in `__call__` — inner code stamped `session`, `user`, `resolver_match` on that same object. Those names are not on the response. Deepens LR-0021. The log line `response captured` is *when*, not *which object*.
