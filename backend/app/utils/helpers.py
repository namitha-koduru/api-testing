import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import current_app, g, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request
from app.utils.slugify import slugify as _slugify

from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import ActivityLog, User, UserRole


def generate_slug(text: str, model=None, field="slug") -> str:
    base = _slugify(text) if _slugify else re.sub(r"[^\w\s-]", "", text.lower()).strip().replace(" ", "-")
    slug = base
    counter = 1
    if model:
        while db.session.query(model).filter(getattr(model, field) == slug).first():
            slug = f"{base}-{counter}"
            counter += 1
    return slug


def generate_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def generate_verification_code() -> str:
    return secrets.token_hex(16)


def paginate_query(query, page: int = 1, per_page: int = 20):
    page = max(1, page)
    per_page = min(max(1, per_page), 100)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": pagination.items,
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }


def log_activity(user_id, action, entity_type=None, entity_id=None, event_id=None, metadata=None):
    log = ActivityLog(
        user_id=user_id,
        event_id=event_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_address=request.remote_addr if request else None,
        user_agent=request.headers.get("User-Agent", "")[:500] if request else None,
        metadata_json=metadata or {},
    )
    db.session.add(log)
    db.session.commit()
    return log


def get_current_user() -> User | None:
    return getattr(g, "current_user", None)


def jwt_required_custom(optional=False):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=optional)
                identity = get_jwt_identity()
                if identity:
                    user = User.query.filter_by(id=identity, is_deleted=False, is_active=True).first()
                    g.current_user = user
                    g.jwt_claims = get_jwt()
                elif not optional:
                    return jsonify({"message": "Authentication required"}), 401
            except Exception:
                if optional:
                    g.current_user = None
                else:
                    return jsonify({"message": "Invalid or expired token"}), 401
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def role_required(*roles: UserRole):
    allowed = {r.value for r in roles}
    allowed.add(UserRole.ADMIN.value)

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = User.query.get(get_jwt_identity())
            if not user:
                return jsonify({"message": "User not found"}), 404
            if user.role.value not in allowed:
                return jsonify({"message": "Insufficient permissions"}), 403
            g.current_user = user
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def utc_now():
    return datetime.now(timezone.utc)


def parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
