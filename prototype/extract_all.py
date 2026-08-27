"""
PROTOTYPE, throwaway script. Not part of the real product.

Records a real request pipeline for EVERY endpoint the restautant-order-system
project defines, so the Lab can replay any of them.

Everything server-side is captured by actually issuing the request through
Django's test Client against a throwaway sqlite database and observing what
happened: the resolved route, the middleware-populated request, the view and
its permissions, serializer input/output, the SQL emitted, the template
rendered, and the response. Source excerpts come from inspect.getsourcelines()
on the real callables, so they cannot drift out of sync with the code.

What is seeded: the menu rows and the user accounts. The project ships an
empty database.

Usage:
    TARGET_REPO=/path/to/restautant-order-system python extract_all.py > endpoints.json
"""
import inspect
import itertools
import json
import os
import re
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

from django.contrib.auth.models import User  # noqa: E402
from django.db import connection  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import CaptureQueriesContext  # noqa: E402
from django.urls import resolve  # noqa: E402

from restaurantAPI import views as views_module  # noqa: E402
from restaurantAPI import serializers as ser_module  # noqa: E402
from restaurantAPI.models import (  # noqa: E402
    menuitem,
    meattype,
    hotpotingredients,
    cart,
    cartitem,
)

# ------------------------------------------------------------------ SQL pool
SQL_POOL = []
SQL_INDEX = {}


def sql_ref(statement):
    """Dedupe SQL text across every recorded run; the JSON stores indices."""
    key = statement.strip()
    if key not in SQL_INDEX:
        SQL_INDEX[key] = len(SQL_POOL)
        SQL_POOL.append(key)
    return SQL_INDEX[key]


# ------------------------------------------------------------------ helpers
def jsonable(value, depth=0):
    if value is None or isinstance(value, (str, int, float, bool)):
        return {"type": type(value).__name__, "value": value}
    if depth > 4:
        return {"type": type(value).__name__, "value": str(value)[:200]}
    if isinstance(value, (list, tuple)):
        return {"type": "list", "value": [jsonable(v, depth + 1) for v in value[:12]]}
    if isinstance(value, dict):
        return {"type": "dict", "value": {str(k): jsonable(v, depth + 1) for k, v in value.items()}}
    if hasattr(value, "pk") and hasattr(value, "_meta"):
        return {
            "type": f"{type(value).__name__} instance",
            "value": f"<{type(value).__name__}: {value}>  pk={value.pk}",
        }
    if hasattr(value, "__iter__") and not isinstance(value, str):
        try:
            items = list(value)[:12]
            return {"type": type(value).__name__, "value": [jsonable(v, depth + 1) for v in items]}
        except Exception:
            pass
    return {"type": type(value).__name__, "value": str(value)[:200]}


def source_of(obj):
    """Real source lines for a real callable, located by inspect."""
    try:
        target = obj
        if hasattr(obj, "cls"):
            target = obj.cls
        lines, start = inspect.getsourcelines(target)
        path = os.path.relpath(inspect.getsourcefile(target), TARGET_REPO)
        code = "".join(lines).rstrip("\n")
        if len(code) > 4000:
            code = code[:4000] + "\n    # … truncated"
        return {"file": path, "start_line": start, "code": code}
    except Exception as exc:  # pragma: no cover - defensive
        return {"file": "?", "start_line": 0, "code": f"# source unavailable: {exc}"}


