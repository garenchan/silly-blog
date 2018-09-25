# -*- coding: utf-8 -*-
import datetime
import functools

from silly_blog.app.db import db
from silly_blog.app.db.models import (
    ModelBase, Role, User, Category, Source, Tag, Article
)


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
            result = f(*args, **kwargs)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        else:
            return _serialize(result)
        finally:
            db.session.remove()

    return wrapper


@serialized
def user_get(uuid):
    user = User.query.filter_by(uuid=uuid).first()
    return user
