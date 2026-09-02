# A method is a function object on the class

They asked how `Template.render` can be stored in `original_render` and then replaced. Floor: Python binds names to objects; `Template.render` is a function on the class, same as `Serializer.is_valid`. First line keeps a second name for the real function; second line points the class attribute at `probed_render`. Docs: names-and-objects + method objects (`xf = x.f`).
