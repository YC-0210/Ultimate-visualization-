# Supervisualizer capture — resources

## Knowledge

- [Django: URL dispatcher — How Django processes a request](https://docs.djangoproject.com/en/5.2/topics/http/urls/#how-django-processes-a-request)
  The walk: load `urlpatterns`, try each pattern in order, stop at the first match, call that view. Use for: what “URL resolving” actually is. Primary source for lesson 0001’s lookup section.
- [Django: Including other URLconfs](https://docs.djangoproject.com/en/5.2/topics/http/urls/#including-other-urlconfs)
  “Whenever Django encounters `include()`, it chops off whatever part of the URL matched up to that point and sends the remaining string to the included URLconf.” Use for: P2.1 — why `supervisualizer/urls.py` matches `""`, not the full prefix. Primary source for lesson 0021. They already `include('restaurantAPI.urls')` under `api/`.
- [Django: `DEBUG`](https://docs.djangoproject.com/en/5.2/ref/settings/#debug)
  “A boolean that turns on/off debug mode.” “Never deploy a site into production with `DEBUG` turned on.” Use for: P2.1 — wrap the panel include so the prefix is absent when `DEBUG` is False. Traces carry `Cookie`.
- [Django: `HttpRequest`](https://docs.djangoproject.com/en/5.2/ref/request-response/#httprequest-objects)
  One object per visit: method, path, COOKIES, body, GET/POST, META, plus later `resolver_match`, `session`, `user`. Use for: lesson 0005 — what is inside `request`. “When a page is requested, Django creates an HttpRequest object… passing the HttpRequest as the first argument to the view.”
- [Django: `HttpResponse`](https://docs.djangoproject.com/en/5.2/ref/request-response/#httpresponse-objects)
  The object the view returns. Django builds the request; the view is responsible for the response. Pockets for P1.6: `status_code`, `headers`, `content` (bytes), size via `len(content)`. Use for: lesson 0009. “HttpResponse objects are your responsibility.”
- [Django: `HttpResponse.content`](https://docs.djangoproject.com/en/5.2/ref/request-response/#django.http.HttpResponse.content)
  “A bytestring representing the content, encoded from a string if necessary.” Same type as `request.body`. Use for: decode like P1.1; size is a byte count.
- [Django: `HttpResponse.headers`](https://docs.djangoproject.com/en/5.2/ref/request-response/#django.http.HttpResponse.headers)
  Case-insensitive dict-like headers on the way out. Docs: all headers except `Set-Cookie` (that is `response.cookies`). Use for: P1.6 `dict(response.headers)`.
- [Django: `StreamingHttpResponse`](https://docs.djangoproject.com/en/5.2/ref/request-response/#streaminghttpresponse-objects)
  No `.content`. Docs: do not consume `streaming_content` in middleware. `HttpResponse.streaming` is always `False` so middleware can tell the two apart. Use for: skip the body on a streaming response; the restaurant JSON GET is not one.
- [Django: `HttpRequest.resolver_match`](https://docs.djangoproject.com/en/5.2/ref/request-response/#django.http.HttpRequest.resolver_match)
  When the result of that walk is on the request: after resolving, in views and `process_view()`, not in request-phase middleware. Use for: P1.2 timing.
- [Django: `ResolverMatch`](https://docs.djangoproject.com/en/5.2/ref/urlresolvers/#django.urls.ResolverMatch)
  The fields: `func`, `args`, `kwargs`, `url_name`, `route`, `view_name`. Use for: what to read off the match once it exists.
- [Django: Middleware](https://docs.djangoproject.com/en/5.2/topics/http/middleware/)
  Plugin that takes a request and returns a response. `get_response` is the next middleware or eventually the view. Onion: inward top-down, outward reverse. Order matters because one middleware can depend on another. Use for: lesson 0006 wrapping; where to put a probe.
- [Django: Middleware ordering](https://docs.djangoproject.com/en/5.2/ref/middleware/#middleware-ordering)
  Hints: AuthenticationMiddleware after SessionMiddleware (uses session storage). Use for: why the restaurant `MIDDLEWARE` list is not arbitrary.
- [Django: `View.as_view()`](https://docs.djangoproject.com/en/5.2/ref/class-based-views/base/#django.views.generic.base.View.as_view)
  The returned callable has `view_class` and `view_initkwargs`. Use for: getting the class name from `match.func` on a CBV.
- [Django Debug Toolbar — Installation, step 4 “Add the URLs”](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html)
  The toolbar is extra paths on the same URLconf. Default prefix `__debug__`. `debug_toolbar_urls()` returns `[]` when `DEBUG` is False. Use for: Phase 2 — the panel is a view on this app, not a second process. Primary source for lesson 0020.
- [Django Debug Toolbar — `RequestPanel`](https://github.com/django-commons/django-debug-toolbar/blob/main/debug_toolbar/panels/request.py)
  Prior art for capturing view name, args, kwargs, url_name after a request. Uses `resolve()` + `get_name_from_obj` (`view_class` if present). Also dumps session (sanitized). Use for: how a shipped tool names a view; P1.3 captures *keys* only, not DDT’s full session values.
- [Django: Authentication in web requests](https://docs.djangoproject.com/en/5.2/topics/auth/default/#authentication-in-web-requests)
  Sessions + middleware hook auth onto the request. `request.user` is `User` or `AnonymousUser`; tell them apart with `is_authenticated`. Use for: P1.3 / lesson 0005 — the diner is not a field the browser posted.
- [Django: `HttpRequest.user` / `HttpRequest.session`](https://docs.djangoproject.com/en/5.2/ref/request-response/#attributes-set-by-middleware)
  Attributes set by middleware: session from `SessionMiddleware`, user from `AuthenticationMiddleware`. Use for: when those attributes exist, and that a missing middleware means a missing attribute.
- [Django: AuthenticationMiddleware](https://docs.djangoproject.com/en/5.2/ref/middleware/#django.contrib.auth.middleware.AuthenticationMiddleware)
  Adds `request.user`. Must run after `SessionMiddleware`. Use for: onion order on the restaurant app’s `MIDDLEWARE` list.
- [Django: AnonymousUser](https://docs.djangoproject.com/en/5.2/ref/contrib/auth/#anonymoususer-object)
  Logged out is still an object: `is_authenticated` is False, `get_username()` is `""`, `id` is `None`. Use for: the “user is None when logged out” trap.
- [MDN: Using HTTP cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
  What a cookie is: a small piece of data the server sends (`Set-Cookie`), the browser stores, and sends back (`Cookie`) on later requests. HTTP is stateless by default. Use for: lesson 0004. Primary source for “ticket number, not a name.”
- [Django: How to use sessions](https://docs.djangoproject.com/en/5.2/topics/http/sessions/)
  `request.session` is dict-like; `keys()` lists slots. “Cookies contain a session ID – not the data itself.” Use for: lesson 0004 (the ticket holds an id); P1.3 session keys (`table_number`, `_auth_user_id`), not dumping values.
- [Django: Database instrumentation](https://docs.djangoproject.com/en/5.2/topics/db/instrumentation/)
  `connection.execute_wrapper`: a context manager that installs a callable around every query. Wrappers are modeled after middleware. Five arguments: `execute`, `sql`, `params`, `many`, `context`. Must call `execute(...)` and return its result. Use for: P1.5 / lesson 0008. Primary source for the SQL probe.
- [Python: The `with` statement](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement)
  Wraps a block with setup and cleanup. Use for: what `with connection.execute_wrapper(...)` is doing. Not a Django keyword.
- [Django FAQ: How can I see the raw SQL queries Django is running?](https://docs.djangoproject.com/en/5.2/faq/models/#how-can-i-see-the-raw-sql-queries-django-is-running)
  `connection.queries` is a list of `{sql, time}` dictionaries — **only when `DEBUG` is True**. Use for: why P1.5 does not read this list.
- [Django: Models](https://docs.djangoproject.com/en/5.2/topics/db/models/)
  “A model is the single, definitive source of information about your data… maps to a single database table.” The Manager `objects` “is used to retrieve the instances from the database.” Use for: lesson 0011 — model vs instance.
- [Django: Making queries — Retrieving objects](https://docs.djangoproject.com/en/5.2/topics/db/queries/#retrieving-objects)
  “A QuerySet represents a collection of objects from your database.” Use for: lesson 0011 — queryset is a search, not a row.
- [DRF: Serializers](https://www.django-rest-framework.org/api-guide/serializers/)
  Convert “querysets and model instances” to native types for JSON; deserialize parsed data “back into complex types, after first validating.” Use for: lesson 0011 — serializer sits between JSON and those objects.
- [DRF: Serializers — Validation](https://www.django-rest-framework.org/api-guide/serializers/#validation)
  `is_valid()` deserializes and validates incoming data; `validated_data` is the dict that exists only after a successful call. Use for: P1.7 / lesson 0010. Primary source for when that dict is legal to read.
- [Python: Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
  “A function definition associates the function name with the function object.” “Other names can also point to that same function object.” Docs example: `f = fib` then `f(100)`. Use for: lesson 0014 — `original_render = Template.render` is this fact.
- [Python: A Word About Names and Objects](https://docs.python.org/3/tutorial/classes.html#a-word-about-names-and-objects)
  “Objects have individuality, and multiple names (in multiple scopes) can be bound to the same object.” “Attributes may be read-only or writable. In the latter case, assignment to attributes is possible.” Use for: `original_render = Template.render` (second name for the same function) and `Template.render = probed_render` (rebind the class attribute).
- [Python: Method objects](https://docs.python.org/3/tutorial/classes.html#method-objects)
  “The instance object is passed as the first argument of the function.” The name `self` “is nothing more than a convention.” Use for: lesson 0012 — why `probed_is_valid` has `self`.
- [Python: Arbitrary Argument Lists](https://docs.python.org/3/tutorial/controlflow.html#arbitrary-argument-lists)
  Extra positional arguments “will be wrapped up in a tuple.” `**name` receives a dict of leftover keyword arguments. Use for: lesson 0012 — `*args` / `**kwargs` on the `is_valid` wrap.
- [DRF: `SlugRelatedField`](https://www.django-rest-framework.org/api-guide/relations/#slugrelatedfield)
  Represents a related object by a field on the target (`slug` here). `queryset` is “used for model instance lookups when validating the field input.” Use for: why `product: "經典原味鍋"` becomes a `menuitem` instance.
- [Django: `render()`](https://docs.djangoproject.com/en/5.2/topics/http/shortcuts/#render)
  “Combines a given template with a given context dictionary and returns an HttpResponse object with that rendered text.” `context` is “A dictionary of values to add to the template context.” The docs show the equivalent: `get_template` then `t.render(c, request)` then `HttpResponse`. Use for: P1.8 / lesson 0013 — what `menuitem_detail` calls, and that the shortcut is not the wrap target (the view already imported that name).
- [Django: `Template.render` (common API)](https://docs.djangoproject.com/en/5.2/topics/templates/#django.template.backends.base.Template.render)
  Objects from `get_template()` “must provide a `render()` method” with signature `render(context=None, request=None)`. “If `context` is provided, it must be a dict.” Use for: P1.8 wrap target. Primary source for lesson 0013.
- [Django: `django.template.backends.django.Template`](https://docs.djangoproject.com/en/5.2/topics/templates/#django.template.backends.django.Template)
  “A thin wrapper adapting django.template.Template to the common template API.” Use for: which class to import; the filename is on the inner compiled template (`self.template.name`).
- [Django: `template_rendered`](https://docs.djangoproject.com/en/5.2/ref/signals/#template-rendered)
  Sent when the *test system* renders a template. “This signal is not emitted during normal operation of a Django server – it is only available during testing.” Use for: why P1.8 does not connect a signal — same class of trap as `connection.queries` needing `DEBUG`.
- [Django Debug Toolbar — `TemplatesPanel`](https://github.com/django-commons/django-debug-toolbar/blob/main/debug_toolbar/panels/templates/panel.py)
  Prior art: monkeypatches `Template._render` so the test-only `template_rendered` signal fires in development, then listens. Use for: a shipped tool also wraps render rather than reading the response HTML; P1.8 wraps the common-API `render` instead, so the copied dict is the one the view passed.
- [D7 — `kind` and `label`](DECISIONS.md)
  First-party: the panel reads only `kind`; adapters write `label`. Closed, agreed, stable, nearest-fit. Use for: P1.9 reshape. Primary source for lesson 0016.
- [FastAPI](https://fastapi.tiangolo.com/)
  Official: “a modern, fast (high-performance), web framework for building APIs with Python.” Use for: what the name in D7 / P6.4 / lesson 0016 refers to. Not a Phase 1 install. Not the restaurant app.
- [OpenTelemetry: Traces](https://opentelemetry.io/docs/concepts/signals/traces/)
  “The path of a request through your application.” A span is “a unit of work or operation… the building blocks of Traces.” Root span = `trace_id` with no `parent_id`. Attributes are scalars or arrays of scalars — no dicts. Use for: lesson 0017. Primary source for what D5 borrowed and why P0.4a needed the encoder.
- [OpenTelemetry: Observability primer](https://opentelemetry.io/docs/concepts/observability-primer/)
  “A trace is made of one or more spans. The first span represents the root span.” Use for: the plainest statement of trace-vs-span before the spec.
- [OpenTelemetry: Trace API — `Span` and `SpanKind`](https://opentelemetry.io/docs/specs/otel/trace/api/#spankind)
  Span name “SHOULD be the most general string that identifies a (statistically) interesting class of Spans” — `get_user` good, `get_user/314159` bad (cardinality). `SpanKind` is five values describing call direction and communication style; `INTERNAL` is “operations which do not cross a process boundary.” Use for: why neither the name nor `SpanKind` can replace our `kind` (D7).
- [Roadmap — stage vocabulary, v0](ROADMAP.md)
  The fourteen `kind` strings. Server half used in P1.9; client kinds wait for Phase 4. Use for: which string to write on each stage.
- [Python tutorial: Saving structured data with json](https://docs.python.org/3/tutorial/inputoutput.html#saving-structured-data-with-json)
  `dumps` → a string; `dump` → a text file. “This process is called serializing.” JSON files must be UTF-8. Use for: P1.9 file write (next lesson). They already know `dumps` (LR-0012).
- [Python: `json.dump`](https://docs.python.org/3/library/json.html#json.dump)
  “Serialize obj as a JSON formatted stream to fp.” Same flags as `dumps` (`ensure_ascii=False`, `default`). Use for: the call that replaces `print(json.dumps(...))`.

- [LSP: What is the Language Server Protocol?](https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/)
  The M×N problem in its own words: support "must be repeated for each development tool, as each provides different APIs for implementing the same features," so LSP standardises the protocol and "a single Language Server can be re-used in multiple development tools." Also the deeper design lesson: LSP standardises *simple neutral* types (document URI, cursor position) and deliberately not "an abstract syntax tree and compiler symbols." Use for: why the Trace standardises `kind` + `{type, value}` rather than Django's object model.
- [LSP 3.17 specification — Document Symbols Request](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_documentSymbol)
  The real prior art for D7. On that page: [`DocumentSymbol`](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#documentSymbol) carries `name` ("displayed in the user interface") *and* `kind: SymbolKind` — our `label`/`kind` pair; [`SymbolKind`](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#symbolKind) is 26 integers with `Class = 5`. Clients declaring supported kinds must "handle values outside its set gracefully and fall back to a default value when unknown." Flat [`SymbolInformation`](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#symbolInformation) is deprecated in favour of the hierarchical `DocumentSymbol[]`, which supports D5. Use for: the kind/label idea, and the panel's unknown-kind rule (P2.2). Always-current version: [specification-current](https://microsoft.github.io/language-server-protocol/specifications/specification-current/).
- [DRF source — `Request.user` setter](https://github.com/encode/django-rest-framework/blob/master/rest_framework/request.py)
  The setter's own docstring: “we also set the user on Django's underlying `HttpRequest` instance, ensuring that it is available to any middleware in the stack.” Use for: why `attach_context` reported `is_authenticated: false` on a DRF view whose session still held `_auth_user_id` — `authentication_classes = []` makes DRF assign `AnonymousUser` and write it through. Read the copy in the target project's venv, not from memory.
- [Django: Middleware — Exception handling](https://docs.djangoproject.com/en/5.2/topics/http/middleware/#exception-handling)
  The paragraph that settles where a guard goes. Django converts exceptions from the view and inner middleware into responses *between* each layer, so “every middleware can always rely on getting some kind of HTTP response back from calling its `get_response` callable. Middleware don't need to worry about wrapping their call to `get_response` in a `try/except`.” And the other direction: “an exception raised from a middleware will immediately be converted to the appropriate HTTP response.” Use for: P1.10 / lesson 0019 — why you never guard `get_response`, and why our own `AttributeError` became a 500. Primary source; it corrects the intuition that a wide `try` would swallow the app's errors.
- [Django: Middleware — Dealing with streaming responses](https://docs.djangoproject.com/en/5.2/topics/http/middleware/#dealing-with-streaming-responses)
  “Unlike `HttpResponse`, `StreamingHttpResponse` does not have a `content` attribute. As a result, middleware can no longer assume that all responses will have a `content` attribute. If they need access to the content, they must test for streaming responses and adjust their behavior accordingly” — shown as `if response.streaming: … else: …`. Also: `streaming_content` “should be assumed to be too large to hold in memory. Response middleware may wrap it in a new generator, but must not consume it.” Use for: P1.10 — the exact branch P1.6 was missing. Note the docs show the branch for *altering* content; we take the skip branch instead.
- [Django: `FileResponse`](https://docs.djangoproject.com/en/5.2/ref/request-response/#django.http.FileResponse)
  A subclass of `StreamingHttpResponse`. Use for: what `django.views.static.serve` returns — verified in the target project's venv at `django/views/static.py`, which ends `response = FileResponse(fullpath.open("rb"), …)`. Because the restaurant project's root `urls.py` does `urlpatterns += static(settings.MEDIA_URL, …)`, every `/media/` request is an ordinary route and reaches our middleware. `/static/` does not: `runserver`'s `StaticFilesHandler.__call__` intercepts it before the middleware chain (`django/contrib/staticfiles/handlers.py`).
- [Python: `Exception` and `BaseException`](https://docs.python.org/3/library/exceptions.html#Exception)
  “All built-in, non-system-exiting exceptions are derived from this class.” `KeyboardInterrupt` and `SystemExit` derive from `BaseException` instead. Use for: P1.10 — `except Exception`, never a bare `except:`, in code that runs on every request; a bare one eats Ctrl-C on `runserver`.
- [Django: Exceptions reference](https://docs.djangoproject.com/en/5.2/ref/exceptions/) · [`DATA_UPLOAD_MAX_MEMORY_SIZE`](https://docs.djangoproject.com/en/5.2/ref/settings/#data-upload-max-memory-size)
  `RequestDataTooBig` is a subclass of `SuspiciousOperation`, and a `SuspiciousOperation` reaching the WSGI handler “results in a `HttpResponseBadRequest`”. `UnreadablePostError` “is raised when a user cancels an upload.” Use for: P1.10 — why the `request.body` read needs `except Exception` and not only `UnicodeDecodeError`. Confirmed in the venv: `HttpRequest.body` calls `_check_data_too_big` before reading, and raises `RawPostDataException` if the stream was already consumed. Relevant to this project because `menuitem.image` is an `ImageField`.
- [Sentry SDK source — `capture_internal_exceptions`](https://github.com/getsentry/sentry-python/blob/master/sentry_sdk/utils.py)
  Prior art for the whole of P1.10, in about twenty lines. `CaptureInternalException.__exit__` returns `True` (Python's signal to suppress) and hands the exception to `capture_internal_exception`, whose docstring is “Capture an exception that is likely caused by a bug in the SDK itself. These exceptions do not end up in Sentry and are just logged instead.” Use for: lesson 0019 — a shipped instrumentation library swallows from the host app *and* records for the tool's author. Both halves; the second is what keeps a silent probe failure from reading as an observed absence.

## Wisdom (Communities)

- [Django Forum — Using Django](https://forum.djangoproject.com/c/users/6)
  Official, moderated. Use for: middleware timing questions that the docs left ambiguous on your project.
- [Django Discord](https://docs.djangoproject.com/en/5.2/faq/help/)
  Official chat, linked from Django's own "Getting help" FAQ. Use for: short "is resolver_match set yet?" checks.

## Gaps

- Django's docs state that `resolver_match` is unavailable in middleware *before* resolving, and name `process_view()` as the hook. They do not spell out the equally valid read *after* `get_response` returns — which is the smallest change to the P1.1 middleware. That mapping is in the lesson, cited back to the onion diagram in the middleware docs.
- Django’s “Activating middleware” paragraph says AuthenticationMiddleware “stores the authenticated user in the session.” The inward-pass fact is the reverse direction of that sentence: Auth *reads* `request.session` (which SessionMiddleware just set) and *sets* `request.user`. The ordering page is the clearer line: “After SessionMiddleware: uses session storage.” Lesson 0006 uses both, with the waiter walk showing the read.
- Django’s docs name `request.user` as `User` or `AnonymousUser`. They do not say that `AuthenticationMiddleware` assigns a `SimpleLazyObject` first. That wrapper is in Django’s source (`django.contrib.auth.middleware`). Lesson 0005 puts it in a gloss, not the running sentence.
- Django’s instrumentation page shows `execute_wrapper` as a local context manager around “some flow in your code.” It does not show installing it in middleware around `get_response`. That mapping is in lesson 0008: SQL from inner middleware and the view runs inside that call, so the wrapper has to wrap it, not sit after it.
- Django’s HttpResponse page names the pockets (`status_code`, `headers`, `content`) but does not show reading them in `__call__` middleware after `get_response` returns. That mapping is in lesson 0009: the return value is a new object; the request is still the ticket.
- DRF’s validation page shows `validated_data` after `is_valid()` on a serializer you constructed yourself. It does not show replacing `Serializer.is_valid` from middleware. That mapping is in lesson 0010: the serializer instance lives inside `get_response`, so the wrap has to be on during that call, the same timing as `execute_wrapper`.
- DRF’s `SlugRelatedField` page says the queryset is used for model instance lookups. It does not walk a real `POST /api/cart/item/` body field-by-field. Lesson 0010 does that on `cartitemSerializer` (`product`, `meattype`, `hotpotingredients`).
- Django’s shortcut page shows `render()` and the `get_template` / `t.render(context, request)` equivalent. It does not show replacing `Template.render` from middleware, or that replacing `django.shortcuts.render` is a no-op once the view has imported it. That mapping is in lesson 0013.
- Django documents `template_rendered` as test-only. Debug Toolbar re-enables it by patching `_render`. Lesson 0013 skips the signal and wraps the common-API `render`, so the copied context is the view’s dict (no `user` / `csrf_token` from context processors).
- Nothing in Django or DRF names `kind`. The mapping from `captured` keys to the closed list is first-party (D7 + the P0.4 table). Lesson 0016 is that mapping; an empty probe list means omit the stage.
- OTel defines a span as a timed unit of work, names it with disciplined free text, and classifies it with a five-value `SpanKind` about messaging role. It has **no field** for “which job in the request lifecycle is this” — every Phase 1 Django stage would be `INTERNAL`. That gap is what `kind` fills, and the argument is first-party (D7). Lesson 0017 makes it from OTel's own definitions.
- Django's “Dealing with streaming responses” shows the `response.streaming` branch for middleware that wants to **alter** the body. It does not describe the case where middleware only wants to *read* the body and should skip it entirely — nor what to record in place of a byte count it declined to take. That mapping is in lesson 0019: `None`, not `0`, because `0` asserts a measurement we did not make.
- Django's middleware docs say a guard around `get_response` is unnecessary, and its exception-handling paragraph says a middleware's own exception becomes an HTTP response. Neither page says anything about guarding a middleware's *own* capture code, which is the entire subject of P1.10. The rule (call the original outside the guard, guard only the bookkeeping) is first-party, argued in lesson 0019 from those two facts plus the Sentry SDK's implementation.
- Nothing in Django or Python says what to write when a probe fails. That a swallowed failure needs a mark is first-party and follows from D7 + lesson 0016: an absent stage already means “did not happen”, so a silent failure would make the panel state a fact nothing observed (D2). Hence `capture_errors` on the Trace. Sentry's logger is the prior art for the shape, not for the schema.
- CONTEXT defines Panel as the page at `/__supervisualizer__/` and also says it “Receives finished Traces over SSE.” SSE is Phase 3. Phase 2’s reader is an ordinary GET that opens a file. That split is in lesson 0020; D3 is the decision that the page is a view on this app.
- Django’s `include()` page states the chop. It does not say that a 404 on an unmounted prefix is unrelated to whether a Trace file exists. That mapping is in lesson 0021. It also does not warn that toggling `DEBUG` to False with empty `ALLOWED_HOSTS` rejects the host before URL resolving — that trap is a sidenote in the same lesson.
