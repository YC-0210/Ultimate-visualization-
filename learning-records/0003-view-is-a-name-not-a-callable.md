# The view field is a name string, not something to call

P1.2 copies four JSON-safe pieces off `ResolverMatch`. The user has: the match is a Python object; Django already called the view; the Trace only needs to record *which* handler ran.

Two corrections from this session:

1. Do not parse the print `func=restaurantAPI.views.menuitemDetail`. That label is `_func_path` (display). `match.func` is the `as_view()` wrapper; the class is `func.view_class`.
2. Do not look for a way to *call* the class. The probe watches. The Trace wants a string that *names* the handler.

Still open at the time: they knew it must be a string. They then named the string (`restaurantAPI.views.menuitemDetail`) but did not see why that is a trap if the letters match the print. That beat moved to lesson 0003.
