Altitude: mechanical

# Session dict and User are not in the response body

They have the inbound lookup: Cookie `sessionid` → server session dictionary (`table_number`, etc.). Mix-up: those facts and `request.user` are not sent back as the response. The view returns an `HttpResponse` (HTML/JSON, status, headers). The session stays on the server; at most the response repeats `Set-Cookie` with the same lookup number. `request.user` lives on the request object in memory for this visit; next visit Django loads it again from `_auth_user_id` in the session + the database.