def source_slice(rel_path, start, end):
    with open(os.path.join(TARGET_REPO, rel_path), encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    return {
        "file": rel_path,
        "start_line": start,
        "code": "\n".join(lines[start - 1 : end]),
    }


def js_block(rel_path, needle, before=2, after=40):
    """Slice the real JS around the line containing `needle`."""
    with open(os.path.join(TARGET_REPO, rel_path), encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    idx = next((i for i, l in enumerate(lines) if needle in l), 0)
    start = max(0, idx - before)
    end = min(len(lines), idx + after)
    return {"file": rel_path, "start_line": start + 1, "code": "\n".join(lines[start:end])}


# ------------------------------------------------------------------ seed
PRODUCTS = [
    menuitem.objects.create(slug="classic-original", product="經典原味鍋", price="200.00"),
    menuitem.objects.create(slug="spicy-mala", product="麻辣鴛鴦鍋", price="260.00"),
    menuitem.objects.create(slug="milk-miso", product="味噌牛奶鍋", price="240.00"),
]
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

MANAGER = User.objects.create_user(username="manager", password="pw", is_staff=True)
CUSTOMER = User.objects.create_user(username="customer", password="pw")

STATUS_CHOICES = [c[0] for c in cartitem.STATUS_CHOICES]


def reset_carts():
    cartitem.objects.all().delete()
    cart.objects.all().delete()


def make_demo_cart(owner=None, table=7, how_many=2):
    c = cart.objects.create(user=owner, table_number=table, total_price="0.00")
    total = 0
    for i in range(how_many):
        it = cartitem.objects.create(
            cart=c,
            product=PRODUCTS[i % len(PRODUCTS)],
            meattype=MEATS[i % len(MEATS)],
            quantity=1,
            price=PRODUCTS[i % len(PRODUCTS)].price,
            doublemeat=False,
            notes="",
        )
        total += float(it.price)
    c.total_price = total
    c.save()
    return c


# ------------------------------------------------------------------ recorder
CLIENT = Client()


def perform(method, path, body=None, as_user=None, content_type="application/json"):
    """Issue one real request and capture everything observable about it."""
    if as_user:
        CLIENT.force_login(as_user)
    else:
        CLIENT.logout()

    session = CLIENT.session
    session["table_number"] = 7
    session.save()

    fn = getattr(CLIENT, method.lower())
    kwargs = {}
    if body is not None:
        kwargs["data"] = json.dumps(body) if content_type == "application/json" else body
        kwargs["content_type"] = content_type

    with CaptureQueriesContext(connection) as ctx:
        response = fn(path, **kwargs)

    queries = ctx.captured_queries
    reads = [sql_ref(q["sql"]) for q in queries if q["sql"].lstrip().upper().startswith("SELECT")]
    writes = [
        sql_ref(q["sql"])
        for q in queries
        if q["sql"].lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
    ]

    req = response.wsgi_request
    match = resolve(path)

    body_out = None
    if hasattr(response, "data"):
        body_out = jsonable(response.data)
    elif response.get("Content-Type", "").startswith("text/html"):
        body_out = {
            "type": "html",
            "value": f"{len(response.content)} bytes of HTML",
        }

    context_keys = {}
    if getattr(response, "context", None):
        ctxs = response.context if isinstance(response.context, list) else [response.context]
        for c in ctxs:
            try:
                for d in c.dicts:
                    for k, v in d.items():
                        if k.startswith("_") or k in ("True", "False", "None", "csrf_token"):
                            continue
                        context_keys[k] = jsonable(v)
            except Exception:
                pass

    return {
        "status_code": response.status_code,
        "route": {
            "path": path,
            "matched_pattern": str(match.route),
            "url_name": match.url_name,
            "view_class": getattr(match.func, "cls", type(None)).__name__,
            "callable": f"{match.func.__module__}.{getattr(match.func, '__name__', 'view')}",
            "kwargs": jsonable(match.kwargs),
        },
        "middleware": {
            "request.method": jsonable(req.method),
            "request.path": jsonable(req.path),
            "request.user": jsonable(str(req.user)),
            "request.user.is_authenticated": jsonable(req.user.is_authenticated),
            "request.session['table_number']": jsonable(req.session.get("table_number")),
            "middleware chain": jsonable([m.rsplit(".", 1)[-1] for m in settings.MIDDLEWARE]),
        },
        "request_body": jsonable(body) if body is not None else None,
        "response_body": body_out,
        "template_context": context_keys or None,
        "templates": [t.name for t in getattr(response, "templates", []) if t.name][:4],
        "sql_reads": reads,
        "sql_writes": writes,
        "query_count": len(queries),
        "content_length": len(response.content),
    }


# ------------------------------------------------------------------ stages
def stages_for(kind, has_body, has_serializer, triggered_by_ui):
    """The ordered stages an endpoint's data actually passes through."""
    s = []
    if triggered_by_ui:
        s.append(("dom", "DOM", "Form controls hold the user's input", "client"))
        s.append(("javascript", "JavaScript", "Handler builds a JS object", "client"))
    elif kind == "html":
        s.append(("navigation", "Browser Navigation", "A link or address bar starts the request", "client"))
    else:
        s.append(("console", "API Console", "The request is issued directly", "client"))

    s.append(("network", "Browser Network", "fetch() adds headers and the CSRF cookie", "client"))
    s.append(("http_request", "HTTP Request", "Everything is now text on the wire", "wire"))
    s.append(("url_router", "URL Router", "Django matches the path to a view", "server"))
    s.append(("middleware", "Middleware", "session and request.user are attached", "server"))
    s.append(("view", "View", "The view receives the parsed request", "server"))

    if has_serializer and has_body:
        s.append(("serializer_in", "Serializer (in)", "Strings become real model objects", "server"))
    s.append(("database", "Database", "SQL runs against the tables", "server"))
    if has_serializer:
        s.append(("serializer_out", "Serializer (out)", "Model instances become a plain dict", "server"))
    if kind == "html":
        s.append(("template", "Template", "Context is rendered into HTML", "server"))

    s.append(("http_response", "HTTP Response", "Status line, headers and a text body", "wire"))
    if triggered_by_ui:
        s.append(("javascript_then", "JavaScript (.then)", "res.json() parses text back to an object", "client"))
        s.append(("dom_update", "DOM (update)", "The page shows the result", "client"))
    elif kind == "html":
        s.append(("render", "Browser Render", "HTML is parsed into a new DOM", "client"))
    else:
        s.append(("console_out", "API Console (out)", "The parsed response body", "client"))

    return [{"id": i, "name": n, "sub": sub, "side": side} for i, n, sub, side in s]


# ------------------------------------------------------------------ runs
def combo_key(product, meat, toppings, doublemeat, quantity):
    return "|".join(
        [product, meat, ",".join(sorted(toppings)) or "-", "1" if doublemeat else "0", str(quantity)]
    )


def record_post_cart_item():
    """The form-driven endpoint: one real run per selectable combination."""
    runs = {}
    topping_slugs = [t.slug for t in TOPPINGS]
    subsets = []
    for r in range(len(topping_slugs) + 1):
        subsets.extend(itertools.combinations(topping_slugs, r))

    for product in PRODUCTS:
        for meat in MEATS:
            for subset in subsets:
                for dbl in (False, True):
                    for qty in QUANTITIES:
                        reset_carts()
                        body = {
                            "product": product.slug,
                            "meattype": meat.slug,
                            "doublemeat": dbl,
                            "notes": "__NOTE__",
                            "quantity": qty,
                            "hotpotingredients": list(subset),
                        }
                        run = perform("POST", "/api/cart/item/", body)
                        item = cartitem.objects.order_by("-pk").first()
                        if item:
                            run["serializer_in"] = jsonable(
                                {
                                    "product": item.product,
                                    "meattype": item.meattype,
                                    "hotpotingredients": list(item.hotpotingredients.all()),
                                    "quantity": item.quantity,
                                    "doublemeat": item.doublemeat,
                                    "notes": item.notes,
                                }
                            )
                            run["computed"] = {
                                "unit_price": str(item.price),
                                "cart_total": str(item.cart.total_price),
                                "formula": (
                                    f"{product.price} (product.price)"
                                    f" + {meat.addon_price} (meattype.addon_price)"
                                    + (" + 80 (doublemeat)" if dbl else "")
                                    + "".join(
                                        f" + {t.addon_price} ({t.name})"
                                        for t in TOPPINGS if t.slug in subset
                                    )
                                    + f" = {item.price}"
                                ),
                            }
                            run["row"] = jsonable(
                                {
                                    "id": item.pk, "cart_id": item.cart_id,
                                    "product_id": item.product_id, "meattype_id": item.meattype_id,
                                    "quantity": item.quantity, "price": item.price,
                                    "doublemeat": item.doublemeat, "notes": item.notes,
                                    "status": item.status,
                                }
                            )
                        runs[combo_key(product.slug, meat.slug, subset, dbl, qty)] = run
    return runs


def record_patch_cart_item():
    """The cart_list status dropdown: one real run per status value."""
    runs = {}
    for status in STATUS_CHOICES:
        reset_carts()
        c = make_demo_cart(owner=CUSTOMER, how_many=1)
        item = cartitem.objects.filter(cart=c).first()
        run = perform("PATCH", f"/api/cart/item/{item.pk}/", {"status": status}, as_user=MANAGER)
        item.refresh_from_db()
        run["row"] = jsonable(
            {"id": item.pk, "status": item.status, "price": item.price, "quantity": item.quantity}
        )
        run["path_used"] = f"/api/cart/item/{item.pk}/"
        runs[status] = run
    return runs


def one(method, path, body=None, as_user=None, setup=None):
    reset_carts()
    if setup:
        setup()
    return {"default": perform(method, path, body, as_user)}


# ------------------------------------------------------------------ endpoints
def build_endpoints():
    eps = []

    def add(**kw):
        eps.append(kw)

    # ---- form-driven API endpoint
    add(
        id="post_cart_item", method="POST", path="/api/cart/item/", kind="api",
        view="cartitemList", serializer="cartitemSerializer", model="cartitem",
        permissions=["AllowAny"], trigger={"page": "detail", "kind": "form"},
        note="Triggered by 加入訂單 on the item page.",
        stages=stages_for("api", True, True, True),
        code={
            "dom": source_slice("templates/includes/menuitem-detail.html", 51, 63),
            "javascript": js_block("templates/js/menudetail.js", 'fetch("/api/cart/item/"', before=8, after=24),
            "network": js_block("templates/js/menudetail.js", "function getCsrfToken", before=1, after=14),
            "view": source_of(views_module.cartitemList),
            "serializer_in": source_of(ser_module.cartitemSerializer),
            "serializer_out": source_of(ser_module.cartitemSerializer),
            "database": source_of(cartitem),
        },
        runs=record_post_cart_item(),
    )

    # ---- dropdown-driven API endpoint
    add(
        id="patch_cart_item", method="PATCH", path="/api/cart/item/<id>/", kind="api",
        view="cartitemDetail", serializer="cartitemSerializer", model="cartitem",
        permissions=["IsAuthenticated"], trigger={"page": "cart", "kind": "select"},
        note="Triggered by the status dropdown on the order-management page. Manager only.",
        stages=stages_for("api", True, True, True),
        code={
            "dom": source_slice("templates/js/cart-list.js", 1, 9),
            "javascript": js_block("templates/js/cart-list.js", "fetch(`/api/cart/item/", before=8, after=24),
            "network": js_block("templates/js/cart-list.js", "X-CSRFToken", before=4, after=8),
            "view": source_of(views_module.cartitemDetail),
            "serializer_in": source_of(ser_module.cartitemSerializer),
            "serializer_out": source_of(ser_module.cartitemSerializer),
            "database": source_of(cartitem),
        },
        runs=record_patch_cart_item(),
    )

    # ---- HTML pages
    add(
        id="get_index", method="GET", path="/", kind="html",
        view="index", serializer=None, model="menuitem", permissions=[],
        trigger={"page": "menu", "kind": "navigate"},
        note="The menu page. A plain Django view - no serializer anywhere.",
        stages=stages_for("html", False, False, False),
        code={"view": source_of(views_module.index), "database": source_of(menuitem)},
        runs=one("GET", "/"),
    )
    add(
        id="get_menuitem_page", method="GET", path="/menuitem/<slug>/", kind="html",
        view="menuitem_detail", serializer=None, model="menuitem", permissions=[],
        trigger={"page": "detail", "kind": "navigate"},
        note="The item page. Renders the form that later POSTs to the API.",
        stages=stages_for("html", False, False, False),
        code={"view": source_of(views_module.menuitem_detail), "database": source_of(menuitem)},
        runs={p.slug: perform("GET", f"/menuitem/{p.slug}/") for p in PRODUCTS},
    )
    add(
        id="get_cart_list_manager", method="GET", path="/cart_list/", kind="html",
        view="cart_list", serializer=None, model="cart", permissions=["login_required"],
        trigger={"page": "cart", "kind": "navigate"},
        note="Order management. select_related + prefetch_related collapse the joins; a manager sees every cart.",
        stages=stages_for("html", False, False, False),
        code={"view": source_of(views_module.cart_list), "database": source_of(cart)},
        runs={
            "manager": perform("GET", "/cart_list/", as_user=MANAGER),
            "customer": perform("GET", "/cart_list/", as_user=CUSTOMER),
        },
    )
    add(
        id="get_login", method="GET", path="/login/", kind="html",
        view="login_view", serializer=None, model=None, permissions=[],
        trigger=None, note="Manager sign-in form.",
        stages=stages_for("html", False, False, False),
        code={"view": source_of(views_module.login_view)},
        runs=one("GET", "/login/"),
    )
    add(
        id="post_login", method="POST", path="/login/", kind="html",
        view="login_view", serializer=None, model=None, permissions=[],
        trigger=None, note="AuthenticationForm validates, then redirects on success.",
        stages=stages_for("html", True, False, False),
        code={"view": source_of(views_module.login_view)},
        runs={
            "default": perform(
                "POST", "/login/",
                {"username": "manager", "password": "pw"},
                content_type="application/x-www-form-urlencoded",
            )
        },
    )
    add(
        id="get_logout", method="GET", path="/logout/", kind="html",
        view="logout_view", serializer=None, model=None, permissions=[],
        trigger=None, note="Clears the session but deliberately preserves table_number.",
        stages=stages_for("html", False, False, False),
        code={"view": source_of(views_module.logout_view)},
        runs=one("GET", "/logout/", as_user=MANAGER),
    )

    # ---- the rest of the DRF surface, no UI trigger
    api_specs = [
        ("get_menu_list", "GET", "/api/menuitem/", None, None, views_module.menuList,
         ser_module.menuitemSerializer, "AllowAny", "Lists every menu item."),
        ("post_menu_list", "POST", "/api/menuitem/",
         {"slug": "new-dish", "product": "新品鍋", "price": "180.00"}, None, views_module.menuList,
         ser_module.menuitemSerializer, "AllowAny", "Creates a menu item. Note it is AllowAny - anyone can post a dish."),
        ("get_menuitem_detail", "GET", "/api/menuitem/classic-original/", None, None,
         views_module.menuitemDetail, ser_module.menuitemSerializer, "AllowAny",
         "Looks up by slug, not by id - lookup_field = 'slug'."),
        ("get_cart_list_api", "GET", "/api/cart/", None, None, views_module.cartList,
         ser_module.cartSerializer, "AllowAny", "Lists carts."),
        ("post_cart_api", "POST", "/api/cart/", {}, None, views_module.cartList,
         ser_module.cartSerializer, "AllowAny",
         "Every field on cartSerializer is read_only, so an empty body still creates a cart."),
        ("get_cartitem_list_api", "GET", "/api/cart/item/", None, MANAGER, views_module.cartitemList,
         ser_module.cartitemSerializer, "AllowAny",
         "get_queryset() branches on who is asking - a manager sees every line."),
    ]
    for eid, method, path, body, user, view_cls, ser_cls, perm, note in api_specs:
        add(
            id=eid, method=method, path=path, kind="api",
            view=view_cls.__name__, serializer=ser_cls.__name__,
            model=getattr(getattr(view_cls, "queryset", None), "model", type(None)).__name__,
            permissions=[perm], trigger=None, note=note,
            stages=stages_for("api", body is not None, True, False),
            code={
                "view": source_of(view_cls),
                "serializer_in": source_of(ser_cls),
                "serializer_out": source_of(ser_cls),
                "database": source_of(getattr(getattr(view_cls, "queryset", None), "model", menuitem)),
            },
            runs=one(method, path, body, user),
        )

    # ---- detail endpoints that need an existing row
    def with_cart():
        c = make_demo_cart(owner=CUSTOMER, how_many=1)
        return c

    for eid, method, body, note in [
        ("get_cart_detail", "GET", None, "Manager-only read of one cart."),
        ("patch_cart_detail", "PATCH", {"table_number": 12},
         "table_number is read_only on cartSerializer, so this succeeds and changes nothing."),
        ("delete_cart_detail", "DELETE", None, "Cascades: deleting a cart deletes its cartitems."),
    ]:
        reset_carts()
        c = with_cart()
        add(
            id=eid, method=method, path=f"/api/cart/<id>/", kind="api",
            view="cartDetail", serializer="cartSerializer", model="cart",
            permissions=["IsAuthenticated"], trigger=None, note=note,
            stages=stages_for("api", body is not None, True, False),
            code={
                "view": source_of(views_module.cartDetail),
                "serializer_in": source_of(ser_module.cartSerializer),
                "serializer_out": source_of(ser_module.cartSerializer),
                "database": source_of(cart),
            },
            runs={"default": perform(method, f"/api/cart/{c.pk}/", body, as_user=MANAGER)},
        )

    for eid, method, body, user, note in [
        ("get_cartitem_detail", "GET", None, MANAGER, "Reads one line item."),
        ("put_cartitem_detail", "PUT",
         {"product": "classic-original", "meattype": "beef-short-plate", "quantity": 3,
          "doublemeat": False, "notes": "put replaces every writable field", "hotpotingredients": []},
         MANAGER, "PUT replaces the whole object - and create()'s price logic does NOT run on update, so price keeps its old value."),
        ("delete_cartitem_detail", "DELETE", None, MANAGER, "Removes the line. Note cart.total_price is not recalculated."),
    ]:
        reset_carts()
        c = make_demo_cart(owner=CUSTOMER, how_many=1)
        item = cartitem.objects.filter(cart=c).first()
        run = perform(method, f"/api/cart/item/{item.pk}/", body, as_user=user)
        add(
            id=eid, method=method, path="/api/cart/item/<id>/", kind="api",
            view="cartitemDetail", serializer="cartitemSerializer", model="cartitem",
            permissions=["IsAuthenticated"], trigger=None, note=note,
            stages=stages_for("api", body is not None, True, False),
            code={
                "view": source_of(views_module.cartitemDetail),
                "serializer_in": source_of(ser_module.cartitemSerializer),
                "serializer_out": source_of(ser_module.cartitemSerializer),
                "database": source_of(cartitem),
            },
            runs={"default": run},
        )

    return eps


def main():
    endpoints = build_endpoints()
    out = {
        "target_project": "YC-0210/restautant-order-system",
        "products": [{"slug": p.slug, "name": p.product, "price": str(p.price)} for p in PRODUCTS],
        "meats": [{"slug": m.slug, "name": m.name, "addon_price": str(m.addon_price)} for m in MEATS],
        "toppings": [{"slug": t.slug, "name": t.name, "addon_price": str(t.addon_price)} for t in TOPPINGS],
        "statuses": [{"value": v, "label": l} for v, l in cartitem.STATUS_CHOICES],
        "doublemeat_addon": "80",
        "quantities": QUANTITIES,
        "note_placeholder": "__NOTE__",
        "middleware": [m.rsplit(".", 1)[-1] for m in settings.MIDDLEWARE],
        "sql_pool": SQL_POOL,
        "endpoints": endpoints,
    }
    print(json.dumps(out, separators=(",", ":"), default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
