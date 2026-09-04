Altitude: structural

# Read after get_response because the work is inside that call

They stated the wrapping reason correctly: the request goes inward layer by layer via `get_response`; session and user are stamped by inner middleware, so the read belongs after that call returns. One correction: `resolver_match` is not an inner name on the `MIDDLEWARE` list — Django’s URL walk sets it further inside the same `get_response` (the kitchen side), on the same request object. Floor for P1.4: they know why the probe sits after `get_response`, not only that it does.
