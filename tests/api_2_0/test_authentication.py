import unittest
import time
from datetime import date
from mock import Mock, patch, MagicMock
from flask import current_app
from flask_testing import TestCase
from app import create_app, create_app, db
from app.models import Company, Indicators, User
import datetime
import os
import json
from base64 import b64encode

email = os.environ.get('CLI_USER') or 'testuser'
password = os.environ.get('CLI_PASSWORD') or 'password'


def register_user(self, email, password):
    return self.client.post(
        '/api/2.0/auth/register',
        data = json.dumps(dict(
            email=email,
            password=password
        )),
        content_type="application/json"
    )


def login_user(self, email, password):
    return self.client.post(
        '/api/2.0/auth/login',
        data=json.dumps(dict(
            email=email,
            password=password
        )),
        content_type="application/json"
    )


class TestAuthenticationAPI(TestCase):
    def create_app(self):
        self.app = create_app('testing')
        return self.app

    def setUp(self):
        self.buffer = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_auth_register(self):
        """
        Test registration to api
        Returns:

        """
        # pass
        with self.client:
            response = register_user(self, email, password)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')

    def test_auth_valid_login(self):
        # Register user
        response = register_user(self, email, password)
        # Login
        data = json.loads(login_user(self, email, password).get_data())
        self.assertTrue(data.get('token'))
        self.assertEqual(data.get('status'), 'success')

    def test_auth_invalid_login(self):
        response = register_user(self, email, password)
        # Bad password
        data = json.loads(login_user(self, email, "badpassword").get_data())
        self.assertFalse(data.get('token'))
        self.assertEqual(data.get('status'), 'fail')

    def test_auth_user_status(self):
        register_user(self, email, password)
        data = json.loads(login_user(self, email, password).get_data())
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data.get('message'), 'Logged in')

        with self.client:
            response = self.client.get(
                '/api/2.0/auth/status',
                headers=dict(
                    Authorization='Bearer ' + data.get('token')
                ),
                content_type="application/json"
            )
            good_data = json.loads(response.get_data())
            self.assertEqual(good_data.get('status'), 'success')
            self.assertEqual(good_data.get('data').get('id'), 1)

            # check expired signature
            time.sleep(2)
            response = self.client.get(
                '/api/2.0/auth/status',
                headers=dict(
                    Authorization='Bearer ' + data.get('token')
                ),
                content_type="application/json"
            )
            bad_data = json.loads(response.get_data())
            self.assertEqual(bad_data.get('status'), 'fail')
            self.assertEqual(bad_data.get('message'), 'Signature expired.  Please log in again.')


