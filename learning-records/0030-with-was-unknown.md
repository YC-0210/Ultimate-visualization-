# `with` was unknown

They did not know Python’s `with` statement. Treat it as new: setup, indented block, automatic cleanup. Do not assume `try`/`finally` or `__enter__`/`__exit__` as known names unless taught. P1.5’s `with connection.execute_wrapper(...)` is this, not a Django-only keyword.
