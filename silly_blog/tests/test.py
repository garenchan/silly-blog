#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from silly_blog.app.db import db
from silly_blog.app.db import models

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_ECHO=True,
    SQLALCHEMY_COMMIT_ON_TEARDOWN=False,
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:admin123@172.18.231.172/test'
)
db.init_app(app)


@app.route('/')
def index():
    return jsonify(['1', '2'])


if __name__ == '__main__':
    #with app.app_context():
    #    db.create_all()
    app.run(debug=True)
