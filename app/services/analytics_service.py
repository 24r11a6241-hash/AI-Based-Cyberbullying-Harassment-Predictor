"""Analytics aggregation for admin dashboard."""
from datetime import datetime, timedelta, timezone
from collections import Counter


def get_dashboard_stats(db) -> dict:
    """Summary metrics for admin and user dashboards."""
    total_users = db.users.count_documents({})
    total_predictions = db.predictions.count_documents({})
    harmful = db.predictions.count_documents({"primary_label": {"$ne": "Normal"}})

    label_pipeline = [
        {"$group": {"_id": "$primary_label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    by_label = {r["_id"]: r["count"] for r in db.predictions.aggregate(label_pipeline)}

    severity_pipeline = [
        {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
    ]
    by_severity = {r["_id"]: r["count"] for r in db.predictions.aggregate(severity_pipeline)}

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent = db.predictions.count_documents({"created_at": {"$gte": week_ago}})

    return {
        "total_users": total_users,
        "total_predictions": total_predictions,
        "harmful_predictions": harmful,
        "harmful_rate": round(harmful / total_predictions, 4) if total_predictions else 0,
        "predictions_by_label": by_label,
        "predictions_by_severity": by_severity,
        "predictions_last_7_days": recent,
    }


def get_recent_predictions(db, limit: int = 10) -> list[dict]:
    """Latest predictions for admin view."""
    from app.models.repository import serialize_prediction

    cursor = db.predictions.find().sort("created_at", -1).limit(limit)
    return [serialize_prediction(d) for d in cursor]


def top_toxic_keywords(db, limit: int = 15) -> list[dict]:
    """Aggregate toxic keyword frequency from history."""
    counter: Counter = Counter()
    for doc in db.predictions.find({"toxic_keywords": {"$exists": True, "$ne": []}}):
        counter.update(doc.get("toxic_keywords", []))
    return [{"keyword": k, "count": v} for k, v in counter.most_common(limit)]
