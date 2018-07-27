#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
import flask_restful as restful


app = Flask(__name__)
api = restful.Api(app)


@api.resource("/")
class HelloWorld(restful.Resource):

    def get(self):
        return {'hello': 'world'}


# api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(port=10000, debug=True)
