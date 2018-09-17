# -*- coding: utf-8 -*-
import os

import pytest

from silly_blog.app import create_app, db, models


os.environ['FLASK_ENV'] = 'testing'


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        db.create_all()
        models.Role.insert_default_values()
        models.User.insert_default_values()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
