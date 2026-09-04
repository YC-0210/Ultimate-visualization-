Altitude: mechanical

# json.dumps is “write this dict down as text”

Before leaving P1.2 they asked what `json.dumps` is and why it is needed. They have been calling it without the underlying job: a live Python object (`ResolverMatch`, a function, a response) cannot go in a Trace; JSON is strings/numbers/lists/dicts. `dumps` = dump to a string. `ensure_ascii=False` is why `經典原味鍋` stays readable. Next agent: they now have the why; do not re-teach the call, do teach it again if P1.3 tries to dump `request.user` as an object.
