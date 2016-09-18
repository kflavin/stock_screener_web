from flask import g
from flask.ext.httpauth import HTTPBasicAuth
from ..models import User
from .errors import unauthorized
from . import api

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    if not email or not password:
        return False

    user = User.query.filter(User.email.ilike(email)).first()
    g.current_user = user

    return user.verify_password(password)


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.confirmed_at:
        return unauthorized("Invalid credentials")
