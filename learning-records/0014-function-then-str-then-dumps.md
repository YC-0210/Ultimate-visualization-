# View goes function → Python str on the dict → JSON text

They have the order: peel the function into a string, put it on `captured['view']`, then `json.dumps`. The muddy phrase was “assign as the python object.” `captured['view']` holds a Python `str`, not the function. The dict is still Python until `dumps` makes JSON text.
