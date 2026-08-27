"""
PROTOTYPE, throwaway script. Not part of the real product.

Produces the Snapshot (see CONTEXT.md) for the Ultimate Visualization prototype:
runs the real restautant-order-system Django project via Django/DRF's own
reflection to build the Structure Map, and actually executes the three Focus
Endpoints against sample data in a throwaway sqlite database to capture real
Flow Traces.

Usage:
    TARGET_REPO=/path/to/restautant-order-system \
    python extract_snapshot.py > snapshot.json

Requires the target repo's requirements.txt to be installed in the current
interpreter (Python >= 3.12, since the target pins Django==6.1).
"""
import json
import os
import sys
import tempfile

TARGET_REPO = os.environ.get(
    "TARGET_REPO", "/home/user/yc-0210/restautant-order-system"
)
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

from restaurantAPI.models import (  # noqa: E402
    menuitem,
    meattype,
    hotpotingredients,
    cart,
    cartitem,
)
from restaurantAPI import serializers as ser_module  # noqa: E402
from restaurantAPI import views as views_module  # noqa: E402

MODELS = [menuitem, meattype, hotpotingredients, cart, cartitem]
SERIALIZERS = [
    ser_module.menuitemSerializer,
    ser_module.cartSerializer,
    ser_module.cartitemSerializer,
]
HTTP_METHODS = ["get", "post", "put", "patch", "delete"]


