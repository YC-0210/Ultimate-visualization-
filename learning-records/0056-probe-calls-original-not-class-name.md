Altitude: mechanical

# probed_render calls original_render, not Template.render

They had the save (`original_render = Template.render`) right, then said probed_render points back at `Template.render`. Floor: after `Template.render = probed_render`, that class name *is* `probed_render`. Calling `Template.render` inside the probe would recurse. The real function is only reachable as `original_render`.
