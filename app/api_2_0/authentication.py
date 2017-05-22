from flask.views import MethodView

from flask import g, request, make_response, jsonify, current_app
from flask.ext.httpauth import HTTPBasicAuth
from ..models import User
from .. import db
from .errors import unauthorized, InvalidUsage
from . import api


class RegisterAPI(MethodView):
    """
    Register a user
    """
    def post(self):
        post_data = request.get_json()
        user = User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = User(
                    email = post_data.get('email'),
                    password = post_data.get('password')
                )

                db.session.add(user)
                db.session.commit()
                auth_token = user.encode_auth_token(user.id)
                response_object = {
                    'status': 'success',
                    'message': 'Registered user',
                    'auth_token': auth_token.decode()
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
                'message': 'User already exists, please login'
            }
            return make_response(jsonify(response_object)), 202


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
                )))

            if user.verify_password(post_data.get('password')):
                return make_response(jsonify(dict(
                    status='success',
                    message='Logged in',
                    token=user.encode_auth_token(user.id).decode()
                )))
            else:
                return make_response(jsonify(dict(
                    status='fail',
                    message='User does not exist, or password is invalid'
                )))
        except Exception as e:
            current_app.logger.debug(e.message)
            return make_response((jsonify(dict(
                status='fail',
                message='Unknown error, please try again'
            )), 500))



registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')

api.add_url_rule('/auth/register', view_func=registration_view, methods=['POST'])
api.add_url_rule('/auth/login', view_func=login_view, methods=['POST'])

# auth = HTTPBasicAuth()
#
#
# @auth.verify_password
# def verify_password(email, password):
#     if not email or not password:
#         return False
#
#     user = User.query.filter(User.email.ilike(email)).first()
#     g.current_user = user
#
#     if not user:
#         raise InvalidUsage("Invalid credentials", status_code=401)
#
#     return user.verify_password(password)


#@api.before_request
#@auth.login_required
#def before_request():
#    if not g.current_user.confirmed_at:
#        return unauthorized("Invalid credentials")
