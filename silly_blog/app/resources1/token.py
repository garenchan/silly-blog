# -*- coding: utf-8 -*-
import logging

from flask import g
import flask_restful as restful
from marshmallow import Schema, fields
from marshmallow.validate import Length

from silly_blog.app import jws, auth
from silly_blog.app.resources1 import api
from silly_blog.app.db.api import UserDBAPI, RoleAssignmentDBAPI
from silly_blog.contrib.utils import (
    make_error_response, require_json_envelope)


LOG = logging.getLogger(__name__)


def generate_auth_token(user: dict) -> dict:
    """Generate a `JWS` token for user"""
    payload = {
        'id': user['id'],
        'uuid': user['uuid'],
    }
    return jws.encode(payload)


def verify_auth_token(token: str):
    """Verify auth token and returns a user object."""
    try:
        payload, header = jws.decode(token, return_header=True)
    except Exception:
        LOG.exception('Verify auth token {!r} failed'.format(token))
        payload, header = None, None
        return None
    else:
        return (UserDBAPI.get(payload['id'])
                if payload and payload.get('id') else None)
    finally:
        # Cache token datas for later use
        g.auth_token = {
            'id': token,
            'payload': payload,
            'header': header
        }


@auth.user_loader
def _load_user(token):
    """Register loader user callback for `HTTPTokenAuth`"""
    if not token:
        return None

    return verify_auth_token(token)


class GenerateTokenSchema(Schema):
    """Validate generate token input"""
    username = fields.Str(required=True, validate=Length(min=1, max=255))
    password = fields.Str(required=True, validate=Length(min=1, max=64))


@api.resource('/tokens', methods=['GET', 'POST'], endpoint='tokens')
class TokenResource(restful.Resource):
    """Token Resource"""

    @staticmethod
    def _user_info(user):
        _roles = RoleAssignmentDBAPI.get_roles_by_user_uuid(user['uuid'])
        return {
            'id': user['id'],
            'uuid': user['uuid'],
            'name': user['nickname'] or user['username'],
            'roles': [role['name'] for role in _roles]
        }

    @auth.login_required
    def get(self):
        """Validates and shows information for a token."""
        token_id = g.auth_token['id']
        token_header = g.auth_token['header']
        token = jws.get_detail(token_id, token_header)
        token['user'] = self._user_info(auth.current_user)
        return dict(token=token)

    @require_json_envelope('auth', schema=GenerateTokenSchema())
    def post(self, auth):
        """Password authentication and return a token.

        Accept auth as a dict that looks like::
            {
                "auth": {
                    "username": "hanmei",
                    "password": "passwd",
                }
            }
        """
        user = UserDBAPI.get_by_username_email(auth['username'])
        if not user:
            return make_error_response(401, 'Invalid username or email')
        elif not UserDBAPI.check_password(user, auth['password']):
            return make_error_response(401, 'Invalid password')

        token = generate_auth_token(user)
        token['user'] = self._user_info(user)
        return dict(token=token)
