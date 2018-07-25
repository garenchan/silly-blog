#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request
import flask_restful as restful
from flask_restful import fields, marshal_with, reqparse

from silly_blog.app import api


fields = {
    "id": fields.String,
}


@api.resource("/tokens")
class Token(restful.Resource):

    @marshal_with(fields, envelope="token")
    def post(self):
        auth = request.json["auth"]
        method = auth["methods"]
        assert method == "password"
        method_info = auth[method]
        username = method_info["username"]
        password = method_info["password"]
        return {
            "username": username,
            "password": password,
        }
