Altitude: structural

# Cookie is the lookup number; session is the dictionary

They finished P1.3 and stated the lookup correctly: the request’s Cookie header has `sessionid`, Django uses it to find a dictionary on the server. They saw live keys `table_number`, `cart_id`, `_auth_user_id`, `_auth_user_backend`, `_auth_user_hash`. On this restaurant app `cart_id` in the session is how later add-to-cart finds the cart (`models.py`).

Correction: the cookie does not store those facts. Django’s docs: cookies contain a session ID, not the data itself. `table_number` / `cart_id` / `_auth_user_*` live in the session dictionary. The Cookie header can also carry `csrftoken=` — a different pair, not the session lookup.

P1.3 is the floor. Next is P1.4.
