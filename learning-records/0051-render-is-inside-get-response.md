Altitude: mechanical

# Context is copied during get_response, not after

They had “copy during Template.render” right, then placed that call after `get_response`. Floor: `render` runs *inside* the view, which runs *inside* `get_response` — same timing as `is_valid` and SQL. After `get_response` returns, the context dict is gone; `response.content` is already HTML.
