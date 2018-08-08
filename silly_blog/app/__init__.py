#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import functools
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import flask_restful as restful
from werkzeug.exceptions import HTTPException

from silly_blog.configs import get_config
from silly_blog.contrib.auth import HTTPTokenAuth
from silly_blog.contrib.jwtoken import JSONWebSignature
from silly_blog.contrib.utils import make_error_response


LOG = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
auth = HTTPTokenAuth("X-Auth-Token")
jws = JSONWebSignature()


@auth.unauthorized_handler
def handle_unauthorized():
    return make_error_response(401, "Unauthorized Access")


def create_app(config_name):
    _app = Flask(__name__, instance_relative_config=True)
    _app.config.from_object(get_config(config_name))
    # _app.config.from_pyfile(os.getenv("CONFIG_FILE", ""), True)

    # db related
    db.init_app(_app)
    migrate.init_app(_app, db=db)
    # auth related
    auth.init_app(_app)
    jws.init_app(_app)

    # globally disable strict slashes
    _app.url_map.strict_slashes = False

    return _app


app = create_app(os.getenv("FLASK_CONFIG"))
# enable CORS
CORS(app)
# NOTE: `flask-restful` has a issue: can't defer initialization for app but bp.
api = restful.Api(app)


# FIXME: `flask-restful` is very aggressive, will intercept exception in midway.
def custom_error_handler(orig, e):
    if isinstance(e, HTTPException):
        return make_error_response(e.code, e.description)
    return orig(e)


app.handle_exception = functools.partial(
    custom_error_handler, app.handle_exception)
app.handle_user_exception = functools.partial(
    custom_error_handler, app.handle_user_exception)


# import views
from silly_blog.app import resources, views  # noqa
