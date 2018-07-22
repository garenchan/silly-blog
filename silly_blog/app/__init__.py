#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from flask import Flask

from silly_blog.configs import get_config


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(get_config(config_name))

    return app


app = create_app(os.getenv("FLASK_CONFIG"))
