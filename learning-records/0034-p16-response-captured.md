# P1.6 response captured on a live request

They nested `{status, headers, body, size}` under `captured["response"]` after `get_response`. On `GET /menuitem/經典原味鍋/` (HTML `menuitem_page`, not the JSON API): status 200, `Content-Type: text/html; charset=utf-8`, body the customize-page HTML, size 5342 matching `Content-Length`. Request `headers`/`body` were not overwritten. The four fields sit outside `if match`.
