Altitude: mechanical

# Four-field dump nested inside captured['view']

They copied the peel after `get_response` correctly (`view_class` branch, `getattr` for a missing match). They then `json.dumps`’d the four-field dict into `captured['view']` and dumped `captured` again, so `view` is a JSON string of four keys, not the view name, and the four fields are not sibling keys. P1.2 wants one dump of `{route, url_name, view, kwargs}`.
