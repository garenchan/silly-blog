# -*- coding: utf-8 -*-
"""
SQLAlchemy APIs for silly blog.
"""
import types
import datetime
import functools
import logging

from sqlalchemy import exc as sqla_exc
from sqlalchemy.orm import exc as orm_exc

from silly_blog.app.db import db
from silly_blog.app.db.models import (
    ModelBase, Role, User, Category, Source, Tag, Article, RoleAssignment)
from silly_blog.app.db import exception as db_exc

LOG = logging.getLogger(__name__)


def _serialize(data):
    """Serialize the data into a dictionary."""
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


def _serialized(func):
    """A serialize decorator for db api."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            serialize = kwargs.pop('serialize', True)
            result = func(*args, **kwargs)

            if serialize:
                result = _serialize(result)
            db.session.commit()
        except orm_exc.MultipleResultsFound:
            LOG.exception('Multiple rows were found for one().')
            return None
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


class DBAPIMeta(type):
    """Metaclass for API.

    Convert the function attributes into class methods and
    serialize their return values.
    """

    def __new__(cls, name, bases, attrs):
        for k, v in attrs.items():
            if isinstance(v, types.FunctionType):
                if not k.startswith('_'):
                    v = _serialized(v)
                attrs[k] = classmethod(v)

        return type.__new__(cls, name, bases, attrs)


class DBAPIBase(metaclass=DBAPIMeta):
    """Base class for API.

    Provide some simple and general CRUD APIs.
    """

    __model__ = None

    def _get(self, _id):
        """Get record by id primary key."""
        record = self.__model__.query.get(_id)
        return record

    def get(self, _id):
        return self._get(_id)

    def _get_by_uuid(self, uuid):
        """Get record by uuid."""
        record = self.__model__.query.filter_by(uuid=uuid).first()
        return record

    def get_by_uuid(self, uuid):
        return self._get_by_uuid(uuid)

    def create(self, **kwargs):
        """Create a new record."""
        record = self.__model__(**kwargs)
        db.session.add(record)
        return record

    def delete(self, _id):
        """Delete record by id primary key."""
        record = self._get(_id)
        db.session.delete(record)

    def delete_by_uuid(self, uuid):
        """Delete record by uuid."""
        record = self._get_by_uuid(uuid)
        db.session.delete(record)

    def _update(self, record, *args, **kwargs):
        record.update(*args, **kwargs)
        db.session.add(record)
        return record

    def update(self, _id, *args, **kwargs):
        """Update record by id primary key."""
        record = self._get(_id)
        return self._update(record, *args, **kwargs)

    def update_by_uuid(self, uuid, *args, **kwargs):
        """Update record by uuid."""
        record = self._get_by_uuid(uuid)
        return self._update(record, *args, **kwargs)


class RoleDBAPI(DBAPIBase):
    __model__ = Role


class UserDBAPI(DBAPIBase):
    __model__ = User

    def get_by_username_email(self, username_or_email):
        """Get user record by username or email."""
        user = self.__model__.query.filter(
            db.or_(
                self.__model__.username == username_or_email,
                self.__model__.email == username_or_email
            )).scalar()
        return user

    def check_password(self, pwhash, password):
        """Check that a plaintext password matches hashed."""
        if isinstance(pwhash, dict):
            pwhash = pwhash.get('password')
        return self.__model__.check_password(pwhash, password)


class CategoryDBAPI(DBAPIBase):
    __model__ = Category


class SourceDBAPI(DBAPIBase):
    __model__ = Source


class TagDBAPI(DBAPIBase):
    __model__ = Tag


class ArticleDBAPI(DBAPIBase):
    __model__ = Article


class RoleAssignmentDBAPI(DBAPIBase):
    __model__ = RoleAssignment

    def get_roles_by_user_uuid(self, user_uuid):
        """Lists all role assignments a user has."""
        records = db.session.query(Role).join(self.__model__).filter_by(
            user_uuid=user_uuid).all()
        return records

    def assign_by_uuid(self, user_uuid, role_uuid):
        user = UserDBAPI.get_by_uuid(user_uuid, serialize=False)
        role = RoleDBAPI.get_by_uuid(role_uuid, serialize=False)
        user.roles.append(role)

    def unassign_by_uuid(self, user_uuid, role_uuid):
        user = UserDBAPI.get_by_uuid(user_uuid, serialize=False)
        role = RoleDBAPI.get_by_uuid(role_uuid, serialize=False)
        user.roles.remove(role)
