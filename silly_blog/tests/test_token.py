# -*- coding: utf-8 -*-
import json

import pytest


class TestToken(object):

    @pytest.mark.parametrize(('username_or_email', 'password'), (
            ('nonexsit_username', 'test123'),
            ('nonexsit_email@qq.com', 'test123'),
            ('admin', 'error_password')
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
        assert response.status_code == 401
        assert any(error in response.data for error in
                   (b'Invalid username or email', b'Invalid password'))

    def test_post_success(self, client):
        data = {
            'auth': {
                'username': 'admin',
                'password': 'admin123'
            }
        }
        response = client.post('/tokens', data=json.dumps(data),
                               content_type='application/json')
        assert response.status_code == 200
        token = json.loads(response.data.decode())
        assert 'token' in token
        assert token['token']['id']
