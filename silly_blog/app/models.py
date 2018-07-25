#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import uuid
import logging

from flask import g
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property

from silly_blog.app import db, auth, jws


LOG = logging.getLogger(__file__)


class IdMixin(object):
    """ID Mixin"""
    id = db.Column(db.Integer, primary_key=True)


def _get_uuid():
    """Returns a string-type uuid"""
    return uuid.uuid4().hex


class UUIDMixin(object):
    """UUID Mixin"""
    id = db.Column(db.String(64), primary_key=True, default=_get_uuid)


class TimestampMixin(object):
    """Timestamp Mixin"""
    created_at = db.Column(db.TIMESTAMP, default=time.time)
    updated_at = db.Column(db.TIMESTAMP, default=time.time)


class ModelBase(db.Model):
    """Extended base model class"""
    __abstract__ = True

    @classmethod
    def from_dict(cls, d: dict):
        """Returns a model instance from a dictionary."""
        new_d = d.copy()
        return cls(**new_d)

    def to_dict(self):
        """Returns the models'a attributes as a dictionary."""
        names = (column.name for column in self.__table__.columns)
        return {name: getattr(self, name) for name in names}

    def __str__(self):
        """Convert model instance to string.

        ModelBase subclasses can override this to custom str().
        """
        identifier = None
        if hasattr(self, "name"):
            identifier = self.name
        elif hasattr(self, "title"):
            identifier = self.title
        elif hasattr(self, "id"):
            identifier = self.id
        return "<{0} {1!r}>".format(self.__class__.__name__, identifier)
    __repr__ = __str__


class Role(IdMixin, ModelBase):
    """User Role model

    Use for RBAC(Role-Based Access Control)!
    """
    __tablename__ = "roles"

    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    users = db.relationship("User", backref="role", lazy="dynamic")

    # role constants
    ADMINISTRATOR = "administrator"
    COMMON_USER = "common-user"

    @classmethod
    def insert_default_values(cls):
        for attr in dir(cls):
            if attr.startswith('_') or not attr.isupper():
                continue
            name = getattr(cls, attr, None)
            if not isinstance(name, str):
                continue

            role = Role(name=name, description=attr)
            db.session.add(role)
        db.session.commit()


class FederatedUser(IdMixin, ModelBase):
    """Federated User Model

    Use for third party auth!
    """
    __tablename__ = "federated_users"

    user_id = db.Column(db.String(64),
                        db.ForeignKey("users.id", ondelete="CASCADE"))
    idp_name = db.Column(db.String(64), nullable=False)
    protocol = db.Column(db.String(64), nullable=False)
    unique_id = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255), nullable=True)


class LocalUser(IdMixin, ModelBase):
    """Local User Model"""
    __tablename__ = "local_users"

    user_id = db.Column(db.String(64),
                        db.ForeignKey("users.id", ondelete="CASCADE"),
                        unique=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    display_name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(128), nullable=False)


class User(UUIDMixin, ModelBase):
    """User Model"""
    __tablename__ = "users"

    role_id = db.Column(db.Integer,
                        db.ForeignKey("roles.id", ondelete="CASCADE"))
    enabled = db.Column(db.Boolean)
    local_user = db.relationship("LocalUser", uselist=False, lazy="subquery",
                                 backref="user", cascade="all,delete-orphan")
    federated_users = db.relationship("FederatedUser", single_parent=True,
                                      lazy="subquery", backref="user",
                                      cascade="all,delete-orphan")
    articles = db.relationship("Article", lazy="dynamic",
                               backref=db.backref("author", lazy="subquery"))

    @hybrid_property
    def name(self):
        if self.local_user:
            return self.local_user.name
        elif self.federated_users:
            return self.federated_users[0].unique_id
        else:
            return None

    @hybrid_property
    def display_name(self):
        if self.local_user:
            return self.local_user.display_name or self.local_user.name
        elif self.federated_users:
            return self.federated_users[0].display_name
        else:
            return None

    @display_name.setter
    def display_name(self, value):
        if not self.local_user:
            self.local_user = LocalUser()
        self.local_user.display_name = value

    @hybrid_property
    def password(self):
        if self.local_user:
            return self.local_user.password
        else:
            return None

    @password.setter
    def password(self, value):
        if not self.local_user:
            self.local_user = LocalUser()
        self.local_user.password = generate_password_hash(value)

    def check_password(self, password: str):
        """Check that a plaintext password matches hashed."""
        if self.password is None or password is None:
            return False
        return check_password_hash(self.password, password)

    def generate_auth_token(self):
        """Generate a `JWS` token for user"""
        data = dict(id=self.id)
        return jws.encode(data)

    @staticmethod
    def verify_auth_token(token):
        """Verify auth token and returns a user object."""
        try:
            data = jws.decode(token)
            user_id = data["id"]
        except Exception:
            LOG.exception("Verify auth token {!r} failed".format(token))
            return None
        else:
            return User.query.get(user_id)

    @staticmethod
    def insert_default_values():
        users = [
            {"name": "admin",
             "password": "admin123",
             "role": Role.ADMINISTRATOR},
            {"name": "common",
             "password": "common123",
             "role": Role.COMMON_USER},
        ]
        for info in users:
            local_user = LocalUser.query.filter_by(name=info["name"]).first()
            if local_user:
                continue
            user = User(enabled=True)
            user.role = Role.query.filter_by(name=info.pop("role")).first()
            user.local_user = LocalUser.from_dict(info)
            db.session.add(user)
        db.session.commit()


