import os
from flask import Flask
from .extensions import db, migrate, jwt, login_manager
from .config import config_by_name


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    cfg = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(cfg)

    # Ensure folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.admin import admin_bp
    from .routes.api_auth import api_auth_bp
    from .routes.api_workshops import api_workshops_bp
    from .routes.api_meetings import api_meetings_bp
    from .routes.api_payments import api_payments_bp
    from .routes.api_admin import api_admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp, url_prefix="/dashboard")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_auth_bp, url_prefix="/api/auth")
    app.register_blueprint(api_workshops_bp, url_prefix="/api/workshops")
    app.register_blueprint(api_meetings_bp, url_prefix="/api/meetings")
    app.register_blueprint(api_payments_bp, url_prefix="/api/payments")
    app.register_blueprint(api_admin_bp, url_prefix="/api/admin")

    # Context processor: expose config & request to all templates
    @app.context_processor
    def inject_globals():
        from flask import request
        return {
            "config": app.config,
            "request": request,
        }

    # Security headers
    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("shared/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template("shared/403.html"), 403

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()
        _seed_admin(app)

    return app


def _seed_admin(app):
    """Create default admin account if not exists."""
    from .models.user import User, UserRole
    from werkzeug.security import generate_password_hash

    email = app.config.get("ADMIN_EMAIL", "admin@eventnet.io")
    if not User.query.filter_by(email=email).first():
        admin = User(
            email=email,
            username="admin",
            first_name="Super",
            last_name="Admin",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            password_hash=generate_password_hash(
                app.config.get("ADMIN_PASSWORD", "Admin@1234")
            ),
        )
        db.session.add(admin)
        db.session.commit()
