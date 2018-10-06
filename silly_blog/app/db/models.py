# -*- coding: utf-8 -*-
"""
SQLAlchemy models for silly blog.
"""
import uuid
from datetime import datetime

import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash

from silly_blog.app.db import db


def _uuid():
    return uuid.uuid4().hex


class IdMixin(object):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(32), default=_uuid, unique=True, nullable=False)


class TimestampMixin(object):
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ModelBase(db.Model, TimestampMixin, IdMixin):
    """Base class for models."""
    __abstract__ = True

    @classmethod
    def from_dict(cls, d):
        """Convert a dict to a model.

        :param d: a dict contains model's attributes
        :type d: dict
        """
        assert isinstance(d, dict)
        new_d = d.copy()
        return cls(**new_d)

    def to_dict(self):
        """Returns the model's attributes as a dictionary."""
        result = {}
        res = sqlalchemy.inspect(self)

        for c in self.__table__.columns:
            if c.key not in res.unloaded:
                try:
                    result[c.name] = getattr(self, c.name)
                except AttributeError:
                    pass

        for r in self.__mapper__.relationships:
            if r.key not in res.unloaded:
                result[r.key] = getattr(self, r.key)

        return result

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def update(self, *args, **kwargs):
        """Make the model object behave like a dict."""
        assert len(args) in (0, 1)
        if args:
            values = dict(args[0])
            values.update(kwargs)
        else:
            values = kwargs

        for k, v in values.items():
            setattr(self, k, v)


class RoleAssignment(ModelBase):
    __tablename__ = 'role_assignments'
    __table_args__ = (
        db.UniqueConstraint('user_uuid', 'role_uuid', name='user_role_unique'),
        db.Index('ix_user_uuid', 'user_uuid'))

    user_uuid = db.Column(
        db.String(32),
        db.ForeignKey('users.uuid', ondelete='CASCADE'),
        nullable=False)
    role_uuid = db.Column(
        db.String(32),
        db.ForeignKey('roles.uuid', ondelete='CASCADE'),
        nullable=False)


class Role(ModelBase):
    __tablename__ = 'roles'

    name = db.Column(db.String(128), unique=True, nullable=False)

    users = db.relationship(
        'User',
        secondary=RoleAssignment.__table__,
        backref=db.backref('roles'),
        lazy='dynamic')


class User(ModelBase):
    __tablename__ = 'users'

    username = db.Column(db.String(128), unique=True, nullable=False)
    nickname = db.Column(db.String(128))
    # TODO: use custom email type for validation
    email = db.Column(db.String(255), unique=True)
    _password = db.Column('password', db.String(128), nullable=False)
    enabled = db.Column(db.Boolean, default=True)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = generate_password_hash(value)

    @staticmethod
    def check_password(pwhash, password):
        """Check that a plaintext password matches hashed."""
        if not all([pwhash, password]):
            return False
        return check_password_hash(pwhash, password)


class Category(ModelBase):
    __tablename__ = 'categories'

    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    display_order = db.Column(db.Integer)
    protected = db.Column(db.Boolean, default=False)
    childless = db.Column(db.Boolean, default=False)
    parent_uuid = db.Column(db.String(32), db.ForeignKey('categories.uuid'))

    children = db.relationship(
        'Category',
        backref=db.backref('parent', remote_side='Category.uuid'),
        cascade='all,delete')


class Source(ModelBase):
    __tablename__ = 'sources'

    name = db.Column(db.String(32), unique=True, nullable=False)


class TagAssignment(ModelBase):
    __tablename__ = 'tag_assignments'
    __table_args__ = (
        db.UniqueConstraint('article_uuid', 'tag_uuid', name='article_tag_unique'),
        db.Index('ix_article_uuid', 'article_uuid'),
        db.Index('ix_tag_uuid', 'tag_uuid'))

    article_uuid = db.Column(
        db.String(32), db.ForeignKey('articles.uuid'), nullable=False)
    tag_uuid = db.Column(
        db.String(32), db.ForeignKey('tags.uuid'), nullable=False)


class Tag(ModelBase):
    __tablename__ = 'tags'

    name = db.Column(db.String(32), unique=True, nullable=False)

    articles = db.relationship(
        'Article',
        secondary=TagAssignment.__table__,
        backref=db.backref('tags'))


class Article(ModelBase):
    __tablename__ = 'articles'

    title = db.Column(db.String(255), nullable=False)
    content = db.deferred(db.Column(db.Text, nullable=False))
    summary = db.Column(db.String(255), default='')
    protected = db.Column(db.Boolean, default=False)
    stars = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    # Record the publication time of the article
    published_at = db.Column(db.DateTime, nullable=True)
    user_uuid = db.Column(
        db.String(32), db.ForeignKey(User.uuid), nullable=False)
    category_uuid = db.Column(
        db.String(32), db.ForeignKey(Category.uuid), nullable=False)
    source_uuid = db.Column(
        db.String(32), db.ForeignKey(Source.uuid), nullable=False)

    user = db.relationship(User, backref=db.backref('articles'))
    category = db.relationship(Category, backref=db.backref('articles'))
    source = db.relationship(Source, backref=db.backref('articles'))


class Comment(ModelBase):
    __tablename__ = 'comments'

    content = db.Column(db.Text, nullable=False)
    user_uuid = db.Column(
        db.String(32), db.ForeignKey(User.uuid), nullable=False)
    article_uuid = db.Column(
        db.String(32), db.ForeignKey(Article.uuid), nullable=False)

    article = db.relationship(Article, backref=db.backref('comments'))
