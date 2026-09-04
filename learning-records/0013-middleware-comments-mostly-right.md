Altitude: mechanical

# Middleware comments: dumps/view peel right; getattr fallback and ensure_ascii slightly off

They restated P1.2 in comments. Solid: `func` is not JSON; build a module+name string; `json.dumps` writes a dict as JSON text; JSON only takes strings/numbers/bools/lists/dicts/None. Off: file header still says empty; `getattr` comment omits the fallback (`None` on 404 / no `view_class`); `ensure_ascii=False` is “keep 經典原味鍋 readable,” not “the string is not ASCII.” `json.dumps` runs on the dict of copied facts, not on a live function.
