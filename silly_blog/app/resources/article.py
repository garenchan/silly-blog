#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from flask import g, request
import flask_restful as restful
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import UnaryExpression
from marshmallow import Schema, fields, post_load
from marshmallow.validate import Length, Email

from silly_blog.app import api, db, auth
from silly_blog.app.models import Article
from silly_blog.contrib.utils import (envelope_json_required, str2bool,
                                      make_error_response)


LOG = logging.getLogger(__name__)


class CreateArticleSchema(Schema):
    """Validate create article input"""
    title = fields.Str(required=True, validate=Length(min=1, max=255))
    summary = fields.Str(validate=Length(max=255))
    content = fields.Str(required=True)
    published = fields.Boolean()
    category_id = fields.Str(required=True, validate=Length(max=64))
    source_id = fields.Str(required=True, validate=Length(max=64))
    tags = fields.Dict(values=fields.List(fields.Str(validate=Length(max=64))),
                       keys=fields.Str())

    @post_load
    def make_article(self, data):
        return Article.from_dict(data)


@api.resource("/articles/", methods=["POST", "GET"], endpoint="articles")
@api.resource("/articles/<string:article_id>", methods=["GET"], endpoint="article")
class ArticleResource(restful.Resource):
    """Controller for article resources"""

    def __init__(self):
        super().__init__()
        self.post_schema = CreateArticleSchema()

    @staticmethod
    def _article_to_dict(article, content=False):
        """Get a dict of article's details"""
        info = article.to_dict(content=content)
        info["category"] = article.category.name
        info["source"] = article.source.name
        info["tags"] = [tag.name for tag in article.tags]

        return info

    def _get_by_id(self, article_id):
        article = Article.query.get(article_id)
        if not article:
            return make_error_response(404, "article %r not found" % article_id)

        return {"article": self._article_to_dict(article, content=True)}

    def get(self, article_id=None):
        if article_id:
            return self._get_by_id(article_id)

        query = Article.query
        # filter by `published` field, `None` means nothing to do.
        published = request.args.get("published", None)
        if published is not None:
            published = str2bool(published)
            query = query.filter_by(published=published)
        # filter by `user_id`
        user_id = request.args.get("user_id", None)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        # filter by `category_id`
        category_id = request.args.get("category_id", None)
        if category_id is not None:
            query = query.filter_by(category_id=category_id)
        # filter by `source_id`
        source_id = request.args.get("source_id", None)
        if source_id is not None:
            query = query.filter_by(source_id=source_id)

        # order by related
        sort_key = request.args.get("sort_key", "published_at")
        sort_attribute = getattr(Article, sort_key, None)
        if not isinstance(sort_attribute, InstrumentedAttribute):
            return make_error_response(400, "Unknown sort_key %r" % sort_key)
        sort_dir = request.args.get("sort_dir", "desc")
        try:
            sort_dir_method = getattr(sort_attribute, sort_dir)
            sort_exp = sort_dir_method()
            if not isinstance(sort_exp, UnaryExpression):
                raise TypeError("Not a unary expression!")
        except (AttributeError, TypeError):
            return make_error_response(400, "Unknown sort_dir %r" % sort_dir)
        else:
            query = query.order_by(sort_exp)

        # offset limit related
        offset = request.args.get("offset", 0)
        if offset != 0:
            try:
                offset = int(offset)
            except ValueError:
                return make_error_response(400, "Unknown offset %r" % offset)
        query = query.offset(offset)
        limit = request.args.get("limit", 10)
        if limit != 10:
            try:
                limit = int(limit)
            except ValueError:
                return make_error_response(400, "Unknown limit %r" % limit)
        query = query.limit(limit)

        articles = query.all()
        # with content or not
        content = request.args.get("content", False)
        return {"articles": [self._article_to_dict(article, content=content)
                             for article in articles]}

    @auth.login_required
    @envelope_json_required("article")
    def post(self):
        """Create a article.

        Accept article as a dict that looks like:
            {
                "article": {
                    "title": "db",
                    "summary": "db related",
                    "content": "",
                    "published": True,
                    "category_id": "767324455b2b4a6c9afc35331c0c14d0",
                    "source_id": "0484d56615ac49f381876ca1112cccd7",
                    "tags": "",
                }
            }
        """
