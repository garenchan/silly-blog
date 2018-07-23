#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import uuid

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property

from silly_blog.app import db


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


class DictMixin(object):

    @classmethod
    def from_dict(cls, d: dict):
        """Returns a model instance from a dictionary."""
        new_d = d.copy()
        return cls(**new_d)

    def to_dict(self):
        """Returns the models'a attributes as a dictionary."""
        names = (column.name for column in self.__table__.columns)
        return {name: getattr(self, name) for name in names}


class Role(IdMixin, DictMixin, db.Model):
    """User Role model

    Use for RBAC(Role-Based Access Control)!
    """
    __tablename__ = "roles"

    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    users = db.relationship("User", backref="role", lazy="dynamic")

    @staticmethod
    def insert_default_values():
        roles = {
            "Administrator": "system administrators",
            "CommonUser": "common users",
        }
        for name, desc in roles.items():
            role = Role(name=name, description=desc)
            db.session.add(role)
        db.session.commit()


class FederatedUser(IdMixin, DictMixin, db.Model):
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


class LocalUser(IdMixin, DictMixin, db.Model):
    """Local User Model"""
    __tablename__ = "local_users"

    user_id = db.Column(db.String(64),
                        db.ForeignKey("users.id", ondelete="CASCADE"),
                        unique=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    display_name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(128), nullable=False)


class User(UUIDMixin, DictMixin, db.Model):
    """User Model"""
    __tablename__ = "users"

    role_id = db.Column(db.Integer,
                        db.ForeignKey("roles.id", ondelete="CASCADE"))
    enabled = db.Column(db.Boolean)
    local_user = db.relationship("LocalUser", uselist=False, lazy="subquery",
                                 backref="user", cascade="all,delete-orphan")
    federated_users = db.relationship("FederatedUser", single_parent=True,
                                      lazy="dynamic", backref="user",
                                      cascade="all,delete-orphan")

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

    @staticmethod
    def insert_default_values():
        users = [
            {
                "name": "admin",
                "role": "Administrator",
                "password": "admin123",
            },
            {
                "name": "common",
                "role": "CommonUser",
                "password": "common123",
            }
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