@auth.user_loader
def _load_user(token):
    """Register loader user callback for `HTTPTokenAuth`"""
    if not token:
        return None

    return User.verify_auth_token(token)


class Category(UUIDMixin, ModelBase):
    """Article Category Model"""
    __tablename__ = "categories"

    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer)
    protected = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.String(64),
                          db.ForeignKey("categories.id", ondelete="CASCADE"))

    children = db.relationship("Category",
                               backref=db.backref("parent", remote_side="Category.id"),
                               lazy="dynamic")
    articles = db.relationship("Article",
                               backref=db.backref("category", uselist=False),
                               lazy="dynamic")

    @staticmethod
    def insert_default_values():
        category = Category(name="database", description="database related",
                            display_order=0)
        db.session.add(category)
        db.session.commit()


# Multiple-Multiple-Mapping Table: associate articles with tags
article_tag_mapping = db.Table(
    "article_tag_mapping",
    ModelBase.metadata,
    db.Column("article_id", db.String(64),
              db.ForeignKey("articles.id", ondelete="CASCADE")),
    db.Column("tag_id", db.String(64),
              db.ForeignKey("tags.id", ondelete="CASCADE")),
    db.PrimaryKeyConstraint("article_id", "tag_id"),
)


class Tag(UUIDMixin, TimestampMixin, ModelBase):
    """Article Tag Model"""
    __tablename__ = "tags"

    name = db.Column(db.String(64), nullable=False)

    articles = db.relationship("Article", secondary=article_tag_mapping,
                               backref=db.backref("tags", lazy="dynamic"),
                               lazy="dynamic")


class Source(UUIDMixin, ModelBase):
    """Article Source Model"""
    __tablename__ = "sources"

    name = db.Column(db.String(32), nullable=False)

    articles = db.relationship("Article",
                               backref=db.backref("source", uselist=False),
                               lazy="dynamic")

    @staticmethod
    def insert_default_values():
        names = ("original", "reproduction", "translation")
        for name in names:
            source = Source(name=name)
            db.session.add(source)
        db.session.commit()


class Article(UUIDMixin, TimestampMixin, ModelBase):
    """Article Model"""
    __tablename__ = "articles"

    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(255), nullable=True)
    stars = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    published = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.String(64),
                        db.ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False)
    category_id = db.Column(db.String(64),
                            db.ForeignKey("categories.id", ondelete="SET NULL"))
    source_id = db.Column(db.String(64),
                          db.ForeignKey("sources.id", ondelete="SET NULL"))

    comments = db.relationship("Comment",
                               backref=db.backref("article", lazy="subquery"),
                               lazy="dynamic")


class Comment(UUIDMixin, TimestampMixin, ModelBase):
    """Article Comment Model"""
    __tablename__ = "comments"

    article_id = db.Column(db.String(64),
                           db.ForeignKey("articles.id", ondelete="CASCADE"))
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String(64),
                        db.ForeignKey("users.id", ondelete="SET NULL"))
