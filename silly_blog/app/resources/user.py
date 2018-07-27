#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from flask import g
import flask_restful as restful
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, post_load
from marshmallow.validate import Length, Email

from silly_blog.app import api, db, auth
from silly_blog.app.models import User
from silly_blog.contrib.utils import envelope_json_required, make_error_response


LOG = logging.getLogger(__name__)


class CreateUserSchema(Schema):
    """Validate create user input"""
    name = fields.Str(required=True, validate=Length(min=5, max=255))
    display_name = fields.Str(validate=Length(max=255))
    email = fields.Str(validate=[Length(max=255), Email()])
    password = fields.Str(required=True, validate=Length(min=6, max=64))
    enabled = fields.Boolean()
    role_id = fields.Str(validate=Length(max=64))

    @post_load
    def make_user(self, data):
        return User.from_dict(data)


@api.resource("/users/", methods=["POST", "GET"], endpoint="users")
@api.resource("/user/<string:user_id>", methods=["GET"], endpoint="user")
class UserResource(restful.Resource):
    """Controller for user resources"""

    def __init__(self):
        super().__init__()
        self.post_schema = CreateUserSchema()

    @staticmethod
    def _user_to_dict(user):
        """Get a dict of user's details"""
        info = user.to_dict()
        if user.local_user:
            info.update(user.local_user.to_dict())
        info["role"] = user.role.name if user.role else None
        return info

    def _get_by_id(self, user_id):
        user = User.get(user_id)
        if not user:
            return make_error_response(404, "user %r not found" % user_id)

        return {"user": self._user_to_dict(user)}

    def get(self, user_id=None):
        if user_id:
            return self._get_by_id(user_id)

        # TODO: DB QUERY OPTIMIZE
        users = User.query.options(db.joinedload(User.local_user)).options(
            db.joinedload(User.role)).all()
        return {"users": [self._user_to_dict(user) for user in users]}

    @auth.login_required
    @envelope_json_required("user")
    def post(self):
        """Create a user.

        Accept category as a dict that looks like:
            {
                "user": {
                    "name": "zhangsan",
                    "display_name": "san zhang",
                    "email": "zhangsan@gmail.com",
                    "password": "zhangsanblogpasswd",
                    "enabled": True,
                    "role_id": "2",
                }
            }
        """
        result = self.post_schema.load(g.user)
        if result.errors:
            return make_error_response(400, result.errors)

        try:
            user = result.data
            db.session.add(user)
            db.session.commit()
        except IntegrityError as ex:
            db.session.rollback()
            # TODO: make db-related error more human-readable
            return make_error_response(400, str(ex))
        else:
            return {"user": self._user_to_dict(user)}
