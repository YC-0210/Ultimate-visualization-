# P1.5 summary: during, not before; context manager; queries then captured

They had the lesson’s shape right (P1.4 is the class; P1.5 is the SQL string; wrap `get_response`; QueryLogger appends). Three corrections: copying runs *during* `get_response` (install is before; the queries are not grabbed beforehand); it is a *context* manager, not a content manager; the wrapper appends to `queries`, and `captured["sql"]` is assigned after the `with`.
