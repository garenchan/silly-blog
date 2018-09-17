# -*- coding: utf-8 -*-
import os
import functools
import logging.config
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from silly_blog.configs import get_config
from silly_blog.contrib.auth import HTTPTokenAuth
from silly_blog.contrib.jwtoken import JSONWebSignature
from silly_blog.contrib.utils import make_error_response
from silly_blog.contrib.middleware import SizeLimitMiddleware


LOG = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
auth = HTTPTokenAuth('X-Auth-Token')
jws = JSONWebSignature()
cors = CORS()


def create_app():
    """Create a flask application."""
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir, 'instance'))
    app = Flask(__name__, instance_path=path, instance_relative_config=True)
    config_object = get_config(app.config['ENV'])  # respect FLASK_ENV env
    app.config.from_object(config_object)
    # NOTE: we can use instance folders to store config files and
    # here use "from_pyfile" to load them.
    # http://flask.pocoo.org/docs/1.0/config/#instance-folders
    app.config.from_pyfile('application.cfg', silent=True)
    # Create a config file and set environment variable APP_CONFIGS to it
    # to override above configs.
    app.config.from_envvar('APP_CONFIGS', silent=True)
    # init logging, inject app into logging namespace,
    # so fileConfig can respect flask config
    with app.open_instance_resource('logging.ini', mode='r') as fp:
        logging.config.fileConfig(fp, disable_existing_loggers=False)
    # globally disable strict slashes
    app.url_map.strict_slashes = False

    initialize_extensions(app)
    register_blueprints(app)
    minor_repairs(app)
    add_cli_command(app)

    # Add `sizelimit` middleware
    app.wsgi_app = SizeLimitMiddleware(app)

    return app


def initialize_extensions(app):
    """Initialize initialize_extensions with specified app."""
    # db related
    db.init_app(app)
    migrate.init_app(app, db=db)
    # auth related
    auth.init_app(app)
    jws.init_app(app)
    # enable CORS
    cors.init_app(app)

    @auth.unauthorized_handler
    def handle_unauthorized():
        """Callback for auth's unauthorized event."""
        return make_error_response(401, 'Unauthorized Access')


def register_blueprints(app):
    """Register blueprints with specified app."""
    from silly_blog.app.resources import api_bp
    from silly_blog.app.views import other_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(other_bp)


def minor_repairs(app):
    """Some extensions is very aggressive, will cause some mechanisms of
    Flask not work. So we need to fix them.
    """
    def custom_error_handler(_orig, e):
        if isinstance(e, HTTPException):
            return make_error_response(e.code, e.description)
        else:
            # TODO: further break down the error
            LOG.exception('Unknown internal server error.')
            return make_error_response(500, 'Internal Server Error')

    # FIXME: `flask-restful` will intercept exception in midway.
    app.handle_exception = functools.partial(
        custom_error_handler, app.handle_exception)
    app.handle_user_exception = functools.partial(
        custom_error_handler, app.handle_user_exception)


def add_cli_command(app):
    """add some useful cli command to app."""
    from silly_blog.app.cli import COMMANDS

    for command in COMMANDS:
        app.cli.add_command(command)

    @app.shell_context_processor
    def make_shell_context():
        # NOTE: app already exists, no need to append.
        return dict(db=db)
