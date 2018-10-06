# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restful import Api


api_bp = Blueprint('api1', __name__, url_prefix='/api')
api = Api(api_bp)


from . import (token)  # noqa
