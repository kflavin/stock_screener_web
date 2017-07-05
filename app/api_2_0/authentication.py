import datetime
from calendar import timegm

from flask.views import MethodView
from functools import wraps

from flask import g, request, make_response, jsonify, current_app, redirect, url_for
from ..models import User, BlacklistToken
from .. import db
from .errors import unauthorized, InvalidUsage, bad_request
from . import api


def login_required(f):
    """
    Decorator for protected pages
    :param f: 
    :return: decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if auth:
            try:
                auth_token = auth.split(" ")[1]
            except IndexError as e:
                current_app.logger.debug(e)
                auth_token = ''
        else:
            auth_token = ''

        # Ensure token exists and is not blacklisted
        if auth_token and not BlacklistToken.query.filter_by(token=auth_token).first():
            response = User.decode_auth_token(auth_token)
            if isinstance(response, int):
                return f(*args, **kwargs)

        return unauthorized("Not logged in")

    return decorated_function


class RegisterAPI(MethodView):
    """
    Register a user
    """
    def post(self):
        post_data = request.get_json()
        if not post_data.get("email") or not post_data.get("password"):
            return bad_request("email and password should be defined")

        user = User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = User(
                    email = post_data.get('email'),
                    password = post_data.get('password')
                )

                # make sure last_password_change is set
                user.set_password(post_data.get('password'))

                db.session.add(user)
                db.session.commit()
                # auth_token = user.encode_auth_token(user.id, current_app.config.get('TOKEN_EXPIRATION_IN_SECONDS'))
                response_object = {
                    'status': 'success',
                    'message': 'Registered user',
                    # 'auth_token': auth_token.decode()
                }
                return make_response(jsonify(response_object)), 201

            except Exception as e:
                response_object = {
                    'status': 'fail',
                    'message': 'Unknown error, failed to register user',
                    'error': e.message
                }
                return make_response(jsonify(response_object)), 401
        else:
            response_object = {
                'status': 'fail',
                'message': 'User already exists.'
            }
            return make_response(jsonify(response_object)), 400


class LoginAPI(MethodView):
    """
    Login Resource
    """
    def post(self):
        post_data = request.get_json()
        try:
            user = User.query.filter_by(email=post_data.get('email')).first()
            if not user:
                return make_response(jsonify(dict(
                    status='fail',
                    message='User does not exist, or password is invalid'
                )), 400)

            if user.verify_password(post_data.get('password')):
                return make_response(jsonify(dict(
                    status='success',
                    message='Logged in',
                    token=user.encode_auth_token(user.id,
                                                 current_app.config.get('TOKEN_EXPIRATION_IN_SECONDS')).decode()
                )), 200)
            else:
                return make_response(jsonify(dict(
                    status='fail',
                    message='User does not exist, or password is invalid'
                )), 400)
        except Exception as e:
            current_app.logger.debug(e.message)
            return make_response((jsonify(dict(
                status='fail',
                message='Unknown error, please try again'
            )), 500))


class UserAPI(MethodView):
    """
    User resource
    """
    def get(self):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError as e:
                # current_app.logger.debug(e)
                # current_app.logger.debug(auth_header)
                auth_token = ''
        else:
            auth_token = ''

        if auth_token:
            response = User.decode_auth_token(auth_token)
            if not isinstance(response, str):
                user = User.query.filter_by(id=response).first()
                return make_response(jsonify(dict(
                    status='success',
                    data={
                        'id': user.id,
                        'email': user.email
                    }
                ))), 200

            return make_response(jsonify(dict(
                status='fail',
                message=response
            ))), 401
        else:
            return make_response(jsonify(dict(
                status='fail',
                message='no auth token provided'
            ))), 401


class LogoutAPI(MethodView):
    """
    Logout Resource
    """
    def post(self):
        """
        
        :return: 
        """
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''

        if auth_token:
            response = User.decode_auth_token(auth_token)
            if isinstance(response, int):
                try:
                    db.session.add(BlacklistToken(auth_token))
                    db.session.commit()
                    return make_response(jsonify(dict(
                        status='success',
                        message='Logged out'
                    ))), 200
                except Exception as e:
                    return make_response(jsonify(dict(
                        status='fail',
                        message=e
                    ))), 500
            else:
                return make_response(jsonify(dict(
                    status='fail',
                    message='unknown error'
                ))), 401
        else:
            return make_response(jsonify(dict(
                status='fail',
                message='no auth token given'
            ))), 403


class ChangePasswordAPI(MethodView):
    """
    Change password
    {
        "email": <email>
        "old_password": <old password>
        "new_password": <new password>
    }
    """

    # @login_required
    def post(self):
        post_data = request.get_json()
        user = User.query.filter_by(email=post_data['email']).first()
        if user:
            if user.verify_password(post_data['old_password']):
                # Update password and last change time
                user.set_password(post_data['new_password'])
                user.last_password_change = datetime.datetime.utcnow()
                db.session.add(user)
                db.session.commit()
                return make_response(jsonify(dict(
                    status='success',
                    message='password changed'
                ))), 200

        return make_response(jsonify(dict(
            status='fail',
            message='invalid user or password'
        ))), 403


registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')
user_view = UserAPI.as_view('user_api')
logout_view = LogoutAPI.as_view('logout_api')
password_view = ChangePasswordAPI.as_view('password_api')

api.add_url_rule('/auth/register', view_func=registration_view, methods=['POST'])
api.add_url_rule('/auth/login', view_func=login_view, methods=['POST'])
api.add_url_rule('/auth/status', view_func=user_view, methods=['GET'])
api.add_url_rule('/auth/logout', view_func=logout_view, methods=['POST'])
api.add_url_rule('/auth/password', view_func=password_view, methods=['POST'])

