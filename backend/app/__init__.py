import os

from flask import Flask, jsonify

from app.api import api
from app.config import config_by_name
from app.extensions import init_extensions, socketio
from app.websocket.handlers import register_socket_handlers


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)

    init_extensions(app)
    api.init_app(app)
    register_socket_handlers(app)

    @app.route("/")
    def home():
        return jsonify({
            "name": "EventNet API",
            "version": "1.0.0",
            "docs": "/api/docs",
            "status": "running",
        })

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    with app.app_context():
        from app import models  # noqa: F401

    return app
