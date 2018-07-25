#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_restful as restful

from silly_blog.configs import get_config
from silly_blog.contrib.auth import HTTPTokenAuth
from silly_blog.contrib.token import JSONWebSignature


db = SQLAlchemy()
migrate = Migrate()
auth = HTTPTokenAuth("X-Auth-Token")
jws = JSONWebSignature()


def create_app(config_name):
    _app = Flask(__name__, instance_relative_config=True)
    _app.config.from_object(get_config(config_name))

    # db related
    db.init_app(_app)
    migrate.init_app(_app, db=db)
    # auth related
    auth.init_app(_app)
    jws.init_app(_app)

    return _app


app = create_app(os.getenv("FLASK_CONFIG"))
# NOTE: `flask-restful` has a issue: can't defer initialization for app but bp.
api = restful.Api(app)

# import views
from . import resources
