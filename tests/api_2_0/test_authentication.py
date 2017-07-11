import time
from mock import Mock, patch, MagicMock
from flask import current_app, request, url_for
import json
from app.api_2_0.authentication import login_required
from base import BaseTest


class TestAuthenticationAPI(BaseTest):

    def test_auth_register(self):
        """
        Test registration to api
        Returns:

        """
        # pass
        with self.client:
            response = self.register_user(self.email, self.password)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')

    def test_auth_valid_login(self):
        # Register user
        response = self.register_user(self.email, self.password)
        # Login
        data = json.loads(self.login_user(self.email, self.password).get_data())
        self.assertTrue(data.get('token'))
        self.assertEqual(data.get('status'), 'success')

    def test_auth_invalid_login(self):
        response = self.register_user(self.email, self.password)
        # Bad password
        data = json.loads(self.login_user(self.email, "badpassword").get_data())
        self.assertFalse(data.get('token'))
        self.assertEqual(data.get('status'), 'fail')

    def test_auth_user_status(self):
        self.register_user(self.email, self.password)
        data = json.loads(self.login_user(self.email, self.password).get_data())
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

            # No token
            response = self.client.get(
                '/api/2.0/auth/status',
                content_type="application/json"
            )
            bad_data = json.loads(response.get_data())
            self.assertEqual(response.status_code, 401)

            # Null token
            response = self.client.get(
                '/api/2.0/auth/status',
                headers=dict(
                    Authorization='Bearer ' + ''
                ),
                content_type="application/json"
            )
            bad_data = json.loads(response.get_data())
            self.assertEqual(response.status_code, 401)

            # Malformed token
            response = self.client.get(
                '/api/2.0/auth/status',
                headers=dict(
                    Authorization='asdfasdasdf'
                ),
                content_type="application/json"
            )
            bad_data = json.loads(response.get_data())
            self.assertEqual(response.status_code, 401)
            self.assertEqual(bad_data['message'], 'no auth token provided')
            self.assertEqual(bad_data['status'], 'fail')

            # Expired password should not be able to grab user status page
            self.change_password(self.email, self.password, "NewShinyPassword")
            time.sleep(1)
            response = self.client.get(
                url_for('api_2_0.user_api'),
                headers=dict(
                    Authorization='Bearer ' + data.get('token')
                ),
                content_type="application/json"
            )
            bad_data = json.loads(response.get_data())
            self.assertEqual(bad_data.get('status'), 'fail')
            self.assertEqual(bad_data.get('message'), 'Signature expired.  Please log in again.')

            # check expired signature
            time.sleep(1)
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

            # Don't use the same token down here, it is EXPIRED!

    def test_auth_change_password(self):
        self.register_user(self.email, self.password)
        self.change_password(self.email, self.password, "ShinyNewPassword")
        time.sleep(2)

        # Old login should fail
        data = json.loads(self.login_user(self.email, self.password).get_data())
        self.assertEqual(data.get('status'), 'fail')
        self.assertEqual(data.get('message'), 'User does not exist, or password is invalid')

        # New login should succeed
        data = json.loads(self.login_user(self.email, "ShinyNewPassword").get_data())
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data.get('message'), 'Logged in')

    def test_auth_login_required(self):
        # Mock a function to return a value of "success", then wrap it with the login decorator
        func = Mock(name="test_auth_login_required_mock", return_value="success")
        func.__name__ = "test_auth_login_required_mock"
        decorated_func = login_required(func)
        token = self.get_token()

        # Valid request
        with current_app.test_request_context(headers={'Authorization': 'Bearer ' + token}):
            value = decorated_func()
            self.assertEqual(value, 'success')

        # No token just space provided
        with current_app.test_request_context(headers={'Authorization': 'Bearer '}):
            response = decorated_func()
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('error'), 'unauthorized user')
            self.assertEqual(data.get('message'), 'Not logged in')

        # No token no space provided
        with current_app.test_request_context(headers={'Authorization': 'Bearer'}):
            response = decorated_func()
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('error'), 'unauthorized user')
            self.assertEqual(data.get('message'), 'Not logged in')

        # Null authorization value
        with current_app.test_request_context(headers={'Authorization': ''}):
            response = decorated_func()
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('error'), 'unauthorized user')
            self.assertEqual(data.get('message'), 'Not logged in')

        # No header provided
        with current_app.test_request_context():
            response = decorated_func()
            data = json.loads(response.data.decode())
            self.assertEqual(data.get('error'), 'unauthorized user')
            self.assertEqual(data.get('message'), 'Not logged in')
