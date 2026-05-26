from flask_jwt_extended import jwt_required

def auth_required():
    return jwt_required()