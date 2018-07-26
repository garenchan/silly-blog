#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging

from flask import request
import flask_restful as restful
from flask_restful import fields, marshal_with, reqparse

from silly_blog.app import api, jws
from silly_blog.app.models import User, Role
from silly_blog.contrib.utils import envelope_json_required, make_error_response


LOG = logging.getLogger(__name__)


@api.resource("/tokens")
class AuthResource(restful.Resource):

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
        try:
            auth_context = request.auth
            username = auth_context["username"]
            password = auth_context["password"]
        except KeyError as ex:
            return make_error_response(400, "Params Error: %r" % ex.args[0])
        else:
            user = User.get(name_email=username)
            if not user:
                return make_error_response(401, "Invalid username or email")
            elif not user.check_password(password):
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
                            "is_admin": user.role.name == Role.ADMINISTRATOR,
                        },
                    }
                }
