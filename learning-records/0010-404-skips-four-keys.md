Altitude: mechanical

# 404 skips the four keys and does not crash

They hit `GET /a` and got P1.1 fields only — no `route` / `url_name` / `view` / `kwargs` — and no 500. That is the `getattr(..., None)` skip. P1.2 still needs the two matching dumps (CBV menuitem, FBV login). Insomnia had attached a leftover multipart body and an auth token; the body is not part of the 404 check.
