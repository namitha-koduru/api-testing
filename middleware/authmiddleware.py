from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from functools import wraps
from flask import jsonify


def auth_required():

    def wrapper(fn):

        @wraps(fn)

        @jwt_required()
        def decorator(*args, **kwargs):

            current_user = get_jwt_identity()

            if not current_user:

                return jsonify({
                    "message": "Unauthorized"
                }), 401

            return fn(*args, **kwargs)

        return decorator

    return wrapper