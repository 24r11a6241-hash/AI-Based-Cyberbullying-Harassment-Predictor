"""JWT and role-based decorators."""
import functools
from flask import request, jsonify, g, redirect, url_for, session
import jwt
from app.extensions import get_db


def _extract_token():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return request.cookies.get("access_token") or session.get("access_token")


def decode_token(token: str, secret: str):
    """Decode JWT and return payload or None."""
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def jwt_required(f):
    """Require valid JWT for API routes."""

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        from flask import current_app

        token = _extract_token()
        if not token:
            return jsonify({"error": "Authentication required."}), 401
        payload = decode_token(token, current_app.config["JWT_SECRET_KEY"])
        if not payload:
            return jsonify({"error": "Invalid or expired token."}), 401
        db = get_db()
        user = db.users.find_one({"email": payload.get("sub")})
        if not user:
            return jsonify({"error": "User not found."}), 401
        g.current_user = user
        g.token_payload = payload
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """Require admin role."""

    @functools.wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        if not g.current_user.get("is_admin"):
            return jsonify({"error": "Admin access required."}), 403
        return f(*args, **kwargs)

    return decorated


def login_required_page(f):
    """Require login for server-rendered pages."""

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        from flask import current_app

        token = _extract_token()
        if not token:
            return redirect(url_for("pages.login"))
        payload = decode_token(token, current_app.config["JWT_SECRET_KEY"])
        if not payload:
            session.pop("access_token", None)
            return redirect(url_for("pages.login"))
        db = get_db()
        user = db.users.find_one({"email": payload.get("sub")})
        if not user:
            return redirect(url_for("pages.login"))
        g.current_user = user
        return f(*args, **kwargs)

    return decorated


def admin_required_page(f):
    """Require admin for server-rendered admin pages."""

    @functools.wraps(f)
    @login_required_page
    def decorated(*args, **kwargs):
        if not g.current_user.get("is_admin"):
            return redirect(url_for("pages.dashboard"))
        return f(*args, **kwargs)

    return decorated
