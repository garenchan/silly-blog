#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


DIR_NAME = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Basic Configurations"""
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(DIR_NAME, "db.sqlite")


class TestingConfig(Config):
    pass


class DevelopmentConfig(Config):
    pass


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
