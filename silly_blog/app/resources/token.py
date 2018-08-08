#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging

from flask import g
import flask_restful as restful
from marshmallow import Schema, fields
from marshmallow.validate import Length

from silly_blog.app import api, auth, jws
from silly_blog.app.models import User
from silly_blog.contrib.utils import envelope_json_required, make_error_response


LOG = logging.getLogger(__name__)


class GenerateTokenSchema(Schema):
    """Validate generate token input"""
    username = fields.Str(required=True, validate=Length(min=1, max=255))
    password = fields.Str(required=True, validate=Length(min=1, max=64))


@api.resource("/tokens")
class AuthResource(restful.Resource):

    def __init__(self):
        super().__init__()
        self.post_schema = GenerateTokenSchema()

    @auth.login_required
    def get(self):
        user = auth.current_user
        if not user:
            return make_error_response(401, "Unauthorized Access")

        return {
            "token": {
                "id": auth.get_token(),
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role.name,
                },
            }
        }

    @envelope_json_required("auth")
    def post(self):
        """Password authentication and return a token.

        Accept auth as a dict that looks like::
            {
                "auth": {
                    "username": "user1",
                    "password": "passwd",
                }
            }
        """
        result = self.post_schema.load(g.auth)
        if result.errors:
            return make_error_response(400, result.errors)

        user = User.get(name_email=result.data["username"])
        if not user:
            return make_error_response(401, "Invalid username or email")
        elif not user.check_password(result.data["password"]):
            return make_error_response(401, "Invalid password")
        else:
            now = datetime.datetime.utcnow()
            expired_at = now + datetime.timedelta(
                seconds=jws.get_expires_in())
            return {
                "token": {
                    "id": user.generate_auth_token(),
                    "issued_at": now.isoformat() + 'Z',
                    "expired_at": expired_at.isoformat() + 'Z',
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "role": user.role.name,
                    },
                }
            }
