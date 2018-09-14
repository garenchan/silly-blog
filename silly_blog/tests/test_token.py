# -*- coding: utf-8 -*-
import json
import uuid

import pytest
from flask import url_for

from silly_blog.app import db
from silly_blog.app.models import Role, User


class TestToken(object):

    @pytest.mark.parametrize(('username_or_email', 'password'), (
            ('nonexsit_username', 'test123'),
            ('nonexsit_email', 'test123'),
            ('', 'error_password')
    ))
    def test_post_failed(self, client, username_or_email, password):
        data = {
            'auth': {
                'username': username_or_email,
                'password': password
            }
        }
        response = client.post('/tokens', data=json.dumps(data),
                               content_type='application/json')
        print(response)
