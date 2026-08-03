"""
auth.py — Password hashing, JWT issuing/verification, and the route guard.

Tokens are stateless JWTs signed with JWT_SECRET. If JWT_SECRET is not set we
generate a random one at boot: the app still works, but every restart
invalidates existing logins — so set it in .env for anything real.
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

# This module reads env vars at import time, which happens before app.py's own
# load_dotenv() call — so load it here too. Repeat calls are harmless.
load_dotenv()

TOKEN_TTL_DAYS = 7
_ALGORITHM = "HS256"

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    JWT_SECRET = secrets.token_urlsafe(48)
    print("⚠️  JWT_SECRET not set — generated a temporary one. Logins will not survive a restart.")


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


def create_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),  # RFC 7519 requires 'sub' to be a string
        "iat": now,
        "exp": now + timedelta(days=TOKEN_TTL_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=_ALGORITHM)


def decode_token(token: str) -> int | None:
    """Return the user id encoded in the token, or None if it is invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[_ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        return None


def _user_id_from_request() -> int | None:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    return decode_token(header[7:].strip())


def require_auth(view):
    """Reject the request unless it carries a valid token. Sets g.user_id."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        user_id = _user_id_from_request()
        if user_id is None:
            return jsonify({"error": "Authentication required"}), 401
        g.user_id = user_id
        return view(*args, **kwargs)

    return wrapper


def validate_credentials(email: str, password: str, name: str | None = None) -> str | None:
    """Return an error message for bad signup input, or None if it all checks out."""
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        return "A valid email address is required."
    if not password or len(password) < 8:
        return "Password must be at least 8 characters."
    if name is not None and not name.strip():
        return "Name is required."
    return None
