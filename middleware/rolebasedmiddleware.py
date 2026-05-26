from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify

from model.usermodel import User


def role_required(role):

    def wrapper(fn):

        @wraps(fn)
        def decorator(*args, **kwargs):

            current_user = get_jwt_identity()

            user = User.query.filter_by(
                username=current_user
            ).first()

            if user.role != role:

                return jsonify({
                    "message": "Access denied"
                }), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper