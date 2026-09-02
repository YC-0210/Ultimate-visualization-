# Template.render is the class function object

They stated: `Template` is the class, `Template.render` is the function object, `original_render` is another name for that same object. Yes. One precision: `Template.render` is a class attribute, `original_render` is a local in `__call__` — two names, not two locals.
