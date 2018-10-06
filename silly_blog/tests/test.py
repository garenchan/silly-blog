#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from silly_blog.app.db import db
from silly_blog.app.db import models
from flask_sqlalchemy import SQLAlchemy
from silly_blog.app.resources1 import api_bp
from silly_blog.app import jws

app = Flask(__name__)
app.config.update(
    SECRET_KEY = b'468f67c072f9490f29ea2b90594e7c0829293b9f1ecc265b',
    SQLALCHEMY_ECHO=True,
    SQLALCHEMY_COMMIT_ON_TEARDOWN=False,
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:admin123@172.18.231.172/test'
)
db.init_app(app)
jws.init_app(app)
app.register_blueprint(api_bp)


@app.shell_context_processor
def make_shell_context():
    # NOTE: app already exists, no need to append.
    return dict(db=db, models=models)


@app.route('/')
def index():
    return jsonify(['1', '2'])


if __name__ == '__main__':
    #with app.app_context():
    #    db.create_all()
    app.run(debug=True)
