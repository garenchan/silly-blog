#!/usr/bin/env python
# -*- coding: utf-8 -*-
import uuid
import datetime
import logging

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property

from silly_blog.app import db, auth, jws
from silly_blog.contrib.utils import isotime


LOG = logging.getLogger(__name__)


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
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow,
                           onupdate=datetime.datetime.utcnow)


class ModelBase(db.Model):
    """Extended base model class"""
    __abstract__ = True

    excludes = []

    @classmethod
    def from_dict(cls, d: dict):
        """Returns a model instance from a dictionary."""
        new_d = d.copy()
        return cls(**new_d)

    @staticmethod
    def _converter(obj):
        """Convert non-json-able object"""
        mapper = {
            datetime.datetime: (lambda x: isotime(x)),
        }
        converter = mapper.get(type(obj))
        return converter(obj) if converter else obj

    def to_dict(self, **kwargs):
        """Returns the models'a attributes as a dictionary.

        The column in the `exclude` list will not be include, you can change
        this by set column name to True in `kwargs`.
        """
        names = (column.name for column in self.__table__.columns
                 if kwargs.get(column.name, False) or
                 column.name not in self.excludes)

        return {name: self._converter(getattr(self, name)) for name in names}

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __str__(self):
        """Convert model instance to string.

        ModelBase subclasses can override this to custom str().
        """
        for attr in ["name", "title", "id"]:
            identifier = getattr(self, attr, None)
            if identifier is not None:
                break
        return "<{0} {1!r}>".format(self.__class__.__name__, identifier)
    __repr__ = __str__


class Role(UUIDMixin, ModelBase):
    """User Role model

    Use for RBAC(Role-Based Access Control)!
    """
    __tablename__ = "roles"

    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    users = db.relationship("User", backref="role", lazy="dynamic")

    # role constants
    ADMIN = "admin"
    USER = "user"

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


class FederatedUser(IdMixin, TimestampMixin, ModelBase):
    """Federated User Model

    Use for third party auth!
    """
    __tablename__ = "federated_users"
    excludes = ["id", "user_id"]

    user_id = db.Column(db.String(64),
                        db.ForeignKey("users.id", ondelete="CASCADE"))
    idp_name = db.Column(db.String(64), nullable=False)
    protocol = db.Column(db.String(64), nullable=False)
    unique_id = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255), nullable=True)


class LocalUser(IdMixin, TimestampMixin, ModelBase):
    """Local User Model"""
    __tablename__ = "local_users"
    excludes = ["id", "user_id", "password"]

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
    excludes = ["role_id"]

    role_id = db.Column(db.Integer,
                        db.ForeignKey("roles.id", ondelete="CASCADE"))
    enabled = db.Column(db.Boolean, default=True)
    local_user = db.relationship("LocalUser",
                                 uselist=False,
                                 lazy="subquery",
                                 cascade="all,delete-orphan",
                                 backref="user",)
    federated_users = db.relationship("FederatedUser",
                                      single_parent=True,
                                      lazy="subquery",
                                      cascade="all,delete-orphan",
                                      backref="user",)
    articles = db.relationship("Article",
                               lazy="dynamic",
                               backref="user")

    def __init__(self, **kwargs):
        for arg in ["name", "display_name", "email", "password"]:
            val = kwargs.get(arg)
            if val is not None:
                setattr(self, arg, val)

        role_id = kwargs.get("role_id")
        role = Role.query.get(role_id) if role_id else None
        if not role:
            role = Role.query.filter_by(name=Role.USER).first()
        self.role = role

        self.enabled = kwargs.get("enabled", True)

    @hybrid_property
    def name(self):
        if self.local_user:
            return self.local_user.name
        elif self.federated_users:
            return self.federated_users[0].unique_id
        else:
            return None

    @name.setter
    def name(self, value):
        self.local_user = self.local_user or LocalUser()
        # TODO: local user name can only set once
        self.local_user.name = value

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
        self.local_user = self.local_user or LocalUser()
        self.local_user.display_name = value

    @hybrid_property
    def email(self):
        return self.local_user.email if self.local_user else None

    @email.setter
    def email(self, value):
        # TODO: email validate
        self.local_user = self.local_user or LocalUser()
        self.local_user.email = value

    @hybrid_property
    def password(self):
        return self.local_user.password if self.local_user else None

    @password.setter
    def password(self, value):
        self.local_user = self.local_user or LocalUser()
        self.local_user.password = generate_password_hash(value)

    def check_password(self, password):
        """Check that a plaintext password matches hashed."""
        if self.password is None or password is None:
            return False
        return check_password_hash(self.password, password)

    @staticmethod
    def get(user_id=None, name_email=None):
        """Get user by id or name/email"""
        assert any((user_id, name_email))
        if user_id:
            return User.query.get(user_id)
        elif name_email:
            local_user = LocalUser.query.join(LocalUser.user).filter(db.or_(
                LocalUser.name == name_email, LocalUser.email == name_email
            )).first()
            return local_user.user if local_user else None
        else:
            return None

    def generate_auth_token(self):
        """Generate a `JWS` token for user"""
        data = dict(id=self.id)
        return jws.encode(data)

    @staticmethod
    def verify_auth_token(token):
        """Verify auth token and returns a user object."""
        try:
            data = jws.decode(token)
        except Exception:
            LOG.exception("Verify auth token {!r} failed".format(token))
            return None
        else:
            if data is None or data.get("id") is None:
                return None
            else:
                return User.query.get(data["id"])

    @staticmethod
    def insert_default_values():
        users = [
            {"name": "admin",
             "password": "admin123",
             "email": "admin@qq.com",
             "role": Role.ADMIN},
            {"name": "common",
             "password": "common123",
             "email": "common@qq.com",
             "role": Role.USER},
        ]
        for info in users:
            local_user = LocalUser.query.filter_by(name=info["name"]).first()
            if local_user:
                continue
            user = User(enabled=True)
            user.role = Role.query.filter_by(name=info.pop("role")).first()
            user.name = info["name"]
            user.password = info["password"]
            user.email = info["email"]
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
                               backref="category",
                               lazy="dynamic")

    @staticmethod
    def insert_default_values():
        category = Category(name="database",
                            description="database related",
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

    name = db.Column(db.String(64), unique=True, nullable=False)

    articles = db.relationship("Article", secondary=article_tag_mapping,
                               backref="tags",
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
    excludes = ["category_id", "source_id"]

    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(255), nullable=True)
    stars = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.TIMESTAMP, nullable=True)
    user_id = db.Column(db.String(64),
                        db.ForeignKey("users.id", ondelete="SET NULL"))
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
