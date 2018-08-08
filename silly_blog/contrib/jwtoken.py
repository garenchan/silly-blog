"""
This module is a temporary substitute for `flask-jwt`.
For details, see `https://en.wikipedia.org/wiki/JSON_Web_Signature`
"""
from itsdangerous import (TimedJSONWebSignatureSerializer as JWSSerializer,
                          BadSignature, SignatureExpired)


class JSONWebSignature(object):

    def __init__(self, app=None):
        self.init_app(app)

    def init_app(self, app):
        if not app:
            return

        self.secret_key = app.config["SECRET_KEY"]
        self.salt = app.config.get("JWT_SALT")
        self.expires_in = app.config.get("JWT_EXPIRES_IN")
        self.algorithm = app.config.get("JWT_ALGORITHM")
        self.serializer = JWSSerializer(self.secret_key, self.expires_in,
                                        salt=self.salt,
                                        algorithm_name=self.algorithm)

    def encode(self, payload, tostr=True):
        """Encodes payload and returns a token."""
        _bytes = self.serializer.dumps(payload)
        return _bytes.decode("ascii") if tostr else _bytes

    def decode(self, token):
        """Decodes a token and returns playload object."""
        try:
            payload = self.serializer.loads(token)
        except (BadSignature, SignatureExpired):
            payload = None
        return payload

    def get_expires_in(self):
        """Get expire time, in seconds"""
        return self.serializer.expires_in
