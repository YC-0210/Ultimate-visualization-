# Teaching notes

## Preferences

- **Logic over syntax.** Coding syntax is not what matters. Teach why the system behaves this way, when a fact exists on the request, and how the pieces actually collaborate. Do not dwell on punctuation, naming style, or "the Pythonic way" unless it changes the behaviour we are observing.
- User asked to be *taught* P1.2, not to have it written for them. Do not implement capture of `resolver_match` in `middleware.py` until they have done the practice.

## Workspace

- Teaching files live at the **repository root**, not inside `supervisualizer/`. That folder is the installable package other people will `pip install`.
- Target app: `hotpot-restaurant-ordering-system` (`-/restaurant/`). Middleware is already installed at the top of `MIDDLEWARE`.
- They build by hand. Prototype (`prototype/extract_all.py`) is ideas-only; its `match.func.cls` is a DRF extra, not Django's documented `view_class`.
- P1.1 is done in code (method, path, headers, body printed as JSON). Next action is P1.2.
