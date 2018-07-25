#!/usr/bin/env python
# -*- coding: utf-8 -*-
from silly_blog.app import app, auth


@app.route("/post")
@auth.login_required
def post():
    return "%s" % auth.current_user
