#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from flask import g, request
import flask_restful as restful
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.orm.attributes import InstrumentedAttribute
from marshmallow import Schema, fields, post_load
from marshmallow.validate import Length, Email

from silly_blog.app import db, auth
from silly_blog.app.resources import api
from silly_blog.app.models import User, LocalUser
from silly_blog.contrib.utils import (envelope_json_required,
                                      make_error_response,
                                      parse_isotime)


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


class UpdateUserSchema(Schema):
    """Validate update user input"""
    name = fields.Str(validate=Length(min=5, max=255))
    display_name = fields.Str(validate=Length(max=255))
    email = fields.Str(validate=[Length(max=255), Email()])
    password = fields.Str(validate=Length(min=6, max=64))
    enabled = fields.Boolean()
    role_id = fields.Str(validate=Length(max=64))


@api.resource("/users/",
              methods=["POST", "GET"],
              endpoint="users")
@api.resource("/users/<string:user_id>",
              methods=["GET", "PUT", "DELETE"],
              endpoint="user")
class UserResource(restful.Resource):
    """Controller for user resources"""

    post_schema = CreateUserSchema()
    put_schema = UpdateUserSchema()

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
            return make_error_response(404, "User %r not found" % user_id)

        return {"user": self._user_to_dict(user)}

    def get(self, user_id=None):
        if user_id:
            return self._get_by_id(user_id)

        # TODO: DB QUERY OPTIMIZE
        query = User.query.join(User.local_user)

        # filter by name or email
        name = request.args.get("name")
        if name is not None:
            # regexp maybe not supported, use like instead
            exp = LocalUser.name.like(''.join(['%', name, '%']))
            query = query.filter(exp)
        email = request.args.get("email")
        if email is not None:
            exp = LocalUser.email.like(''.join(['%', email, '%']))
            query = query.filter(exp)

        # since
        since = request.args.get("since")
        if since is not None:
            try:
                since = parse_isotime(since)
            except ValueError as ex:
                return make_error_response(400, str(ex))
            else:
                query = query.filter(LocalUser.created_at >= since)

        # order by related
        sort = request.args.get("sort", "updated_at")
        sort_attribute = getattr(LocalUser, sort, None)
        if not isinstance(sort_attribute, InstrumentedAttribute):
            return make_error_response(400, "Unknown sort %r" % sort)
        direction = request.args.get("direction", "desc")
        try:
            sort_method = getattr(sort_attribute, direction)
            sort_exp = sort_method()
            if not isinstance(sort_exp, UnaryExpression):
                raise TypeError("Not a unary expression!")
        except (AttributeError, TypeError):
            return make_error_response(400, "Unknown direction %r" % direction)
        else:
            query = query.order_by(sort_exp)

        # before offset and limit, we get the entry total number
        total = query.count()

        # offset limit related
        page = request.args.get("page", None)
        pagesize = request.args.get("pagesize", None)
        if page and pagesize:
            try:
                page = int(page)
            except ValueError:
                return make_error_response(400, "Unknown page %r" % page)
            try:
                pagesize = int(pagesize)
            except ValueError:
                return make_error_response(400, "Unknown pagesize %r" % pagesize)

            offset = (page - 1) * pagesize  # page starts from 1
            if offset < 0:
                offset = 0
            query = query.offset(offset).limit(pagesize)

        users = query.options(db.joinedload(User.local_user)).options(
            db.joinedload(User.role)).all()
        return {
            "users": [self._user_to_dict(user) for user in users],
            "total": total,
        }

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
        print("here")
        result = self.post_schema.load(g.user)
        if result.errors:
            return make_error_response(400, result.errors)

        try:
            user = result.data
            db.session.add(user)
            db.session.commit()
        except IntegrityError as ex:
            db.session.rollback()
            reason = str(ex.orig)
            if any(word in reason.lower() for word in ["duplicate", "unique"]):
                return make_error_response(409, reason)
            LOG.exception("An unknown db error occurred")
            return make_error_response(500, "DB Error", ex.code)
        else:
            return {"user": self._user_to_dict(user)}

    @auth.login_required
    @envelope_json_required("user")
    def put(self, user_id):
        """Update the editable attributes of an exitsing user.

        :param user_id: an exitsing user id.
        """
        result = self.put_schema.load(g.user)
        if result.errors:
            return make_error_response(400, result.errors)

        user = User.query.get(user_id)
        if not user:
            return make_error_response(404, "User %r not found" % user_id)
        try:
            user.update(**result.data)
        except IntegrityError as ex:
            db.session.rollback()
            reason = str(ex.orig)
            if any(word in reason.lower() for word in ["duplicate", "unique"]):
                return make_error_response(409, reason)
            LOG.exception("An unknown db error occurred")
            return make_error_response(500, "DB Error", ex.code)
        else:
            return {"user": self._user_to_dict(user)}

    @auth.login_required
    def delete(self, user_id):
        """Delete a exitsing user.

        :param tag_id: an exitsing user id.
        """
        user = User.query.get(user_id)
        if not user:
            return make_error_response(404, "User %r not found" % user_id)

        try:
            user.delete()
        except DatabaseError as ex:
            LOG.exception("An unknown db error occurred")
            return make_error_response(500, "DB Error", ex.code)
        else:
            return None, 204
