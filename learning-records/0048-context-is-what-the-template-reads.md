Altitude: mechanical

# Context is the Python objects the template reads

They stated P1.8 correctly: the view passes live objects into `render` so the template can look them up as variables (`{{ item.product }}`). Floor: that dict is the whole context, not only the one `menuitem` instance — `meats` / `ingredients` are querysets in the same call.
