# -*- coding: utf-8 -*-
"""
    silly_blog.config
    ~~~~~~~~~~~~~~~~~

    Default configurations for different environment.
"""

import os


DIR_NAME = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Basic Configurations."""

    DEBUG = False
    TESTING = False
    PROPAGATE_EXCEPTIONS = True
    TRAP_HTTP_EXCEPTIONS = False
    SECRET_KEY = '468f67c072f9490f29ea2b90594e7c0829293b9f1ecc265b'
    PREFERRED_URL_SCHEME = 'http'  # used for URL generation
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # limit size of incoming request to 10MB
    JSON_AS_ASCII = False  # serialize objects to unicode-encoded JSON
    JSON_SORT_KEYS = True

    # sqlalchemy related
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # default is None, will issue a warning


class TestingConfig(Config):
    """Configurations For Testing Environment."""

    TESTING = True

    # sqlalchemy related
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class DevelopmentConfig(Config):
    """Configurations For Dev Environment."""

    DEBUG = True

    # sqlalchemy related
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DIR_NAME, 'db-dev.sqlite')
    SQLALCHEMY_ECHO = True

    # token auth related
    FORCE_TOKEN_AUTH = False  # login_required inaction


class ProductionConfig(Config):
    """Configurations For Production Environment."""

    PREFERRED_URL_SCHEME = 'https'

    # sqlalchemy related
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DIR_NAME, 'db.sqlite')


_configs = dict(
    testing=TestingConfig,
    development=DevelopmentConfig,
    production=ProductionConfig,
    default=DevelopmentConfig,
)


def get_config(name, raise_error=False):
    """Get config object corresponding to the name."""
    config = _configs.get(name)
    if config:
        return config
    elif raise_error:
        raise RuntimeError('%r config not found, you need to choose it from'
                           '%s' % (name, list(_configs.keys())))
    else:
        return _configs['default']
