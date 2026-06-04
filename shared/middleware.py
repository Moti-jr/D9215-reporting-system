from django.db import connection

class RLS_connection:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwds):
        if request.use.is_authenticated:
            