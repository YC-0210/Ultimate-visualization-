Altitude: mechanical

# Trace view string is rebuilt from view_class, not from the print or from func

The user can now state the CBV peel: `match.func` is a function so it cannot go in the Trace; the string `"restaurantAPI.views.menuitemDetail"` is `view_class.__module__ + '.' + view_class.__qualname__`. Floor for the class-based API view.

Still to confirm in practice: `view_class` is read off `func` (`getattr(func, "view_class", None)`); a function view has no `view_class` and uses the same recipe on `func` itself. Next is lesson 0002’s four-field JSON on the restaurant app, including `/login/` and a 404.
