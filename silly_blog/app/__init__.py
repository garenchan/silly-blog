# -*- coding: utf-8 -*-
__version__ = 'v1.0.0'

import os
import functools
import logging.config
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
from silly_blog.contrib.middleware import SizeLimit


LOG = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
auth = HTTPTokenAuth('X-Auth-Token')
jws = JSONWebSignature()


@auth.unauthorized_handler
def handle_unauthorized():
    """Callback for auth's unauthorized event."""
    return make_error_response(401, 'Unauthorized Access')


def create_app():
    """Create a flask application."""
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir, 'instance'))
    _app = Flask(__name__, instance_path=path, instance_relative_config=True)
    config_object = get_config(_app.config['ENV'])  # respect FLASK_ENV env
    _app.config.from_object(config_object)
    # NOTE: we can use instance folders to store config files and
    # here use "from_pyfile" to load them.
    # http://flask.pocoo.org/docs/1.0/config/#instance-folders
    _app.config.from_pyfile('application.cfg', silent=True)
    # Create a config file and set environment variable APP_CONFIGS to it
    # to override above configs.
    _app.config.from_envvar('APP_CONFIGS', silent=True)
    # init logging, inject app into logging namespace,
    # so fileConfig can respect flask config
    with _app.open_instance_resource('logging.ini', mode='r') as fp:
        logging.config.fileConfig(fp)
    # db related
    db.init_app(_app)
    migrate.init_app(_app, db=db)
    # auth related
    auth.init_app(_app)
    jws.init_app(_app)
    # globally disable strict slashes
    _app.url_map.strict_slashes = False

    return _app


app = create_app()
# enable CORS
CORS(app)
# NOTE: `flask-restful` has a issue: can't defer initialization for app but bp.
api = restful.Api(app)
app.wsgi_app = SizeLimit(app.wsgi_app)


# FIXME: `flask-restful` is very aggressive, will intercept exception in midway.
def custom_error_handler(_orig, e):
    if isinstance(e, HTTPException):
        return make_error_response(e.code, e.description)
    else:
        # TODO: further break down the error
        return make_error_response(500, 'Internal Server Error')


app.handle_exception = functools.partial(
    custom_error_handler, app.handle_exception)
app.handle_user_exception = functools.partial(
    custom_error_handler, app.handle_user_exception)


# import views
from silly_blog.app import resources, views  # noqa
