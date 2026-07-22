"""MongoDB document helpers for users and predictions."""
from datetime import datetime, timezone
from bson import ObjectId


def serialize_user(user: dict) -> dict:
    """Convert user document for JSON responses."""
    if not user:
        return {}
    return {
        "id": str(user.get("_id", "")),
        "email": user.get("email"),
        "username": user.get("username"),
        "is_admin": bool(user.get("is_admin")),
        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
    }


def serialize_prediction(doc: dict) -> dict:
    """Convert prediction document for JSON responses."""
    if not doc:
        return {}
    return {
        "id": str(doc.get("_id", "")),
        "user_email": doc.get("user_email"),
        "text": doc.get("text"),
        "primary_label": doc.get("primary_label"),
        "confidence": doc.get("confidence"),
        "severity": doc.get("severity"),
        "sentiment": doc.get("sentiment"),
        "all_scores": doc.get("all_scores", {}),
        "toxic_keywords": doc.get("toxic_keywords", []),
        "highlighted_text": doc.get("highlighted_text"),
        "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
    }


def save_prediction(db, user_email: str, text: str, result: dict) -> str:
    """Persist prediction to history."""
    doc = {
        "user_email": user_email,
        "text": text,
        "primary_label": result["primary_label"],
        "confidence": result["confidence"],
        "severity": result["severity"],
        "sentiment": result["sentiment"],
        "all_scores": result["all_scores"],
        "toxic_keywords": result["toxic_keywords"],
        "highlighted_text": result.get("highlighted_text", text),
        "created_at": datetime.now(timezone.utc),
    }
    inserted = db.predictions.insert_one(doc)
    return str(inserted.inserted_id)


def get_user_predictions(db, user_email: str, limit: int = 50, skip: int = 0) -> list[dict]:
    """Fetch prediction history for a user."""
    cursor = (
        db.predictions.find({"user_email": user_email})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return [serialize_prediction(d) for d in cursor]


def oid(value: str):
    """Parse ObjectId safely."""
    try:
        return ObjectId(value)
    except Exception:
        return None
