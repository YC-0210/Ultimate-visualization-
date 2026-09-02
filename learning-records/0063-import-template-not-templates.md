# Import Template, not Templates

The server failed because `from django.template.backends.django import Templates` is not a name Django exports. The wrap target is the class `Template` — the object `get_template()` returns. Floor: `Template.render` is the class attribute; `DjangoTemplates` is the engine.
