#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import uuid

from flask import request, g

from silly_blog.app import app, auth


@app.route("/post")
@auth.login_required
def post():
    print(getattr(request, "aa", "none"))
    return "%s" % auth.current_user


@app.route("/test")
def test():
    uid = uuid.uuid4().hex
    setattr(request, "aa", uid)
    time.sleep(10)
    # print(g, dir(request))
    print(request.aa)
    return ""
