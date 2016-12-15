import unittest

from datetime import date
from mock import Mock, patch, MagicMock
from flask import current_app
from app import create_app, create_app, db
from app.models import Company, Indicators, User
import datetime
import os
import json
from base64 import b64encode

email=os.environ.get('CLI_USER') or 'testuser'
password=os.environ.get('CLI_PASSWORD') or 'password'


class TestCompany(unittest.TestCase):
    def setUp(self):
        self.buffer = True
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        db.session.add(User(email=email, password=password, active=True, confirmed_at=datetime.datetime.utcnow()))
        db.session.commit()

        # Login is needed to initialize pw
        self.client = self.app.test_client()
        self.login(email, password)

        Company.generate_fake(10)
        Indicators.generate_fake(3)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/login', data=dict(
                email=email,
                password=password
            ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_get_companies(self):

        headers = {
            'Authorization': 'Basic ' + b64encode("{0}:{1}".format(email, password))
        }

        # rv = self.login('testuser', 'password')
        r = self.client.get('/api/1.0/company/', headers=headers, follow_redirects=True)
        data = json.loads(r.data)
        self.assertGreaterEqual(data['total'], 1, "At least one company should be returned")
        self.assertIn("companies", data, "Ensure key exists")
        self.assertIn("next", data, "Ensure key exists")
        self.assertIn("pages", data, "Ensure key exists")
        self.assertIn("per_page", data, "Ensure key exists")
        self.assertIn("prev", data, "Ensure key exists")
        self.assertIn("total", data, "Ensure key exists")


