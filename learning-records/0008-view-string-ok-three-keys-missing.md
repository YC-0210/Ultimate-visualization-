# View string is a sibling key; route, url_name, kwargs still missing

They stopped nesting `json.dumps` inside `captured['view']` and now store the peeled view string. Timing and the `view_class` branch remain correct. The dump still only adds `view`. P1.2’s object is four keys: `route`, `url_name`, `view`, `kwargs`.
