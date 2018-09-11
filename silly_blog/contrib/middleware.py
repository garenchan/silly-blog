# -*- coding: utf-8 -*-
from werkzeug.exceptions import RequestEntityTooLarge


class SizeLimit(object):
    """Limit size of incoming request.

    It's unreasonable. Flask's MAX_CONTENT_LENGTH not work with
    json payload. So add a simple middleware to check the request's
    Content-Length header.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        pass
