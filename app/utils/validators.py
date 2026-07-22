"""Input validation helpers."""
import re
from email_validator import validate_email, EmailNotValidError


EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PASSWORD_MIN_LEN = 8


def validate_registration(email: str, password: str, username: str) -> tuple[bool, str]:
    """Validate registration fields."""
    username = (username or "").strip()
    email = (email or "").strip().lower()
    password = password or ""

    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(username) > 50:
        return False, "Username must be at most 50 characters."
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return False, "Invalid email address."
    if len(password) < PASSWORD_MIN_LEN:
        return False, f"Password must be at least {PASSWORD_MIN_LEN} characters."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return False, "Password must contain letters and numbers."
    return True, ""


def validate_login(email: str, password: str) -> tuple[bool, str]:
    """Validate login fields."""
    if not (email or "").strip():
        return False, "Email is required."
    if not password:
        return False, "Password is required."
    return True, ""


def validate_prediction_text(text: str, max_len: int = 5000) -> tuple[bool, str]:
    """Validate text submitted for prediction."""
    text = (text or "").strip()
    if not text:
        return False, "Text cannot be empty."
    if len(text) > max_len:
        return False, f"Text must be at most {max_len} characters."
    return True, ""
