from functools import wraps

from flask import jsonify

from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
)


def role_required(role):

    def wrapper(fn):

        @wraps(fn)

        @jwt_required()
        def decorator(*args, **kwargs):

            current_user = get_jwt_identity()

            if current_user['role'] != role:

                return jsonify({
                    "message": "Access denied"
                }), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper