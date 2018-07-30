#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib.request
import pprint


def client(url, data=None, headers=None):
    if headers is None:
        headers = {}
    if data:
        data = json.dumps(data).encode("utf-8")
        if "content-type" not in headers:
            headers["content-type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        res = urllib.request.urlopen(req)
    except urllib.request.HTTPError as ex:
        print("error:", ex.code)
        data = ex.read().decode("utf-8")
        pprint.pprint(json.loads(data))
        return None
    else:
        data = res.read().decode("utf-8")
        data = json.loads(data)
        pprint.pprint(data)
        return data


def get_token():
    url = "http://127.0.0.1:5000/tokens"
    data = {
        "auth": {
            "username": "admin",
            "password": "admin123",
        }
    }

    res = client(url, data)
    return res["token"]["id"] if res else None


def validate_token():
    token = get_token()
    url = "http://127.0.0.1:5000/tokens"
    headers = {
        "X-Auth-Token": token
    }
    client(url, headers=headers)


def create_category():
    url = "http://127.0.0.1:5000/categories"
    data = {
        "category": {
            "name": "12332",
            "parent_id": "123"
        }
    }
    client(url, data)


def list_category():
    url = "http://127.0.0.1:5000/categories"
    client(url)


def create_tag():
    url = "http://127.0.0.1:5000/tags"
    data = {
        "tag": {
            "name": "123",
        },
    }
    client(url, data)


def list_tags():
    url = "http://127.0.0.1:5000/tags"
    client(url)


def list_sources():
    url = "http://127.0.0.1:5000/sources/c20b5d8e028046288d1b189dabdfa2c4"
    client(url)


def list_users():
    url = "http://127.0.0.1:5000/users"
    client(url)


def create_user():
    data = {
        "user": {
            "name": "zhangsan",
            "password": "zhangsan"

        }
    }
    url = "http://127.0.0.1:5000/users/"
    client(url, data)


def list_articles():
    url = "http://127.0.0.1:5000/articles/"
    client(url)


if __name__ == '__main__':
    validate_token()
