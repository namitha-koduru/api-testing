import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app


def generate_qr_token(registration_id: int, user_id: int, event_id: int) -> tuple[str, datetime]:
    secret = current_app.config["QR_TOKEN_SECRET"]
    expiry_hours = current_app.config["QR_TOKEN_EXPIRY_HOURS"]
    expires_at = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
    payload = {
        "reg_id": registration_id,
        "user_id": user_id,
        "event_id": event_id,
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token, expires_at


def verify_qr_token(token: str) -> dict | None:
    try:
        secret = current_app.config["QR_TOKEN_SECRET"]
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None


def verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
    secret = current_app.config["RAZORPAY_KEY_SECRET"]
    body = f"{order_id}|{payment_id}"
    expected = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_razorpay_webhook(body: bytes, signature: str) -> bool:
    secret = current_app.config.get("RAZORPAY_WEBHOOK_SECRET", "")
    if not secret:
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
