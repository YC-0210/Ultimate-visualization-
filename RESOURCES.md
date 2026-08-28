# Supervisualizer capture — resources

## Knowledge

- [Django: `HttpRequest.resolver_match`](https://docs.djangoproject.com/en/5.2/ref/request-response/#django.http.HttpRequest.resolver_match)
  The timing rule: the match exists after URL resolving, in views and in `process_view()`, not in request-phase middleware. Primary source for P1.2.
- [Django: `ResolverMatch`](https://docs.djangoproject.com/en/5.2/ref/urlresolvers/#django.urls.ResolverMatch)
  The fields: `func`, `args`, `kwargs`, `url_name`, `route`, `view_name`. Use for: what to read off the match once it exists.
- [Django: Middleware](https://docs.djangoproject.com/en/5.2/topics/http/middleware/)
  The onion: code before `get_response` vs after, plus `process_view()`. Use for: where to put a probe.
- [Django: `View.as_view()`](https://docs.djangoproject.com/en/5.2/ref/class-based-views/base/#django.views.generic.base.View.as_view)
  The returned callable has `view_class` and `view_initkwargs`. Use for: getting the class name from `match.func` on a CBV.
- [Django Debug Toolbar — `RequestPanel`](https://github.com/django-commons/django-debug-toolbar/blob/main/debug_toolbar/panels/request.py)
  Prior art for capturing view name, args, kwargs, url_name after a request. Uses `resolve()` + `get_name_from_obj` (`view_class` if present). Use for: how a shipped tool names a view.

## Wisdom (Communities)

- [Django Forum — Using Django](https://forum.djangoproject.com/c/users/6)
  Official, moderated. Use for: middleware timing questions that the docs left ambiguous on your project.
- [Django Discord](https://docs.djangoproject.com/en/5.2/faq/help/)
  Official chat, linked from Django's own "Getting help" FAQ. Use for: short "is resolver_match set yet?" checks.

## Gaps

- Django's docs state that `resolver_match` is unavailable in middleware *before* resolving, and name `process_view()` as the hook. They do not spell out the equally valid read *after* `get_response` returns — which is the smallest change to the P1.1 middleware. That mapping is in the lesson, cited back to the onion diagram in the middleware docs.
