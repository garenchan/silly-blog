#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from flask import g
import flask_restful as restful
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, post_load
from marshmallow.validate import Length

from silly_blog.app import api, db, auth
from silly_blog.app.models import Tag
from silly_blog.contrib.utils import envelope_json_required, make_error_response


LOG = logging.getLogger(__name__)


class CreateTagSchema(Schema):
    """Validate create tag input"""
    name = fields.Str(required=True, validate=Length(min=1, max=64))

    @post_load
    def make_tag(self, data):
        return Tag.from_dict(data)


@api.resource("/tags/", methods=["POST", "GET"], endpoint="tags")
@api.resource("/tags/<string:tag_id>", methods=["GET"], endpoint="tag")
class TagResource(restful.Resource):
    """Controller for article tag resources"""

    def __init__(self):
        super().__init__()
        self.post_schema = CreateTagSchema()

    @staticmethod
    def _get_by_id(tag_id):
        tag = Tag.query.get(tag_id)
        if tag:
            return {
                "tag": tag.to_dict()
            }
        else:
            return make_error_response(404, "tag %r not found" % tag_id)

    def get(self, tag_id=None):
        """List tags or show details of a specified one."""
        if tag_id:
            return self._get_by_id(tag_id)

        tags = Tag.query.all()
        return {
            "tags": [tag.to_dict() for tag in tags]
        }

    @auth.login_required
    @envelope_json_required("tag")
    def post(self):
        """Create a article tag.

        Accept tag as a dict that looks like:
            {
                "tag": {
                    "name": "db",
                }
            }
        """
        result = self.post_schema.load(g.tag)
        if result.errors:
            return make_error_response(400, result.errors)

        try:
            tag = result.data
            db.session.add(tag)
            db.session.commit()
        except IntegrityError as ex:
            db.session.rollback()
            return make_error_response(400, str(ex))
        else:
            return {
                "tag": tag.to_dict()
            }
