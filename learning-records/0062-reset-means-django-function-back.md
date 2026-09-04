Altitude: mechanical

# Restore so the next request does not see the previous probe

They restated the finally reason correctly: reset the class attribute so the next request does not get the previous `probed_render`. Floor: “reset” means `Template.render = original_render` — Django’s function back on the attribute.
