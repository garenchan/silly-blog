# -*- coding: utf-8 -*-
"""
SQLAlchemy APIs for silly blog.
"""
import types
import datetime
import functools

from sqlalchemy import exc as sqla_exc

from silly_blog.app.db import db
from silly_blog.app.db.models import (
    ModelBase, Role, User, Category, Source, Tag, Article, RoleAssignment)
from silly_blog.app.db import exception as db_exc


def _serialize(data):
    if data is None:
        return None

    if isinstance(data, (
            int, float, str, bytes, datetime.date, datetime.time)):
        return data
    if isinstance(data, ModelBase):
        data = data.to_dict()
    if isinstance(data, dict):
        for k, v in data.items():
            data[k] = _serialize(v)
        return data
    if isinstance(data, (list, tuple)):
        return [_serialize(d) for d in data]

    raise ValueError('Unknown data type %s' % data)


def serialized(f):

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            serialize = kwargs.pop('serialize', True)
            result = f(*args, **kwargs)

            if serialize:
                result = _serialize(result)
            db.session.commit()
        except (sqla_exc.DBAPIError, db_exc.DBError):
            db.session.rollback()
            raise
        else:
            return result
        finally:
            # NOTE: no need to remove session, flask-sqlalchemy will
            # do that on app context teardown.
            pass

    return wrapper


class APIMeta(type):
    """Metaclass for API.

    Convert the function attributes into class methods and
    serialize their return values.
    """

    def __new__(cls, name, bases, attrs):
        for k, v in attrs.items():
            if isinstance(v, types.FunctionType):
                if not k.startswith('_'):
                    v = serialized(v)
                attrs[k] = classmethod(v)

        return type.__new__(cls, name, bases, attrs)


class APIBase(metaclass=APIMeta):
    """Base class for API.

    Provide some simple and general CRUD APIs.
    """

    __model__ = None

    def _get(self, _id):
        """Get record by id primary key."""
        obj = self.__model__.query.get_or_404(_id)
        return obj

    def get(self, _id):
        return self._get(_id)

    def _get_by_uuid(self, uuid):
        """Get record by uuid."""
        obj = self.__model__.query.filter_by(uuid=uuid).first_or_404()
        return obj

    def get_by_uuid(self, uuid):
        return self._get_by_uuid(uuid)

    def create(self, **kwargs):
        """Create a new record."""
        obj = self.__model__(**kwargs)
        db.session.add(obj)
        return obj

    def delete(self, _id):
        """Delete record by id primary key."""
        obj = self._get(_id)
        db.session.delete(obj)

    def delete_by_uuid(self, uuid):
        """Delete record by uuid."""
        obj = self._get_by_uuid(uuid)
        db.session.delete(obj)

    def _update(self, obj, **kwargs):
        columns = [c.name for c in self.__model__.__table__.columns]
        for k, v in kwargs.items():
            if k in columns:
                setattr(obj, k, v)
        db.session.add(obj)
        return obj

    def update(self, _id, **kwargs):
        """Update record by id primary key."""
        obj = self._get(_id)
        return self._update(obj, **kwargs)

    def update_by_uuid(self, uuid, **kwargs):
        """Update record by uuid."""
        obj = self._get_by_uuid(uuid)
        return self._update(obj, **kwargs)


class RoleAPI(APIBase):
    __model__ = Role


class UserAPI(APIBase):
    __model__ = User


class CategoryAPI(APIBase):
    __model__ = Category


class SourceAPI(APIBase):
    __model__ = Source


class TagAPI(APIBase):
    __model__ = Tag


class ArticleAPI(APIBase):
    __model__ = Article


class RoleAssignmentAPI(APIBase):
    __model__ = RoleAssignment

    def assign_by_uuid(self, user_uuid, role_uuid):
        user = UserAPI.get_by_uuid(user_uuid, serialize=False)
        role = RoleAPI.get_by_uuid(role_uuid, serialize=False)
        user.roles.append(role)

    def unassign_by_uuid(self, user_uuid, role_uuid):
        user = UserAPI.get_by_uuid(user_uuid, serialize=False)
        role = RoleAPI.get_by_uuid(role_uuid, serialize=False)
        user.roles.remove(role)
