"""Severity and sentiment helpers for predictions."""
from typing import Any


SEVERITY_ORDER = ["Low", "Medium", "High", "Critical"]

CATEGORY_WEIGHT = {
    "Normal": 0.0,
    "Offensive": 0.35,
    "Toxic": 0.55,
    "Cyberbullying": 0.65,
    "Hate Speech": 0.75,
    "Threat": 0.85,
    "Identity Attack": 0.8,
    "Sexual Harassment": 0.7,
}


def compute_severity(primary_label: str, confidence: float) -> str:
    """Map label + confidence to severity tier."""
    if primary_label == "Normal":
        return "Low"
    base = CATEGORY_WEIGHT.get(primary_label, 0.5)
    score = min(1.0, base * 0.6 + confidence * 0.4)
    if score >= 0.85:
        return "Critical"
    if score >= 0.65:
        return "High"
    if score >= 0.4:
        return "Medium"
    return "Low"


def compute_sentiment(primary_label: str, confidence: float) -> str:
    """Simple sentiment from toxicity prediction."""
    if primary_label == "Normal":
        return "Positive" if confidence > 0.6 else "Neutral"
    if primary_label in ("Threat", "Hate Speech", "Identity Attack"):
        return "Very Negative"
    if primary_label in ("Toxic", "Cyberbullying", "Sexual Harassment"):
        return "Negative"
    return "Neutral"


def build_prediction_summary(
    primary_label: str,
    confidence: float,
    all_scores: dict[str, float],
    toxic_keywords: list[str],
) -> dict[str, Any]:
    """Assemble UI/API prediction payload."""
    return {
        "primary_label": primary_label,
        "confidence": round(confidence, 4),
        "confidence_percent": round(confidence * 100, 2),
        "severity": compute_severity(primary_label, confidence),
        "sentiment": compute_sentiment(primary_label, confidence),
        "all_scores": {k: round(v, 4) for k, v in all_scores.items()},
        "toxic_keywords": toxic_keywords,
        "is_harmful": primary_label != "Normal",
    }
