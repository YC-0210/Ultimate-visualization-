"""Spike P0.4a, part 2 — the integration question.

Part 1 proved values can ride on spans we create ourselves. The real
question is whether a probe buried inside DRF can attach a child span to
the request span Django's instrumentation made, without threading any
context by hand. If that works, OTel is carrying real weight. If it does
not, we are only borrowing the shape.

Also: do DB spans come free, and what does the instrumentation cost?
"""
import json, os, sys, tempfile, time

TARGET = os.environ.get("TARGET_REPO", "/home/user/yc-0210/restautant-order-system")
sys.path.insert(0, TARGET)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurant.settings")

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor

FINISHED = []
class Collector(SpanProcessor):
    def on_start(self, span, parent_context=None): pass
    def on_end(self, span): FINISHED.append(span)
    def shutdown(self): pass
    def force_flush(self, t=30000): return True

provider = TracerProvider()
provider.add_span_processor(Collector())
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("supervisualizer.spike")

import django
django.setup()
from django.conf import settings
_db = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
settings.DATABASES["default"]["NAME"] = _db.name
from django.core.management import call_command
call_command("migrate", run_syncdb=True, verbosity=0)

from opentelemetry.instrumentation.django import DjangoInstrumentor
DjangoInstrumentor().instrument()

# do DB spans come free?
DB_INSTRUMENTED = False
try:
    from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
    SQLite3Instrumentor().instrument()
    DB_INSTRUMENTED = True
except Exception as e:
    DB_ERR = repr(e)

from django.test.utils import setup_test_environment
setup_test_environment()

from restaurantAPI.models import menuitem, meattype, hotpotingredients
from restaurantAPI import serializers as ser_module

prod = menuitem.objects.create(slug="classic-original", product="經典原味鍋", price="200.00")
meat = meattype.objects.create(slug="beef-short-plate", name="霜降牛", addon_price="40.00")
top  = hotpotingredients.objects.create(slug="squid", name="九層花枝", addon_price="40.00")


def encode(v, d=0):
    if v is None or isinstance(v, (str, int, float, bool)):
        return {"type": type(v).__name__, "value": v}
    if d > 6: return {"type": type(v).__name__, "value": str(v)[:120]}
    if isinstance(v, (list, tuple, set)):
        return {"type": "list", "value": [encode(x, d+1) for x in list(v)[:20]]}
    if isinstance(v, dict):
        return {"type": "dict", "value": {str(k): encode(x, d+1) for k, x in v.items()}}
    if hasattr(v, "pk") and hasattr(v, "_meta"):
        return {"type": f"{type(v).__name__} instance", "value": f"<{type(v).__name__}: {v}> pk={v.pk}"}
    return {"type": type(v).__name__, "value": str(v)[:200]}


# ---- THE PROBE: monkeypatch DRF, create a child span from deep inside ----
_orig_is_valid = ser_module.serializers.Serializer.is_valid
_orig_save = ser_module.serializers.BaseSerializer.save

def probed_is_valid(self, *a, **kw):
    with tracer.start_as_current_span("validate_input") as sp:
        sp.set_attribute("sv.kind", "validate_input")
        sp.set_attribute("sv.label", f"{type(self).__name__}")
        result = _orig_is_valid(self, *a, **kw)
        try:
            sp.set_attribute("sv.data", json.dumps(encode(dict(self.validated_data)), ensure_ascii=False))
        except Exception as e:
            sp.set_attribute("sv.encode_error", repr(e))
        return result

def probed_save(self, **kw):
    with tracer.start_as_current_span("mutate_data") as sp:
        sp.set_attribute("sv.kind", "mutate_data")
        sp.set_attribute("sv.label", f"{type(self).__name__}.save()")
        obj = _orig_save(self, **kw)
        sp.set_attribute("sv.data", json.dumps(encode({"pk": obj.pk, "price": getattr(obj, "price", None)}), ensure_ascii=False))
        return obj

ser_module.serializers.Serializer.is_valid = probed_is_valid
ser_module.serializers.BaseSerializer.save = probed_save

# ---- fire a REAL request through the whole stack ----
from django.test import Client
c = Client()
_s = c.session
_s["table_number"] = 7
_s.save()
FINISHED.clear()
resp = c.post("/api/cart/item/", data=json.dumps({
    "product": prod.slug, "meattype": meat.slug, "hotpotingredients": [top.slug],
    "doublemeat": True, "quantity": 2, "notes": "少辣不要蔥",
}), content_type="application/json")

print("=" * 74)
print(f"POST /api/cart/item/ -> {resp.status_code}")
print(f"DB instrumentation available: {DB_INSTRUMENTED}")
print("=" * 74)

# ---- did the probe spans nest under Django's request span? ----
by_id = {sp.context.span_id: sp for sp in FINISHED}
roots = [sp for sp in FINISHED if sp.parent is None or sp.parent.span_id not in by_id]
kinds = {}
for sp in FINISHED:
    kinds.setdefault(sp.name, 0)
    kinds[sp.name] += 1

db_spans = [s for s in FINISHED if "db.statement" in (s.attributes or {})
            or s.name.lower().startswith(("select", "insert", "update", "delete"))]
print(f"\nDB spans captured by SQLite3Instrumentor: {len(db_spans)}")
if not db_spans:
    print("  => NONE. Django's ORM goes through its own connection wrapper,")
    print("     so sqlite3 instrumentation does not see ORM queries.")

print(f"\nspans captured: {len(FINISHED)}")
print(f"distinct trace_ids: {len({sp.context.trace_id for sp in FINISHED})}")
print(f"root spans: {[r.name for r in roots]}")
print(f"\nspan counts by name:")
for n, ct in sorted(kinds.items(), key=lambda x: -x[1]):
    print(f"   {ct:3}  {n}")

def show(sp, depth=0):
    a = dict(sp.attributes or {})
    tag = a.get("sv.kind", "")
    data = a.get("sv.data")
    extra = f"  [sv.kind={tag}]" if tag else ""
    size = f"  data={len(data)}ch" if data else ""
    print("   " + "  " * depth + f"- {sp.name}{extra}{size}")
    for ch in FINISHED:
        if ch.parent and ch.parent.span_id == sp.context.span_id:
            show(ch, depth + 1)

print("\ntree:")
for r in roots:
    show(r)

probe_spans = [s for s in FINISHED if (s.attributes or {}).get("sv.kind")]
nested = [s for s in probe_spans if s.parent and s.parent.span_id in by_id]
print(f"\nprobe spans created: {len(probe_spans)}")
print(f"of those, correctly parented inside another captured span: {len(nested)}")
print(f"=> context propagation across the framework boundary: "
      f"{'WORKS' if len(nested) == len(probe_spans) and probe_spans else 'FAILED'}")

# ---- overhead ----
print("\n" + "=" * 74)
print("overhead")
print("=" * 74)
def bench(n=40):
    t = time.perf_counter()
    for _ in range(n):
        c.get(f"/api/menuitem/{prod.slug}/")
    return (time.perf_counter() - t) / n * 1000

FINISHED.clear(); on = bench()
DjangoInstrumentor().uninstrument()
ser_module.serializers.Serializer.is_valid = _orig_is_valid
ser_module.serializers.BaseSerializer.save = _orig_save
FINISHED.clear(); off = bench()
print(f"  instrumented:   {on:.2f} ms/request")
print(f"  uninstrumented: {off:.2f} ms/request")
print(f"  delta:          {on-off:+.2f} ms  ({(on/off-1)*100:+.0f}%)")
