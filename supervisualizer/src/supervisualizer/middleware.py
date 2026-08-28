# This file sits on every request and response to the server.
# currently its empty

import json


class SupervisualizerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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

        print('[supervisualizer] request captured:',json.dumps(captured, ensure_ascii=False))
        response = self.get_response(request)
        return response