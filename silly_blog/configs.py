#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


DIR_NAME = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Basic Configurations"""
    SECRET_KEY = "468f67c072f9490f29ea2b90594e7c0829293b9f1ecc265b"

    # sqlalchemy related
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(DIR_NAME, "db.sqlite")
    SQLALCHEMY_ECHO = False
    # default is None, will issue a warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    pass


class DevelopmentConfig(Config):
    """Configurations For Dev Environment"""
    SQLALCHEMY_ECHO = True

    # token auth related
    FORCE_TOKEN_AUTH = False # login_required inaction


class ProductionConfig(Config):
    pass


_configs = dict(
    test=TestingConfig,
    dev=DevelopmentConfig,
    prod=ProductionConfig,
    default=DevelopmentConfig,
)


def get_config(name, raise_error=False):
    config = _configs.get(name)
    if config:
        return config
    elif raise_error:
        raise RuntimeError("%r config not found, you need to choose it from"
                           "%s" % (name, list(_configs.keys())))
    else:
        return _configs["default"]
