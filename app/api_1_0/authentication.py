from flask import g
from flask_httpauth import HTTPBasicAuth
from ..models import User
from .errors import unauthorized, InvalidUsage
from . import api as api_1_0

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    if not email or not password:
        return False

    user = User.query.filter(User.email.ilike(email)).first()
    g.current_user = user

    if not user:
        raise InvalidUsage("Invalid credentials", status_code=401)

    return user.verify_password(password)


@api_1_0.before_request
@auth.login_required
def before_request():
    if not g.current_user.confirmed_at:
        return unauthorized("Invalid credentials")
