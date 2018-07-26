#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib.request

from flask import request

from silly_blog.app import app


"""x
with app.test_request_context("/", json={}):
    print(request.is_json)
    request.a = {1:2}
    print(request.a)
"""


def get_token():
    data = {
        "auth": {
            "username": "admin",
            "password": "admin123",
        }
    }
    data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:5000/tokens", data=data,
                                 headers={'content-type': 'application/json'})
    try:
        res = urllib.request.urlopen(req)
    except Exception as ex:
        data = ex.read().decode()
        import pprint
        pprint.pprint(json.loads(data))
    else:
        data = res.read().decode("utf-8")
        token= json.loads(data)["token"]["id"]
        print(token)
        return token


def create_category():
    data = {
        "category": {
            "name": "12322224522"
        }
    }
    data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:5000/categories", data=data,
                                 headers={'content-type': 'application/json',
                                          #"X-Auth-Token": get_token()
                                          })
    try:
        res = urllib.request.urlopen(req)
    except Exception as ex:
        print(ex.code)
        data = ex.read().decode()
        import pprint
        pprint.pprint(json.loads(data))
    else:
        data = res.read().decode()
        import pprint
        pprint.pprint(json.loads(data))


def list_category():
    req = urllib.request.Request("http://127.0.0.1:5000/categories")
    try:
        res = urllib.request.urlopen(req)
    except Exception as ex:
        data = ex.read().decode()
        import pprint
        pprint.pprint(json.loads(data))
    else:
        data = res.read().decode()
        import pprint
        pprint.pprint(json.loads(data))

def create_tag():
    data = {
        "tag": {
            "name": "123"
        },
    }
    data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:5000/tags", data=data,
                                 headers={'content-type': 'application/json',
                                          # "X-Auth-Token": get_token()
                                          })
    try:
        res = urllib.request.urlopen(req)
    except Exception as ex:
        print(ex.code)
        data = ex.read().decode()
        import pprint
        pprint.pprint(json.loads(data))
    else:
        data = res.read().decode()
        import pprint
        pprint.pprint(json.loads(data))

def list_tags():
    req = urllib.request.Request("http://127.0.0.1:5000/tags")
    try:
        res = urllib.request.urlopen(req)
    except Exception as ex:
        data = ex.read().decode()
        import pprint
        pprint.pprint(json.loads(data))
    else:
        data = res.read().decode()
        import pprint
        pprint.pprint(json.loads(data))


if __name__ == '__main__':
    create_tag()
