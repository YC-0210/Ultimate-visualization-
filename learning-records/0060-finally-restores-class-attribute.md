# finally puts Django’s function back on Template.render

They asked what `Template.render = original_render` is. Floor: that line belongs in `finally`, not `try`. It undoes `Template.render = probed_render` — the class attribute holds Django’s function again. Same restore they already have for `Serializer.is_valid`. Leave the probe on and the next request nests another wrap.
