Altitude: structural

# After get_response, resolver_match is a ResolverMatch

The user printed `getattr(request, "resolver_match", None)` after `get_response` on `GET /api/menuitem/經典原味鍋/` and got a real `ResolverMatch`: `url_name='menuitem_detail'`, `route='api/menuitem/<str:slug>/'`, `kwargs={'slug': '經典原味鍋'}`. Before the walk it is `None`. That is now the floor.

They also hit the `getattr(..., None)` trap twice: `resolved_route` then `resolved_match` both look like “empty” because Django never sets those names. The real attribute is `resolver_match`.

Next lesson must not re-teach timing. It must teach that this object is not JSON, and that the `func=restaurantAPI.views.menuitemDetail` in Django’s `__repr__` is a display path (`_func_path`), not `match.func` itself.
