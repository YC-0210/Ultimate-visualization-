Altitude: structural

# The stage conditions answer two different questions

They read the five conditions in `stages` as noise and asked why there are so many. Established: `if validations:` / `if renders:` answer "did this stage happen?" (CONTEXT's rule that stages are a property of the endpoint), while `if "route" in captured:`, the session/user check and the view-class extras loop answer "was this fact capturable at all?" — defensive against a 404, a differently-configured settings file, or a function view. Root cause named: one `__call__` serves every request shape the app can receive, and no single request carries every fact. Flagged for P1.10 that a guard and a `try`/`except` are not substitutes — the guard omits one stage and still writes a correct Trace, the `try`/`except` drops the whole Trace. Also noted the repetition (six near-identical dict literals) is reducible to a table plus a loop, but advised against refactoring code run only twice.
