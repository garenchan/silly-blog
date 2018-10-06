"""
Some Utils For Self-Used Without Generality.
"""
import datetime
import functools

from flask import g, request, jsonify
from flask.wrappers import BadRequest
from marshmallow import Schema
import iso8601


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


def _check_json_body():
    """Check whether request content is json"""
    if not request.is_json:
        return make_error_response(400, "JSON Params Expected")
    try:
        # force parse body as json
        _ = request.get_json()
    except BadRequest:
        return make_error_response(400, "JSON Params Expected")
    return None


def json_required(func):
    """A decorator for view handler.
    Confirm the Content-Type of the request is json.

    :param func: a flask view handler
    :type func: callable
    :return: a wrapper function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return _check_json_body() or func(*args, **kwargs)

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
            res = _check_json_body()
            if res:
                return res

            json = request.json
            if not isinstance(json, dict) or \
                    not isinstance(json.get(envelope), dict):
                return make_error_response(400, "Invalid JSON Params")
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


# time related
def isotime(at=None):
    """Stringify time in ISO 8601 format."""
    if not at:
        at = datetime.datetime.utcnow()
    st = at.isoformat()
    tz = at.tzinfo.tzname(None) if at.tzinfo else "UTC"
    st += ('Z' if tz in ("UTC", "UTC+00:00") else tz)
    return st


def parse_isotime(timestr):
    """Parse time from ISO 8601 format."""
    try:
        return iso8601.parse_date(timestr)
    except iso8601.ParseError as ex:
        raise ValueError(str(ex))


def require_json_envelope(envelope: str, schema: Schema=None):
    """Decorator to require a data in json envelope.

    This can only be used in classes and the second argument to the wrapped
    function must be the data (after self).
    :param envelope: envelope name
    :type envelope: str
    :param schema: a schema used for data validation
    :type envelope: marshmallow.Schema
    """
    def decorating_function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = _check_json_body()
            if res:
                return res

            # Check the basic format of the data.
            json = request.json
            if (not isinstance(json, dict) or
                    not isinstance(json.get(envelope), dict)):
                return make_error_response(400, 'Invalid JSON Params')

            # Use schema for data validation.
            data = json[envelope]
            if schema:
                result = schema.load(data)
                if result.errors:
                    return make_error_response(400, result.errors)
                data = result.data

            # Injection data as parameter.
            # TODO: check whether outside of class and make data as the first arg.
            args = list(args)
            args.insert(1, data)

            return func(*args, **kwargs)
        return wrapper
    return decorating_function
