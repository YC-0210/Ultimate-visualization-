Altitude: mechanical

# P1.5 SQL captured on a live request

`execute_wrapper` around `get_response` produced a `sql` list of `{sql, params, duration_ms}`. On `GET /menuitem/經典原味鍋/` (HTML `menuitem_page`, not the JSON API) the list had the menuitem lookup (`params`: `經典原味鍋`), then session, `auth_user`, meattype, and hotpotingredients. Wrapping `get_response` sees every query this request caused, not only the view’s first line.
