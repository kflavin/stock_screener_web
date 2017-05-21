import unittest

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

email=os.environ.get('CLI_USER') or 'testuser'
password=os.environ.get('CLI_PASSWORD') or 'password'


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