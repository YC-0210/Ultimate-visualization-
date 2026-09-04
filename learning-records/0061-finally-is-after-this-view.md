Altitude: mechanical

# finally restores after this request’s view already ran

They had “in the end the class attribute is Django’s function again” right. One timing correction: this request’s view already ran *inside* `try`, through `probed_render` (which calls `original_render`). `finally` does not switch the view back mid-request. It puts Django’s function on the attribute so the *next* lookup is not still wrapped.
