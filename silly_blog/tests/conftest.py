# -*- coding: utf-8 -*-
import os

import pytest

from silly_blog.app import create_app, db


os.environ['FLASK_ENV'] = 'testing'


@pytest.fixture
def app():
    _app = create_app()
    db.create_all()
    yield _app
    db.session.remove()
    db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
