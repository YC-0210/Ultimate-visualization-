Altitude: mechanical

# getattr is a safe lookup, not a Django API

They did not know `getattr`. In this middleware it is used twice for the same reason: `request.resolver_match` is missing on a 404, and `func.view_class` is missing on a function view. `getattr(obj, "name", None)` returns `None` instead of `AttributeError`. Lesson 0001’s typo trap still applies: a wrong name also returns `None`, so it looks empty.
