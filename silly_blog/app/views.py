# -*- coding: utf-8 -*-
from flask import jsonify

from silly_blog.app import app, __version__


@app.route('/')
def index():
    print(__name__)
    return jsonify({
        'name': __name__.split('.', 1)[0],
        'version': __version__
    })
