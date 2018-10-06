"""
This module is a temporary substitute for `flask-jwt`.
For details, see `https://en.wikipedia.org/wiki/JSON_Web_Signature`
"""
from datetime import datetime, timedelta

from itsdangerous import TimedJSONWebSignatureSerializer as JWSSerializer
from itsdangerous import BadSignature, SignatureExpired


class JSONWebSignature(object):

    def __init__(self, app=None):
        self.init_app(app)

    def init_app(self, app):
        if not app:
            return

        self.secret_key = app.config['SECRET_KEY']
        self.salt = app.config.get('JWT_SALT')
        expires_in = app.config.get('JWT_EXPIRES_IN')
        self.algorithm = app.config.get('JWT_ALGORITHM')
        self.serializer = JWSSerializer(
            self.secret_key, expires_in,
            salt=self.salt, algorithm_name=self.algorithm)

    def encode(self, payload, tostr=True):
        """Encodes payload and returns a token."""
        issued_at = datetime.utcnow()
        expired_at = issued_at + timedelta(seconds=self.expires_in)
        _bytes = self.serializer.dumps(payload)
        return {
            'id': _bytes.decode('ascii') if tostr else _bytes,
            'issued_at': issued_at.isoformat() + 'Z',
            'expired_at': expired_at.isoformat() + 'Z'
        }

    def decode(self, token, return_header=False):
        """Decodes a token and returns playload object."""
        try:
            payload, header = self.serializer.loads(token, return_header=True)
        except (BadSignature, SignatureExpired):
            payload, header = None, None
        return payload if not return_header else (payload, header)

    def get_issue_date(self, header):
        """Get token's issue date by its header."""
        return self.serializer.get_issue_date(header)

    def get_expired_date(self, header):
        """Get token's expired date by its header"""
        rv = header.get('exp')
        if isinstance(rv, (int, float)):
            return datetime.utcfromtimestamp(int(rv))

    @property
    def expires_in(self):
        """Get expire time, in seconds"""
        return self.serializer.expires_in

    def get_detail(self, _id, header=None):
        """Get information for a token."""
        try:
            if header is None:
                _, header = self.decode(_id, return_header=True)
                if header is None:
                    return None
            issued_at = self.get_issue_date(header)
            expired_at = self.get_expired_date(header)
            if not all([issued_at, expired_at]):
                return None
            else:
                return {
                    'id': _id,
                    'issued_at': issued_at.isoformat() + 'Z',
                    'expired_at': expired_at.isoformat() + 'Z'
                }
        except Exception as ex:
            return None
