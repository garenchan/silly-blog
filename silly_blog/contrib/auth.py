"""
This module is a temporary substitute for `flask-httpauth` and `flask-login`.
As `flask-httpauth` only supports token auth with HTTP `Authorization` header,
but sometimes we expect to transfer token in custom headers like `X-Auth-Token`!
"""
import functools
from collections import Iterable

from flask import (_request_ctx_stack, request, make_response,
                   current_app, has_request_context)
from werkzeug.local import LocalProxy


class HTTPTokenAuth(object):
    """Get auth token from HTTP request's custom headers."""
    current_user = LocalProxy(lambda: _get_user())

    def __init__(self, keys, app=None):
        """
        :param keys: a str or a collection of strs.
            specify the HTTP request's header fields to carry token.
        """
        self.keys = keys

        self._user_callback = None
        # init auth failed callback
        self._unauthorized_callback = None
        self.unauthorized_handler(self._default_error_callback)

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.force_auth = app.config.get("FORCE_TOKEN_AUTH", True)
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["auth_manager"] = self

    @property
    def keys(self):
        return self._keys

    @keys.setter
    def keys(self, value):
        if isinstance(value, str) or not isinstance(value, Iterable):
            value = [value]
        for key in value:
            if not isinstance(key, str):
                raise ValueError("`value` should be a str or"
                                 "a collection of strs")
        self._keys = value

    def get_token(self):
        """Get token from request headers"""
        for key in self.keys:
            token = request.headers.get(key, "").strip()
            if token:
                return token
        else:
            return None

    def user_loader(self, callback):
        """A decorator for verify token callback.

        :param callback:  The callback for retrieving a user object.
        :type callback: callable

        The callback should be like this:
            @auth.user_loader
            def load_user(token):
                return User()
        """
        self._user_callback = callback
        return callback

    @staticmethod
    def _update_request_context_with_user(user):
        """Store the given user as ctx.user"""
        ctx = _request_ctx_stack.top
        ctx.auth_user = user

    def load_user(self):
        token = self.get_token()
        user = self._user_callback(token) if self._user_callback else None
        self._update_request_context_with_user(user)
        return user

    def unauthorized_handler(self, callback):
        """A decorator for auth failed callback

        :param callback: The callback for unauthorized users.
        :type callback: callable
        """
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            res = make_response(callback(*args, **kwargs))
            if res.status_code == 200:
                res.status_code = 401
            return res

        self._unauthorized_callback = wrapper
        return wrapper

    @staticmethod
    def _default_error_callback():
        """Default auth failed callback"""
        return "Unauthorized Access"

    def login_required(self, func):
        """A decorator for view handler.

        Implement access control for resources like this:
            @app.route("/")
            @auth.login_required
            def resource():
                pass
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.load_user() is None:
                if self.force_auth:
                    return self._unauthorized_callback()
            return func(*args, **kwargs)

        return wrapper


def _get_user():
    if has_request_context() and not hasattr(_request_ctx_stack.top, "auth_user"):
        current_app.extensions["auth_manager"].load_user()

    return getattr(_request_ctx_stack.top, "auth_user", None)
