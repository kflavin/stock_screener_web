import os
import json
from flask_testing import TestCase
from flask import url_for

from app import create_app, db
from app.models import User


class BaseTest(TestCase):
    """
    Base class to implement common functionality like register, login, app and database creation.
    """
    email = os.environ.get('CLI_USER') or 'testuser'
    password = os.environ.get('CLI_PASSWORD') or 'password'

    # def create_app(self):
    #     """
    #     Make the IDE error go away...
    #     """
    #     raise NotImplementedError

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

    def register_unconfirmed_user(self, email, password):
        return self.client.post(
            '/api/2.0/auth/register',
            data=json.dumps(dict(
                email=email,
                password=password
            )),
            content_type="application/json"
        )

    def register_user(self, email, password):
        res = self.client.post(
            '/api/2.0/auth/register',
            data=json.dumps(dict(
                email=email,
                password=password
            )),
            content_type="application/json"
        )

        # Confirm the registration
        u = User.query.filter_by(email=email).first()
        u.registration_code = 1
        u.active = True
        db.session.add(u)
        db.session.commit()

        return res

    def login_user(self, email, password):
        return self.client.post(
            url_for('api_2_0.login_api'),
            data=json.dumps(dict(
                email=email,
                password=password
            )),
            content_type="application/json"
        )

    def change_password(self, email, old_password, new_password):
        return self.client.post(
            url_for('api_2_0.password_api'),
            data=json.dumps(dict(
                email=email,
                old_password=old_password,
                new_password=new_password
            )),
            content_type="application/json"
        )

    def get_token(self):
        """
        Return a JWT token for authentication
        :return: token string
        """
        payload = self.register_user(self.email, self.password)
        data = json.loads(payload.data.decode())
        payload = self.login_user(self.email, self.password)
        data = json.loads(payload.data.decode())
        return data.get('token')