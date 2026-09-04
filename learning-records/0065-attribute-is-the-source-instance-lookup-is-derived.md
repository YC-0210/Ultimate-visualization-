Altitude: structural

# The class attribute is the source; t.render is derived from it

Their P1.8 walkthrough was right on purpose, timing, `encode`, and `args[0]` being the view's dict. Two floors: they said `Template.render` "originally points at the `t.render` function" — the direction is backwards (0058 again). `Template.render` is the class attribute holding Django's function object; `t.render` is not stored anywhere, it is produced on each instance lookup from that attribute with `t` packed in. Second: they called `original_render` "merely a `class.function`" — the function object is one object with two names (`Template.render`, `original_render`), which is why `finally` can restore it.
