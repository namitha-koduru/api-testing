from flask import request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from model.usermodel import User
from config.db import db


def signup_service():

    data = request.json

    existing_user = User.query.filter_by(
        username=data['username']
    ).first()

    if existing_user:
        return jsonify({
            "message": "User already exists"
        }), 400

    hashed_password = generate_password_hash(
        data['password']
    )

    user = User(
        username=data['username'],
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Signup successful"
    }), 201


def login_service():

    data = request.json

    user = User.query.filter_by(
        username=data['username']
    ).first()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    if check_password_hash(
        user.password,
        data['password']
    ):

        token = create_access_token(
            identity=user.username
        )

        return jsonify({
            "token": token
        })

    return jsonify({
        "message": "Invalid password"
    }), 401