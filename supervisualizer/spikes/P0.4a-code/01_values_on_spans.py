"""
Spike P0.4a — can OpenTelemetry carry supervisualizer's values?

THROWAWAY. Answers four unknowns against the real restautant-order-system:
  U1 real values survive an encoder
  U2 what a real Django request produces
  U3 one span vs a span per stage
  U4 what OTel is still buying us
"""
import json
import os
import sys
import tempfile

TARGET = os.environ.get("TARGET_REPO", "/home/user/yc-0210/restautant-order-system")
sys.path.insert(0, TARGET)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurant.settings")

# ---- OTel first, before django.setup(), so instrumentation can patch ----
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from opentelemetry.trace import Status, StatusCode

FINISHED = []


class Collector(SpanProcessor):
    """The in-process reader D6 assumes. No exporter, no collector, no network."""
    def on_start(self, span, parent_context=None):
        pass

    def on_end(self, span):
        FINISHED.append(span)

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis=30000):
        return True


provider = TracerProvider()
provider.add_span_processor(Collector())
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("supervisualizer.spike")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402

_db = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
settings.DATABASES["default"]["NAME"] = _db.name

from django.core.management import call_command  # noqa: E402

call_command("migrate", run_syncdb=True, verbosity=0)

from opentelemetry.instrumentation.django import DjangoInstrumentor  # noqa: E402

DjangoInstrumentor().instrument()

from django.test.utils import setup_test_environment  # noqa: E402

setup_test_environment()

from restaurantAPI.models import menuitem, meattype, hotpotingredients, cart, cartitem  # noqa: E402
from restaurantAPI import serializers as ser_module  # noqa: E402

# --------------------------------------------------------------- U1: encoder
def encode(value, depth=0):
    """Arbitrary Python object -> {type, value}, JSON-safe. Ported from the
    prototype's jsonable(). This is the thing OTel cannot hold natively."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return {"type": type(value).__name__, "value": value}
    if depth > 6:
        return {"type": type(value).__name__, "value": str(value)[:120]}
    if isinstance(value, (list, tuple, set)):
        return {"type": "list", "value": [encode(v, depth + 1) for v in list(value)[:20]]}
    if isinstance(value, dict):
        return {"type": "dict", "value": {str(k): encode(v, depth + 1) for k, v in value.items()}}
    if hasattr(value, "pk") and hasattr(value, "_meta"):
        return {
            "type": f"{type(value).__name__} instance",
            "value": f"<{type(value).__name__}: {value}> pk={value.pk}",
            "fields": {f.name: str(getattr(value, f.name, None))[:60]
                       for f in value._meta.fields[:8]},
        }
    return {"type": type(value).__name__, "value": str(value)[:200]}


# --------------------------------------------------------------- seed
prod = menuitem.objects.create(slug="classic-original", product="經典原味鍋", price="200.00")
meat = meattype.objects.create(slug="beef-short-plate", name="霜降牛", addon_price="40.00")
top = hotpotingredients.objects.create(slug="squid", name="九層花枝", addon_price="40.00")

from django.test import RequestFactory  # noqa: E402
from django.contrib.sessions.middleware import SessionMiddleware  # noqa: E402
from django.contrib.auth.models import AnonymousUser  # noqa: E402

req = RequestFactory().post("/api/cart/item/")
SessionMiddleware(lambda r: None).process_request(req)
req.session.save()
req.session["table_number"] = 7
req.user = AnonymousUser()

payload = {
    "product": prod.slug, "meattype": meat.slug, "hotpotingredients": [top.slug],
    "doublemeat": True, "quantity": 2, "notes": "少辣不要蔥",
}

print("=" * 72)
print("U1 / U3 — run the real serializer inside spans")
print("=" * 72)

# --------------------------------------------------- U3: a span per stage
with tracer.start_as_current_span("http.request") as root:
    root.set_attribute("sv.kind", "receive_input")
    root.set_attribute("sv.label", "HTTP Request")

    with tracer.start_as_current_span("validate_input") as vspan:
        vspan.set_attribute("sv.kind", "validate_input")
        vspan.set_attribute("sv.label", "Serializer (in)")

        s = ser_module.cartitemSerializer(data=payload, context={"request": req})
        ok = s.is_valid()
        validated = dict(s.validated_data)

        # THE test: can this ride on a span?
        encoded = encode(validated)
        vspan.set_attribute("sv.data", json.dumps(encoded, ensure_ascii=False))

        # and the control: raw, as a naive implementer would try
        vspan.set_attribute("sv.data_raw", validated)

        with tracer.start_as_current_span("mutate_data") as mspan:
            mspan.set_attribute("sv.kind", "mutate_data")
            mspan.set_attribute("sv.label", "create()")
            item = s.save()
            mspan.set_attribute("sv.data", json.dumps(
                encode({"price": item.price, "cart_total": item.cart.total_price}),
                ensure_ascii=False))

    with tracer.start_as_current_span("render_output") as rspan:
        rspan.set_attribute("sv.kind", "render_output")
        rspan.set_attribute("sv.label", "Serializer (out)")
        out = dict(ser_module.cartitemSerializer(item).data)
        rspan.set_attribute("sv.data", json.dumps(encode(out), ensure_ascii=False))
    root.set_status(Status(StatusCode.OK))

print(f"serializer valid: {ok}   price computed: {item.price}   cart: {item.cart.total_price}")
print()

# --------------------------------------------------------------- inspect
print("=" * 72)
print("What actually survived onto the spans")
print("=" * 72)
by_name = {}
for sp in FINISHED:
    by_name[sp.name] = sp
    attrs = dict(sp.attributes or {})
    parent = sp.parent.span_id if sp.parent else None
    print(f"\n  span {sp.name!r}")
    print(f"    trace_id  {sp.context.trace_id:032x}")
    print(f"    span_id   {sp.context.span_id:016x}  parent {parent and format(parent,'016x')}")
    print(f"    attrs     {sorted(attrs.keys())}")
    if "sv.data_raw" in attrs:
        print("    !! sv.data_raw SURVIVED (unexpected)")
    else:
        if sp.name == "validate_input":
            print("    -- sv.data_raw ABSENT (silently dropped, as predicted)")

# --------------------------------------------------------------- round trip
print()
print("=" * 72)
print("U1 — does it round-trip field by field?")
print("=" * 72)
v = by_name["validate_input"]
back = json.loads(dict(v.attributes)["sv.data"])
originals = {
    "product": prod, "meattype": meat, "quantity": 2,
    "doublemeat": True, "notes": "少辣不要蔥",
}
allok = True
for key, node in back["value"].items():
    print(f"  {key:20} type={node['type']:28} value={str(node['value'])[:44]}")
for key in ("product", "meattype", "hotpotingredients", "quantity", "doublemeat", "notes"):
    if key not in back["value"]:
        print(f"  MISSING {key}")
        allok = False
print(f"\n  all expected keys present: {allok}")
print(f"  model instance preserved as: {back['value']['product']['type']}")
print(f"  its fields captured:        {list(back['value']['product'].get('fields', {}))[:5]}")
print(f"  encoded blob size:          {len(dict(v.attributes)['sv.data'])} chars")

# --------------------------------------------------------------- U2
print()
print("=" * 72)
print("U2 — what does the real Django instrumentation give us?")
print("=" * 72)
FINISHED.clear()
from django.test import Client  # noqa: E402
c = Client()
resp = c.get(f"/api/menuitem/{prod.slug}/")
print(f"  GET /api/menuitem/{prod.slug}/ -> {resp.status_code}")
print(f"  spans produced by DjangoInstrumentor: {len(FINISHED)}")
for sp in FINISHED:
    a = dict(sp.attributes or {})
    interesting = {k: a[k] for k in a if k.startswith(("http.", "url.", "django"))}
    print(f"    {sp.name!r}")
    print(f"      {interesting}")
print()
print("  NOTE: DB spans require SQLite3Instrumentor separately; Django's")
print("  instrumentation covers the request/view boundary only.")
