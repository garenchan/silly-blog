#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from flask import g, request
import flask_restful as restful
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.orm.attributes import InstrumentedAttribute
from marshmallow import Schema, fields, post_load
from marshmallow.validate import Length

from silly_blog.app import api, db, auth
from silly_blog.app.models import Category
from silly_blog.contrib.utils import (envelope_json_required,
                                      make_error_response,
                                      parse_isotime)


LOG = logging.getLogger(__name__)


class CreateCategorySchema(Schema):
    """Validate create category input"""
    name = fields.Str(required=True, validate=Length(min=1, max=255))
    description = fields.Str(validate=Length(max=255))
    display_order = fields.Int()
    display_order2 = fields.Str()
    protected = fields.Boolean()
    parent_id = fields.Str(validate=Length(max=64))

    @post_load
    def make_category(self, data):
        display_order = data.get("display_order")
        parent_id = data.get("parent_id")
        display_order2 = data.pop("display_order2", None)
        if display_order is None and display_order2:
            data["display_order"] = Category.get_default_order(
                parent_id=parent_id, method=display_order2)
        return Category.from_dict(data)


class UpdateCategorySchema(Schema):
    """Validate update category input"""
    name = fields.Str(validate=Length(min=1, max=255))
    description = fields.Str(validate=Length(max=255))
    display_order = fields.Int()
    protected = fields.Boolean()
    parent_id = fields.Str(validate=Length(max=64))


@api.resource("/categories/",
              methods=["POST", "GET"],
              endpoint="categories")
@api.resource("/categories/<string:category_id>",
              methods=["GET", "PUT", "DELETE"],
              endpoint="category")
class CategoryResource(restful.Resource):
    """Controller for article category resources"""

    def __init__(self):
        super().__init__()
        self.post_schema = CreateCategorySchema()
        self.put_schema = UpdateCategorySchema()

    @staticmethod
    def _get_by_id(category_id):
        category = Category.query.get(category_id)
        if not category:
            return make_error_response(404, "Category %r not found" % category_id)
        return {"category": category.to_dict()}

    def get(self, category_id=None):
        """List categories or show details of a specified one."""
        if category_id:
            return self._get_by_id(category_id)

        query = Category.query

        # filter by parent_id
        if "parent_id" in request.args:
            # NOTE: if parent_id is empty string, it is equivalent to None
            parent_id = request.args["parent_id"] or None
            query = query.filter_by(parent_id=parent_id)

        # filter by name or description
        search_attrs = ("name", "description")
        for attr in search_attrs:
            search_val = request.args.get(attr)
            if search_val is not None:
                exp = getattr(Category, attr).like(''.join(['%', search_val, '%']))
                query = query.filter(exp)

        # since
        since = request.args.get("since")
        if since is not None:
            try:
                since = parse_isotime(since)
            except ValueError as ex:
                return make_error_response(400, str(ex))
            else:
                query = query.filter(Category.updated_at >= since)

        # order by related
        sort = request.args.get("sort", "display_order")
        sort_attribute = getattr(Category, sort, None)
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

        categories = query.all()
        return {
            "categories": [category.to_dict() for category in categories],
            "total": total,
        }

    @auth.login_required
    @envelope_json_required("category")
    def post(self):
        """Create a article category.

        Accept category as a dict that looks like:
            {
                "category": {
                    "name": "db",
                    "description": "db related",
                    "display_order": 1,
                    "protected": False,
                    "parent_id": "767324455b2b4a6c9afc35331c0c14d0",
                }
            }
        """
        result = self.post_schema.load(g.category)
        if result.errors:
            return make_error_response(400, result.errors)

        try:
            category = result.data
            db.session.add(category)
            db.session.commit()
        except IntegrityError as ex:
            db.session.rollback()
            reason = str(ex.orig)
            if any(word in reason.lower() for word in ["duplicate", "unique"]):
                return make_error_response(409, reason)
            LOG.exception("An unknown db error occurred")
            return make_error_response(500, "DB Error", ex.code)
        else:
            return {
                "category": category.to_dict()
            }

    @auth.login_required
    @envelope_json_required("category")
    def put(self, category_id):
        """Update the editable attributes of an exitsing category.

        :param category_id: an exitsing category id.
        """
        result = self.put_schema.load(g.category)
        if result.errors:
            return make_error_response(400, result.errors)

        category = Category.query.get(category_id)
        if not category:
            return make_error_response(404, "Category %r not found" % category_id)
        try:
            category.update(**result.data)
        except IntegrityError as ex:
            db.session.rollback()
            reason = str(ex.orig)
            if any(word in reason.lower() for word in ["duplicate", "unique"]):
                return make_error_response(409, reason)
            LOG.exception("An unknown db error occurred")
            return make_error_response(500, "DB Error", ex.code)
        else:
            return {"category": category.to_dict()}

    @auth.login_required
    def delete(self, category_id):
        """Delete a exitsing category.

        :param tag_id: an exitsing category id.
        """
        category = Category.query.get(category_id)
        if not category:
            return make_error_response(404, "Category %r not found" % category_id)

        try:
            category.delete()
        except DatabaseError as ex:
            LOG.exception("An unknown db error occurred")
            return make_error_response(500, "DB Error", ex.code)
        else:
            return None, 204
