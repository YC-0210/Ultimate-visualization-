# View builds context; render reads it

They asked if “render writes HTML, it does not convert the dict” means the view builds the context dict and render only reads it. Yes. Extra floor: unlike `is_valid`, `context["item"]` stays a `menuitem` instance; the HTML is a new string (`response.content`), not a replacement of that key.
