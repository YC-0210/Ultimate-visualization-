Altitude: mechanical

# Template.render is assigned probed_render

They stated the assignment correctly: the class attribute `Template.render` is pointed at their function `probed_render`. Floor: the name is `Template.render` (dot), not `template_render`. `original_render` still holds Django’s function.