def jsonable(value):
    """Best-effort real-value -> (type name, json-safe repr) for the UI."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return {"type": type(value).__name__, "value": value}
    if isinstance(value, list):
        return {"type": "list", "value": [jsonable(v) for v in value]}
    if isinstance(value, dict):
        return {"type": "dict", "value": {k: jsonable(v) for k, v in value.items()}}
    if hasattr(value, "pk") and hasattr(value, "_meta"):
        return {
            "type": f"{type(value).__name__} instance",
            "value": f"<{type(value).__name__} pk={value.pk}> {value}",
        }
    return {"type": type(value).__name__, "value": str(value)}


def describe_model(model):
    fields = []
    for f in model._meta.get_fields():
        entry = {"name": f.name, "kind": type(f).__name__}
        if getattr(f, "is_relation", False):
            entry["related_model"] = f.related_model.__name__ if f.related_model else None
            entry["many"] = bool(
                getattr(f, "many_to_many", False) or getattr(f, "one_to_many", False)
            )
        fields.append(entry)
    return {"name": model.__name__, "table": model._meta.db_table, "fields": fields}


def describe_serializer(serializer_cls):
    inst = serializer_cls()
    fields = []
    for name, field in inst.get_fields().items():
        fields.append(
            {
                "name": name,
                "kind": type(field).__name__,
                "read_only": field.read_only,
                "required": field.required,
            }
        )
    meta = getattr(serializer_cls, "Meta", None)
    model = getattr(meta, "model", None)
    return {
        "name": serializer_cls.__name__,
        "model": model.__name__ if model else None,
        "fields": fields,
    }


def describe_endpoint(path, view_cls, kind="api", template=None):
    methods = [m.upper() for m in HTTP_METHODS if hasattr(view_cls, m)]
    entry = {"path": path, "methods": methods, "view": view_cls.__name__, "kind": kind}
    if kind == "api":
        entry["serializer"] = getattr(view_cls, "serializer_class", None).__name__
        qs = getattr(view_cls, "queryset", None)
        entry["model"] = qs.model.__name__ if qs is not None else None
        entry["permission_classes"] = [
            p.__name__ for p in getattr(view_cls, "permission_classes", [])
        ]
    else:
        entry["methods"] = ["GET"]
        entry["template"] = template
    return entry


def build_structure():
    return {
        "models": [describe_model(m) for m in MODELS],
        "serializers": [describe_serializer(s) for s in SERIALIZERS],
        "endpoints": [
            describe_endpoint("/api/menuitem/", views_module.menuList),
            describe_endpoint("/api/menuitem/<slug>/", views_module.menuitemDetail),
            describe_endpoint("/api/cart/", views_module.cartList),
            describe_endpoint("/api/cart/<id>/", views_module.cartDetail),
            describe_endpoint("/api/cart/item/", views_module.cartitemList),
            describe_endpoint("/api/cart/item/<id>/", views_module.cartitemDetail),
            describe_endpoint(
                "/cart_list/", views_module.cart_list, kind="html", template="cart_list.html"
            ),
        ],
    }


def seed_menu_fixtures():
    mi = menuitem.objects.create(slug="kimchi-hotpot", product="Kimchi Hotpot", price="180.00")
    mt = meattype.objects.create(slug="beef", name="Beef", addon_price="40.00")
    hp = hotpotingredients.objects.create(slug="mushroom", name="Mushroom", addon_price="15.00")
    return mi, mt, hp


def trace_menuitem_detail(mi):
    from django.test import RequestFactory

    steps = [
        {
            "label": "Database row",
            "description": "The real row fetched from the menuitem table.",
            **jsonable(mi),
        }
    ]
    serialized = ser_module.menuitemSerializer(mi).data
    steps.append(
        {
            "label": "Serializer output",
            "description": "menuitemSerializer turns the model instance into a plain dict of JSON-safe values.",
            **jsonable(dict(serialized)),
        }
    )
    req = RequestFactory().get(f"/api/menuitem/{mi.slug}/")
    resp = views_module.menuitemDetail.as_view()(req, slug=mi.slug)
    steps.append(
        {
            "label": "HTTP response",
            "description": f"GET /api/menuitem/{mi.slug}/ -> {resp.status_code}",
            **jsonable(dict(resp.data)),
        }
    )
    return {
        "id": "menuitem_detail",
        "title": f"GET /api/menuitem/{mi.slug}/",
        "endpoint_path": "/api/menuitem/<slug>/",
        "steps": steps,
    }


def trace_cart_item_create(mi, mt, hp):
    from django.test import RequestFactory
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.auth.models import AnonymousUser

    request = RequestFactory().post("/api/cart/item/")
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    request.session["table_number"] = 5
    request.user = AnonymousUser()

    payload = {
        "product": mi.slug,
        "meattype": mt.slug,
        "hotpotingredients": [hp.slug],
        "doublemeat": True,
        "quantity": 2,
        "notes": "no onion",
    }
    steps = [
        {
            "label": "Client request body",
            "description": "Raw JSON sent by the client. product/meattype/hotpotingredients are plain strings.",
            **jsonable(payload),
        }
    ]

    serializer = ser_module.cartitemSerializer(data=payload, context={"request": request})
    serializer.is_valid(raise_exception=True)
    steps.append(
        {
            "label": "Validated data",
            "description": "After validation, SlugRelatedField resolved each slug string into the real model instance it names.",
            **jsonable(serializer.validated_data),
        }
    )

    item = serializer.save()
    steps.append(
        {
            "label": "cartitemSerializer.create() computed a new value",
            "description": (
                "price never came from the client. It was computed inside create(): "
                f"product.price ({mi.price}) + meattype.addon_price ({mt.addon_price}) "
                "+ 80 (doublemeat surcharge) + sum(hotpot ingredient addon prices)."
            ),
            **jsonable({"item.price": item.price, "cart.total_price": item.cart.total_price}),
        }
    )

    final = ser_module.cartitemSerializer(item).data
    steps.append(
        {
            "label": "HTTP response",
            "description": "The saved row, serialized back out. Slugs render as strings again; price is now present.",
            **jsonable(dict(final)),
        }
    )
    return {
        "id": "cart_item_create",
        "title": "POST /api/cart/item/",
        "endpoint_path": "/api/cart/item/",
        "steps": steps,
    }


def trace_cart_list():
    from django.contrib.auth.models import User
    from django.test import Client
    from django.test.utils import CaptureQueriesContext
    from django.db import connection

    manager = User.objects.create_user(username="mgr_demo", password="x", is_staff=True)
    customer = User.objects.create_user(username="cust_demo", password="x")
    mi = menuitem.objects.filter(slug="kimchi-hotpot").first()
    mt = meattype.objects.filter(slug="beef").first()
    mgr_cart = cart.objects.create(user=manager, table_number=1, total_price="220.00")
    cust_cart = cart.objects.create(user=customer, table_number=2, total_price="220.00")
    cartitem.objects.create(cart=mgr_cart, product=mi, meattype=mt, price="220.00", quantity=1)
    cartitem.objects.create(cart=cust_cart, product=mi, meattype=mt, price="220.00", quantity=1)

    client = Client()
    roles = {}
    for label, user in [("manager", manager), ("customer", customer)]:
        client.force_login(user)
        with CaptureQueriesContext(connection) as ctx:
            resp = client.get("/cart_list/")
        carts_seen = list(resp.context["carts"])
        roles[label] = {
            "status_code": resp.status_code,
            "query_count": len(ctx.captured_queries),
            "carts_seen": [
                f"cart#{c.pk} ({'guest, no owner' if c.user_id is None else f'owner user#{c.user_id}'})"
                for c in carts_seen
            ],
            "html_bytes": len(resp.content),
        }

    steps = [
        {
            "label": "is_manager(request.user) branches the queryset",
            "description": "Same view, same URL - the code path taken depends on who is asking.",
            "type": "comparison",
            "value": roles,
        },
        {
            "label": "select_related + prefetch_related",
            "description": (
                "cart -> cartitem_set (reverse FK) -> product/meattype (forward FK) and "
                "hotpotingredients (M2M) are all joined in a small, fixed number of queries "
                "instead of one query per related row."
            ),
            "type": "note",
            "value": None,
        },
        {
            "label": "Rendered into cart_list.html",
            "description": "No serializer here - the queryset goes straight into a Django template context and comes out as HTML, not JSON.",
            "type": "note",
            "value": None,
        },
    ]
    return {
        "id": "cart_list",
        "title": "GET /cart_list/",
        "endpoint_path": "/cart_list/",
        "steps": steps,
    }


def main():
    structure = build_structure()
    mi, mt, hp = seed_menu_fixtures()
    focus_endpoints = [
        trace_menuitem_detail(mi),
        trace_cart_item_create(mi, mt, hp),
        trace_cart_list(),
    ]
    snapshot = {
        "target_project": "YC-0210/restautant-order-system",
        "structure": structure,
        "focus_endpoints": focus_endpoints,
    }
    print(json.dumps(snapshot, indent=2, default=str))


if __name__ == "__main__":
    main()
