# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify

from silly_blog.app import __version__


other_bp = Blueprint('other', __name__)


@other_bp.route('/')
def index():
    return jsonify({
        'name': __name__.split('.', 1)[0],
        'version': __version__
    })
