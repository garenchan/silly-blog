#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from flask import g, request
import flask_restful as restful
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.orm.attributes import InstrumentedAttribute
from marshmallow import Schema, fields, post_load
from marshmallow.validate import Length

from silly_blog.app import api, db, auth
from silly_blog.app.models import Article
from silly_blog.contrib.utils import (envelope_json_required, str2bool,
                                      make_error_response, parse_isotime)


LOG = logging.getLogger(__name__)


class CreateArticleSchema(Schema):
    """Validate create article input"""
    title = fields.Str(required=True, validate=Length(min=1, max=255))
    summary = fields.Str(validate=Length(max=255))
    content = fields.Str(required=True)
    published = fields.Boolean()
    category_id = fields.Str(required=True, validate=Length(max=64))
    source_id = fields.Str(required=True, validate=Length(max=64))
    tags = fields.Dict()

    @post_load
    def make_article(self, data):
        return Article.from_dict(data)


@api.resource("/articles/",
              methods=["POST", "GET"],
              endpoint="articles")
@api.resource("/articles/<string:article_id>",
              methods=["GET"],
              endpoint="article")
class ArticleResource(restful.Resource):
    """Controller for article resources"""

    def __init__(self):
        super().__init__()
        self.post_schema = CreateArticleSchema()

    @staticmethod
    def _article_to_dict(article, content=False):
        """Get a dict of article's details"""
        info = article.to_dict(content=content)
        info["user"] = article.user.name
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

        # since
        since = request.args.get("since")
        if since is not None:
            try:
                since = parse_isotime(since)
            except ValueError as ex:
                return make_error_response(400, str(ex))
            else:
                query = query.filter(Article.updated_at >= since)

        # order by related
        sort = request.args.get("sort", "published_at")
        sort_attribute = getattr(Article, sort, None)
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

        articles = query.all()
        # with content or not
        content = request.args.get("content", False)
        return {
            "articles": [self._article_to_dict(article, content=content)
                         for article in articles],
            "total": total,
        }

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
        result = self.post_schema.load(g.article)
        if result.errors:
            return make_error_response(400, result.errors)
