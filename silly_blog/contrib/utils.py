"""
Some Utils For Self-Used Without Generality.
"""
import functools

from flask import g, request, jsonify
from flask.wrappers import BadRequest


def make_error_response(status, message, code=None):
    """Make a restful error response

    :param status: http status code
    :type status: int
    :param message: error message
    :type message: a json-able object
    :param code: internal error code
    :type code: none or int
    :return: a flask.wrappers.Response object
    """
    response = jsonify({
        "error": {
            "status": status,
            "message": message,
            "code": code,
        }
    })
    response.status_code = status
    return response


def json_required(func):
    """A decorator for view handler.
    Confirm the Content-Type of the request is json.

    :param func: a flask view handler
    :type func: callable
    :return: a wrapper function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return make_error_response(400, "JSON Params Expected")
        try:
            # force parse body as json
            _ = request.get_json()
        except BadRequest:
            return make_error_response(400, "JSON Params Expected")
        return func(*args, **kwargs)

    return wrapper


def envelope_json_required(envelope):
    """A decorator for view handler.

    If the request's json body with envelope looks like:
        {
            "envelope": {
                "arg1": "username",
                "arg2": "password",
            }
        }
    We uncover the envelope, after that we can access sealed dict like this:
        g.envelope -> {
                                "arg1": "username",
                                "arg2": "password",
                            }
    :param envelope: envelope for request arguments
    :type envelope: str
    :return: a wrapper function
    """
    if not isinstance(envelope, str):
        raise TypeError("Expected `envelope` to be a str")

    def decorating_function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return make_error_response(400, "JSON Params Expected")
            try:
                json = request.get_json()
            except BadRequest:
                return make_error_response(400, "Invalid JSON Params")
            else:
                if not isinstance(json, dict) or \
                        not isinstance(json.get(envelope), dict):
                    return make_error_response(400, "Invalid Params")
                # NOTE: don't set envelope attribute on `request`, because it
                # maybe override the original attribute value, `g` namespace
                # is more cleaner.
                setattr(g, envelope, json[envelope])
            return func(*args, **kwargs)

        return wrapper

    return decorating_function


def str2bool(value):
    """Rich convert a str to bool
    :param value: boolean-style string
    :param value: str
    :return: bool
    """
    assert isinstance(value, str)

    value = value.strip().lower()

    if value in ["true", "t", "yes", "y", "1"]:
        return True
    elif value in ["false", "f", "no", "n", "0"]:
        return False
    else:
        raise ValueError("Unknown boolean-style string %r" % value)
