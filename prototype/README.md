# Prototype — throwaway

This is throwaway code for a quick prototype, not the real product (see `CONTEXT.md` at the repo root for what "the real product" would even mean here).

`extract_snapshot.py` runs the real `restautant-order-system` Django project (via `django.setup()` and DRF's own reflection) against a throwaway sqlite database, and dumps `snapshot.json`: the Structure Map (models/serializers/endpoints) plus a real Flow Trace for each of the three Focus Endpoints, captured by actually executing them against sample data.

To reproduce:

```bash
python3.12 -m venv /tmp/venv
/tmp/venv/bin/pip install -r /path/to/restautant-order-system/requirements.txt
TARGET_REPO=/path/to/restautant-order-system /tmp/venv/bin/python extract_snapshot.py > snapshot.json
```

`snapshot.json` is checked in so the visualization artifact doesn't need this script to run to be viewed — re-run the script and re-publish the artifact to refresh it after the target project's code changes.
