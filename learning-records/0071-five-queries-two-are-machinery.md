Altitude: mechanical

# Their GET emits five queries; only three are the view's reads

On `GET /menuitem/經典原味鍋/` (logged in as `kenny`, `table_number` 9) the wrapper caught five queries: `menuitem` by slug, `django_session`, `auth_user` id=1, all `meattype`, all `hotpotingredients`. The middle two are session/auth machinery, triggered by something touching `request.session` / `request.user` inside `get_response` — not the view's data reads. Consequence recorded in the Trace schema card and lesson 0018: keep `sql` as one flat top-level list, because `execute_wrapper` is handed the SQL and not the caller, so per-stage attribution would be an invented fact (D2). Attribution waits for the stage-aware probe (D6 context propagation).
