# This file sits on every request and response to the server.
from typing import Any
from django.template.backends.django import Template
from rest_framework.serializers import Serializer
from django.db import connection
import time
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from django.conf import settings


class SupervisualizerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = datetime.now(timezone.utc)
        # capture the request
        try : 
            # request.body is always bytes, so we need to decode it as text.
            # decode(utf-8) means reat these bytes as text.
            body = request.body.decode('utf-8')
        except UnicodeDecodeError : 
            # if the body is not a string, just say it's binary, preventing the crashing.
            body =  f"<binary {len(request.body)} bytes>"
        captured ={
            'method' : request.method,
            'path' : request.path,
            'query' : request.META.get('QUERY_STRING',''),
            'body' : body,
            'headers' : dict(request.headers),
        }
        
        #print('[supervisualizer] request captured:',json.dumps(captured, ensure_ascii=False))
        # we can't simply dump the view, since its a function, so we need to get the view class and module name.
        queries =[]

        def capture_sql(execute, sql, params, many, context):
            start = time.monotonic()
            result = execute(sql, params, many, context)
            queries.append({
                "sql": sql,
                "params": list(params) if params else [],
                "duration_ms": round((time.monotonic() - start) * 1000, 2),
            })
            captured["sql"] = queries   
            return result

        def encode(value):
            if value is None or isinstance(value, (str, int, float, bool)):
                return {"type": type(value).__name__, "value": value}
            if isinstance(value, (list, tuple)):
                return {"type": "list", "value": [encode(item) for item in value]}
            if isinstance(value, dict):
                return {"type": "dict", "value": {str(key): encode(item) for key, item in value.items()}}
            if hasattr(value, "pk") and hasattr(value, "_meta"):
                return {"type": type(value).__name__ + " instance", "value": "pk=" + str(value.pk)}

            return {"type": type(value).__name__, "value": str(value)[:200]}

        validations = []

        original_is_valid = Serializer.is_valid

        def probed_is_valid(self, *args, **kwargs):
            result = original_is_valid(self, *args, **kwargs)
            if result:
                validations.append({
                    "serializer": type(self).__module__ + "." + type(self).__qualname__,
                    "data": encode(dict(self.validated_data)),
                })
            return result

        Serializer.is_valid = probed_is_valid

        renders = []

        original_render = Template.render

        def probed_render(self, *args, **kwargs):

            # Run the real render. Skip this and the page never becomes HTML.
            result = original_render(self, *args, **kwargs)
            # The view called t.render(context, request). args[0] is that dict.
            context = args[0] if args else kwargs.get("context")
            renders.append({
                # Inner compiled template. The filename the view asked for.
                "template": self.template.name,
                # The dict the view passed, not csrf_token / user. 
                "context": encode(dict(context) if context else {}),
            })
            return result

        Template.render = probed_render

        try:
            with connection.execute_wrapper(capture_sql):
                response = self.get_response(request)
        finally:
            Serializer.is_valid = original_is_valid
            # Always restore. Same reason as is_valid.
            Template.render = original_render

        captured["templates"] = renders



        

        captured["validations"] = validations
        captured["sql"] = queries
        # getattr is the function that gets the value of an attribute of an object
        # if the attribute is not found, it returns None, instead of crashing
        # we can't directly dump the view since its a function 
        # so we get the view class and module name. also using getattr to get the value of an attribute of an object.

        # Decode the body the same way you already decode request.body.
        # content is bytes. decode turns those bytes into text.
        try:
            response_body = response.content.decode("utf-8")
        except UnicodeDecodeError:
        # Not text (an image, etc.). Record the byte length instead of crashing.
            response_body = f"<binary {len(response.content)} bytes>"
        captured["response"] = {
            # The HTTP status. An int, JSON-safe as a number.
            "status": response.status_code,
            # Response headers. dict() makes it JSON-safe.
            "headers": dict(response.headers),
            # The body, now a string (or the binary placeholder above).
            "body": response_body,
            # Byte length of content. Count the bytes, not the decoded string.
            "size": len(response.content),
        }

        def class_name(value):
            if value is None:
                return None
            return value.__module__ + "." + value.__qualname__

        match = getattr(request, "resolver_match", None)
        if match is not None:
            func = match.func
            
            view_class = getattr(func, "view_class", None)
            if view_class is not None:
                view = view_class.__module__ + "." + view_class.__qualname__

                captured["permission_classes"] = [
                    class_name(permission)
                    for permission in getattr(view_class, "permission_classes", [])
                ]

                serializer_class = getattr(view_class, "serializer_class", None)
                captured["serializer_class"] = class_name(serializer_class)

                queryset = getattr(view_class, "queryset", None)
                model = getattr(queryset, "model", None)
                captured["queryset_model"] = class_name(model)

            else:
                view = func.__module__ + "." + func.__qualname__
            
            captured['route'] = match.route
            captured['url_name'] = match.url_name
            captured['view'] = view
            captured['kwargs'] = match.kwargs
        # json dumps turns the python object (captured) into a json string.
        # we have to use json foramt, which json accept : strings, numbers, booleans, lists, dictionaries, and None.
        # ensure_ascii=False is use to keep the original unicode characters, which '經典原味鍋' will be keep instead of \u7d93.


        # User and session are not in the URL. The Cookie header is only a
        # lookup number (sessionid=…). Django stored a dictionary on the
        # server for that number — the session — and built request.user
        # from it. Those attachments happen inside get_response, so we
        # read them here, same as the route. A 404 still has them; do not
        # nest this inside `if match`.
        # getattr: if Session/Auth middleware is missing, no crash.
        # json.dumps(request.user) fails — it is a live object, like match.func.
        # Logged out is still an object (AnonymousUser), not None.
        # is_authenticated is the bool. get_username() is a string ("" if
        # anonymous). Session: keys only, not values (table_number lives
        # here; later login adds _auth_user_id).
        user = getattr(request, "user", None)
        if user is not None:
            captured["is_authenticated"] = user.is_authenticated
            captured["username"] = user.get_username()

        session = getattr(request, "session", None)
        if session is not None:
            captured["session_keys"] = list(session.keys())


        stages = []

        stages.append({
            "id": "receive_input",
            "parent_id": None,
            "kind": "receive_input",
            "side": "server",
            "label": "HTTP request",
            "data": {
                "method": captured["method"],
                "path": captured["path"],
                "query": captured["query"],
                "body": captured["body"],
                "headers": captured["headers"],
            },
        })

        if "route" in captured:
            route_data = {
                "route": captured["route"],
                "url_name": captured["url_name"],
                "view": captured["view"],
                "kwargs": captured["kwargs"],
            }
            for key in ("permission_classes", "serializer_class", "queryset_model"):
                if key in captured:
                    route_data[key] = captured[key]
            stages.append({
                "id": "route",
                "parent_id": None,
                "kind": "route",
                "side": "server",
                "label": "URL dispatcher",
                "data": route_data,
            })

        if "username" in captured or "session_keys" in captured:
            stages.append({
                "id": "attach_context",
                "parent_id": None,
                "kind": "attach_context",
                "side": "server",
                "label": "Middleware (session, auth)",
                "data": {
                    "is_authenticated": captured.get("is_authenticated"),
                    "username": captured.get("username"),
                    "session_keys": captured.get("session_keys"),
                },
            })

        if validations:
            stages.append({
                "id": "validate_input",
                "parent_id": None,
                "kind": "validate_input",
                "side": "server",
                "label": "Serializer (in)",
                "data": {"validations": validations},
            })

        if renders:
            stages.append({
                "id": "render_output",
                "parent_id": None,
                "kind": "render_output",
                "side": "server",
                "label": "Template",
                "data": {"templates": renders},
            })

        stages.append({
            "id": "send_response",
            "parent_id": None,
            "kind": "send_response",
            "side": "server",
            "label": "HTTP response",
            "data": captured["response"],
        })

        TRACE_DIR = Path(settings.BASE_DIR) / "supervisualizer-traces"

        

        # end of __call__, replacing the print
        trace_id = uuid.uuid4().hex
        trace = {
            "trace_id": trace_id,
            "framework": "django",
            "started_at": started.isoformat(),
            "endpoint": {
                "method": captured["method"],
                "path": captured["path"],
                "route_pattern": captured.get("route"),
                "handler": captured.get("view"),
            },
            "stages": stages,
            "sql": captured["sql"],
            "notes": [],
        }

        TRACE_DIR.mkdir(parents=True, exist_ok=True)
        name = started.strftime("%Y%m%dT%H%M%S%f") + "-" + trace_id[:8] + ".json"
        with (TRACE_DIR / name).open("w", encoding="utf-8") as f:
            json.dump(trace, f, ensure_ascii=False, indent=2, default=str)

        return response