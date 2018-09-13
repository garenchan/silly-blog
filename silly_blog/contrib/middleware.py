# -*- coding: utf-8 -*-
from werkzeug.wsgi import LimitedStream, get_content_length
from werkzeug.exceptions import RequestEntityTooLarge


class SizeLimitStream(LimitedStream):
    """A wrapper for LimitedStream class."""

    def __new__(cls, stream, content_length, max_content_length):
        return (stream
                # means no limitation
                if all(i is None for i in (content_length, max_content_length))
                else super().__new__(cls))

    def __init__(self, stream, content_length, max_content_length):
        limit = content_length or max_content_length or 0
        if all(i is not None for i in (content_length, max_content_length)):
            limit = (content_length
                     if content_length <= max_content_length else 0)
        super().__init__(stream, limit)

    def on_exhausted(self):
        # TODO: detect whether size is outer of limit
        raise RequestEntityTooLarge()


class SizeLimitMiddleware(object):
    """Limit size of incoming request.

    It's unreasonable. Flask's MAX_CONTENT_LENGTH not work with json payload.
    So add a simple middleware to limit size of incoming request regardless
    of its content-type.
    https://github.com/pallets/werkzeug/issues/690
    """

    def __init__(self, app):
        self.app = app.wsgi_app
        self.max_content_length = app.config['MAX_CONTENT_LENGTH']

    def __call__(self, environ, start_response):
        stream = environ['wsgi.input']
        content_length = get_content_length(environ)
        environ['wsgi.input'] = SizeLimitStream(
            stream, content_length, self.max_content_length)
        return self.app(environ, start_response)
