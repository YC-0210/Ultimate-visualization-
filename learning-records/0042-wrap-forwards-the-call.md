# Probe wrap does not need the callee’s argument list

They thought they had to know `Serializer.is_valid`’s types before writing `original_is_valid(self, *args, **kwargs)`. The gap is the wrap rule: a probe forwards whatever the real caller already passed. Docs for `is_valid` give the job and `True`/`False`, not that forwarding pattern.
