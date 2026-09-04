Altitude: mechanical

# Wrapper docs: understand/control, blocker is one example

They read Django’s database-instrumentation page: wrappers exist to understand and control queries, and one documented use is blocking queries while a view renders a template. That reading is right. The remaining map is that P1.5 uses the other example on that page (log/copy), installed around `get_response`, not a blocker around `render()`.
