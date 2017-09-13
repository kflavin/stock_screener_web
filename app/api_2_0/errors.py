from flask import jsonify, abort, request

from . import api as api_2_0


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': "unauthorized user", 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': "forbidden", "message": message})
    response.status_code = 403
    return response


def conflict(message):
    response = jsonify({'error': "conflict", "message": message})
    response.status_code = 409
    return response


# Currently unused
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


# Currently unused
@api_2_0.app_errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@api_2_0.app_errorhandler(405)
def handle_server_error(error):
    response = jsonify({'error': 'method not accepted'})
    response.status_code = 405
    return response
