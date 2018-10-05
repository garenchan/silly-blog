# -*- coding: utf-8 -*-
import types

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
_original_init = db.init_app
db.init_app = types.MethodType(
    lambda self, app: _init_app(self, app), db)


def _init_app(self, app):
    """Patch flask-sqlalchemy's init_app method.

    1. Models are loaded when `init_app` is executed.
    2. Register exception filters for current engine.
    """
    from silly_blog.app.db import models, _exc_filters
    retval = _original_init(app)
    with app.app_context():
        _exc_filters.register_engine(self.engine)
    return retval
