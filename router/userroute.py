from flask import Blueprint

from service.userservice import (
    signup_service,
    login_service
)

user_bp = Blueprint(
    'user_bp',
    __name__
)

# SIGNUP
@user_bp.route('/signup', methods=['POST'])
def signup():
    return signup_service()


# LOGIN
@user_bp.route('/login', methods=['POST'])
def login():
    return login_service()