"""
PROTOTYPE, throwaway script. Not part of the real product.

Records the real request pipeline for POST /api/cart/item/ in the
restautant-order-system Django project, so the visualization can replay a
genuine server-side trace for whatever the user selects on the replica page.

What is real here:
  - URL resolution comes from django.urls.resolve() against the real urlconf.
  - validated_data, the computed price, and the response body come from
    actually running the real cartitemSerializer against a throwaway sqlite DB.
  - The SQL is captured from the real queries those calls emitted.
  - Code excerpts are sliced out of the real source files.

What is seeded: the menu rows themselves. The target project ships an empty
database, so menuitem/meattype/hotpotingredients fixtures are created here to
match the prices visible in the user's screenshots.

Usage:
    TARGET_REPO=/path/to/restautant-order-system python extract_pipeline.py > pipeline.json
"""
import itertools
import json
import os
import sys
import tempfile

TARGET_REPO = os.environ.get("TARGET_REPO", "/home/user/yc-0210/restautant-order-system")
sys.path.insert(0, TARGET_REPO)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurant.settings")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402

_tmp_db = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
settings.DATABASES["default"]["NAME"] = _tmp_db.name

from django.core.management import call_command  # noqa: E402

call_command("migrate", run_syncdb=True, verbosity=0)

from django.test.utils import setup_test_environment  # noqa: E402

setup_test_environment()

from django.db import connection  # noqa: E402
from django.test import RequestFactory  # noqa: E402
from django.test.utils import CaptureQueriesContext  # noqa: E402
from django.contrib.sessions.middleware import SessionMiddleware  # noqa: E402
from django.contrib.auth.models import AnonymousUser  # noqa: E402
from django.urls import resolve  # noqa: E402

from restaurantAPI.models import (  # noqa: E402
    menuitem,
    meattype,
    hotpotingredients,
    cart,
    cartitem,
)
from restaurantAPI import serializers as ser_module  # noqa: E402

# ---------------------------------------------------------------- seed data
# Prices below match the user's screenshots: base 200, each topping +40,
# double meat +80. Meat types are invented (their DB ships empty).
PRODUCT = menuitem.objects.create(
    slug="classic-original", product="經典原味鍋", price="200.00"
)
MEATS = [
    meattype.objects.create(slug="pork-shoulder", name="梅花豬", addon_price="0.00"),
    meattype.objects.create(slug="beef-short-plate", name="霜降牛", addon_price="40.00"),
    meattype.objects.create(slug="pork-jowl", name="松阪豬", addon_price="60.00"),
]
TOPPINGS = [
    hotpotingredients.objects.create(slug="squid", name="九層花枝", addon_price="40.00"),
    hotpotingredients.objects.create(slug="mushroom-ball", name="香菇貢丸", addon_price="40.00"),
]
QUANTITIES = [1, 2, 3, 4, 5]

RECORDED_NOTE = "__NOTE__"  # placeholder; notes is a verified pure passthrough


def jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return {"type": type(value).__name__, "value": value}
    if isinstance(value, list):
        return {"type": "list", "value": [jsonable(v) for v in value]}
    if isinstance(value, dict):
        return {"type": "dict", "value": {k: jsonable(v) for k, v in value.items()}}
    if hasattr(value, "pk") and hasattr(value, "_meta"):
        return {
            "type": f"{type(value).__name__} instance",
            "value": f"<{type(value).__name__}: {value}>  pk={value.pk}",
        }
    return {"type": type(value).__name__, "value": str(value)}


def fresh_request():
    request = RequestFactory().post("/api/cart/item/")
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    request.session["table_number"] = 7
    request.user = AnonymousUser()
    return request


def combo_key(meat_slug, topping_slugs, doublemeat, quantity):
    return "|".join(
        [meat_slug, ",".join(sorted(topping_slugs)) or "-", "1" if doublemeat else "0", str(quantity)]
    )


def record_run(meat, topping_slugs, doublemeat, quantity):
    """Actually run the real serializer and capture every intermediate."""
    cartitem.objects.all().delete()
    cart.objects.all().delete()

    request = fresh_request()
    payload = {
        "product": PRODUCT.slug,
        "meattype": meat.slug,
        "doublemeat": doublemeat,
        "notes": RECORDED_NOTE,
        "quantity": quantity,
        "hotpotingredients": list(topping_slugs),
    }

    with CaptureQueriesContext(connection) as ctx:
        serializer = ser_module.cartitemSerializer(data=payload, context={"request": request})
        ok = serializer.is_valid()
        if not ok:
            return {"errors": serializer.errors}
        validated = dict(serializer.validated_data)
        item = serializer.save()
        response_body = dict(ser_module.cartitemSerializer(item).data)

    writes = [
        q["sql"] for q in ctx.captured_queries
        if q["sql"].lstrip().upper().startswith(("INSERT", "UPDATE"))
    ]
    reads = [
        q["sql"] for q in ctx.captured_queries
        if q["sql"].lstrip().upper().startswith("SELECT")
    ]

    return {
        "validated_data": jsonable(validated),
        "computed": {
            "unit_price": str(item.price),
            "cart_total": str(item.cart.total_price),
            "formula": (
                f"{PRODUCT.price} (product.price) + {meat.addon_price} (meattype.addon_price)"
                + (" + 80 (doublemeat)" if doublemeat else "")
                + "".join(
                    f" + {t.addon_price} ({t.name})"
                    for t in TOPPINGS if t.slug in topping_slugs
                )
                + f" = {item.price}"
            ),
        },
        "response_body": jsonable(response_body),
        "sql_reads": reads,
        "sql_writes": writes,
        "query_count": len(ctx.captured_queries),
        "row": jsonable(
            {
                "id": item.pk,
                "cart_id": item.cart_id,
                "product_id": item.product_id,
                "meattype_id": item.meattype_id,
                "quantity": item.quantity,
                "price": item.price,
                "doublemeat": item.doublemeat,
                "notes": item.notes,
                "status": item.status,
            }
        ),
    }


def record_all():
    runs = {}
    topping_slugs = [t.slug for t in TOPPINGS]
    subsets = []
    for r in range(len(topping_slugs) + 1):
        subsets.extend(itertools.combinations(topping_slugs, r))

    for meat in MEATS:
        for subset in subsets:
            for doublemeat in (False, True):
                for quantity in QUANTITIES:
                    key = combo_key(meat.slug, subset, doublemeat, quantity)
                    runs[key] = record_run(meat, subset, doublemeat, quantity)
    return runs


def resolve_route():
    match = resolve("/api/cart/item/")
    return {
        "path": "/api/cart/item/",
        "matched_pattern": str(match.route),
        "url_name": match.url_name,
        "view_name": match.view_name,
        "callable": f"{match.func.__module__}.{getattr(match.func, '__name__', repr(match.func))}",
        "view_class": getattr(match.func, "cls", type(None)).__name__,
        "args": list(match.args),
        "kwargs": match.kwargs,
    }


def slice_source(rel_path, start, end):
    """1-indexed inclusive line slice out of the real target source file."""
    with open(os.path.join(TARGET_REPO, rel_path), encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    return {
        "file": rel_path,
        "start_line": start,
        "code": "\n".join(lines[start - 1 : end]),
    }


def build_code_excerpts():
    return {
        "dom": slice_source("templates/includes/menuitem-detail.html", 51, 63),
        "javascript": slice_source("templates/js/menudetail.js", 59, 81),
        "network": slice_source("templates/js/menudetail.js", 39, 52),
        "http": slice_source("templates/js/menudetail.js", 66, 81),
        "router": slice_source("restaurantAPI/urls.py", 1, 12),
        "view": slice_source("restaurantAPI/views.py", 134, 150),
        "serializer": slice_source("restaurantAPI/serializers.py", 41, 75),
        "database": slice_source("restaurantAPI/models.py", 80, 105),
    }


def main():
    snapshot = {
        "target_project": "YC-0210/restautant-order-system",
        "product": {
            "slug": PRODUCT.slug,
            "name": PRODUCT.product,
            "price": str(PRODUCT.price),
        },
        "meats": [
            {"slug": m.slug, "name": m.name, "addon_price": str(m.addon_price)} for m in MEATS
        ],
        "toppings": [
            {"slug": t.slug, "name": t.name, "addon_price": str(t.addon_price)} for t in TOPPINGS
        ],
        "doublemeat_addon": "80",
        "quantities": QUANTITIES,
        "note_placeholder": RECORDED_NOTE,
        "route": resolve_route(),
        "code": build_code_excerpts(),
        "runs": record_all(),
    }
    print(json.dumps(snapshot, indent=1, default=str))


if __name__ == "__main__":
    main()
