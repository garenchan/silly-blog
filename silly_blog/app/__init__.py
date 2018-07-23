#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from silly_blog.configs import get_config


db = SQLAlchemy()


def create_app(config_name):
    _app = Flask(__name__, instance_relative_config=True)
    _app.config.from_object(get_config(config_name))

    db.init_app(_app)

    return _app


app = create_app(os.getenv("FLASK_CONFIG"))
