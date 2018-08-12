#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging

from flask import g, request
import flask_restful as restful
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.orm.attributes import InstrumentedAttribute
from marshmallow import Schema, fields, post_load
from marshmallow.validate import Length

from silly_blog.app import api, db, auth
from silly_blog.app.models import Article, Tag
from silly_blog.contrib.utils import (envelope_json_required, str2bool,
                                      make_error_response, parse_isotime)


LOG = logging.getLogger(__name__)


class CreateArticleSchema(Schema):
    """Validate create article input"""
    title = fields.Str(required=True, validate=Length(min=1, max=255))
    summary = fields.Str(validate=Length(max=255))
    content = fields.Str(required=True, validate=Length(min=1))
    published = fields.Boolean()
    protected = fields.Boolean()
    category_id = fields.Str(required=True, validate=Length(max=64))
    source_id = fields.Str(required=True, validate=Length(max=64))
    user_id = fields.Str(validate=Length(max=64))
    tags = fields.List(fields.Dict())


class UpdateArticleSchema(Schema):
    """Validate update article input"""
    title = fields.Str(validate=Length(min=1, max=255))
    summary = fields.Str(validate=Length(max=255))
    content = fields.Str(validate=Length(min=1))
    published = fields.Boolean()
    protected = fields.Boolean()
    category_id = fields.Str(validate=Length(max=64))
    source_id = fields.Str(validate=Length(max=64))
    tags = fields.List(fields.Dict())


@api.resource("/articles/",
              methods=["POST", "GET"],
              endpoint="articles")
@api.resource("/articles/<string:article_id>",
              methods=["GET", "PUT"],
              endpoint="article")
class ArticleResource(restful.Resource):
    """Controller for article resources"""

    def __init__(self):
        super().__init__()
        self.post_schema = CreateArticleSchema()
        self.put_schema = UpdateArticleSchema()

    @staticmethod
    def _article_to_dict(article, content=False):
        """Get a dict of article's details"""
        info = article.to_dict(content=content)
        info["user"] = article.user.name
        # article's categories is a list with hierarchies
        info["category"] = []
        category = article.category
        while category:
            info["category"].insert(0, category.name)
            category = category.parent

        info["source"] = article.source.name
        info["tags"] = [tag.name for tag in article.get_tags()]

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
        published = request.args.get("published")
        if published is not None:
            published = str2bool(published)
            query = query.filter_by(published=published)
        # filter by `user_id`
        user_id = request.args.get("user_id")
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        # filter by `category_id`
        category_id = request.args.get("category_id")
        if category_id is not None:
            query = query.filter_by(category_id=category_id)
        # filter by `source_id`
        source_id = request.args.get("source_id")
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

        tags = result.data.pop("tags", [])
        # NOTE: we respect `user_id` only when `current_user` is admin.
        user_id = result.data.pop("user_id", None)
        published = result.data.get("published")
        article = Article.from_dict(result.data)
        article.user = auth.current_user
        if published:
            article.published_at = datetime.datetime.utcnow()

        for _tag in tags:
            tag_id = _tag.get("id")
            tag_name = _tag.get("name")
            tag = None
            if tag_id:
                tag = Tag.query.get(tag_id)
            elif tag_name:
                tag = Tag(name=tag_name)
                try:
                    db.session.add(tag)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                article.tags.append(tag)

        try:
            db.session.add(article)
            db.session.commit()
        except DatabaseError as ex:
            LOG.exception("An unknown db error occurred")
            return make_error_response(500, "DB Error", ex.code)
        else:
            return {"article": self._article_to_dict(article)}

    @auth.login_required
    @envelope_json_required("article")
    def put(self, article_id):
        """Update the editable attributes of an exitsing article.

        :param article_id:
        :return:
        """
        result = self.put_schema.load(g.article)
        if result.errors:
            return make_error_response(400, result.errors)

        article = Article.query.get(article_id)
        if not article:
            return make_error_response(404, "Article %r not found" % article_id)

        published = result.data.pop("published", None)
        if not article.published and published:
            # NOTE: can only publish once and after that can't be changed
            article.published = published
            article.published_at = datetime.datetime.utcnow()

        tags = result.data.pop("tags", [])
        article.update(**result.data)

        # clear tags first and add
        if tags:
            article.tags = []
            db.session.add(article)
        for _tag in tags:
            tag_id = _tag.get("id")
            tag_name = _tag.get("name")
            tag = None
            if tag_id:
                tag = Tag.query.get(tag_id)
            elif tag_name:
                tag = Tag(name=tag_name)
                try:
                    db.session.add(tag)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                article.tags.append(tag)

        try:
            db.session.add(article)
            db.session.commit()
        except DatabaseError as ex:
            LOG.exception("An unknown db error occurred")
            return make_error_response(500, "DB Error", ex.code)
        else:
            return {"article": self._article_to_dict(article)}
