"""Authentication service: registration, login, password hashing."""
from datetime import datetime, timezone
import bcrypt
import jwt
from app.extensions import get_db
from app.utils.validators import validate_registration, validate_login
from app.models.repository import serialize_user


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(email: str, secret: str, expires_delta) -> str:
    exp = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": email, "exp": exp}
    return jwt.encode(payload, secret, algorithm="HS256")


def register_user(email: str, password: str, username: str) -> tuple[dict | None, str]:
    """Register a new user. Returns (user_doc, error_message)."""
    ok, err = validate_registration(email, password, username)
    if not ok:
        return None, err

    db = get_db()
    email = email.strip().lower()
    if db.users.find_one({"email": email}):
        return None, "Email already registered."
    if db.users.find_one({"username": username.strip()}):
        return None, "Username already taken."

    user = {
        "email": email,
        "username": username.strip(),
        "password_hash": hash_password(password),
        "is_admin": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    result = db.users.insert_one(user)
    user["_id"] = result.inserted_id
    return serialize_user(user), ""


def authenticate_user(email: str, password: str) -> tuple[dict | None, str]:
    """Validate credentials and return user without password hash."""
    ok, err = validate_login(email, password)
    if not ok:
        return None, err

    db = get_db()
    user = db.users.find_one({"email": email.strip().lower()})
    if not user or not verify_password(password, user["password_hash"]):
        return None, "Invalid email or password."

    return serialize_user(user), ""


def ensure_admin_user(app):
    """Create default admin if none exists."""
    db = get_db()
    admin_email = app.config["ADMIN_EMAIL"].lower()
    if db.users.find_one({"is_admin": True}):
        return
    if db.users.find_one({"email": admin_email}):
        db.users.update_one({"email": admin_email}, {"$set": {"is_admin": True}})
        return
    db.users.insert_one(
        {
            "email": admin_email,
            "username": "admin",
            "password_hash": hash_password(app.config["ADMIN_PASSWORD"]),
            "is_admin": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )
