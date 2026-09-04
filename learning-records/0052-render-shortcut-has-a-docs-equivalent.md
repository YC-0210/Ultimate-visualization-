Altitude: mechanical

# shortcuts.render expands to get_template + Template.render

They asked what “shortcut” means and for a docs page. Floor: Django’s `render()` page shows the equivalent — `loader.get_template(...)` then `t.render(context, request)` then `HttpResponse(...)`. That `t.render` is `Template.render`. The view still writes the shortcut; we wrap the method inside it.
