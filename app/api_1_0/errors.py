from flask import jsonify

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
