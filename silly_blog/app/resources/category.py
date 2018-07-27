#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from flask import g
import flask_restful as restful
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, post_load
from marshmallow.validate import Length

from silly_blog.app import api, db, auth
from silly_blog.app.models import Category
from silly_blog.contrib.utils import envelope_json_required, make_error_response


LOG = logging.getLogger(__name__)


class CreateCategorySchema(Schema):
    """Validate create category input"""
    name = fields.Str(required=True, validate=Length(min=1, max=255))
    description = fields.Str(validate=Length(max=255))
    display_order = fields.Int()
    protected = fields.Boolean()
    parent_id = fields.Str(validate=Length(max=64))

    @post_load
    def make_category(self, data):
        return Category.from_dict(data)


@api.resource("/categories/", methods=["POST", "GET"], endpoint="categories")
@api.resource("/categories/<string:category_id>", methods=["GET"], endpoint="category")
class CategoryResource(restful.Resource):
    """Controller for article category resources"""

    def __init__(self):
        super().__init__()
        self.post_schema = CreateCategorySchema()

    @staticmethod
    def _get_by_id(category_id):
        category = Category.query.get(category_id)
        if category:
            return {
                "category": category.to_dict()
            }
        else:
            return make_error_response(404, "category %r not found" % category_id)

    def get(self, category_id=None):
        """List categories or show details of a specified one."""
        if category_id:
            return self._get_by_id(category_id)

        categories = Category.query.all()
        return {
            "categories": [category.to_dict() for category in categories]
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
            return make_error_response(400, str(ex))
        else:
            return {
                "category": category.to_dict()
            }
