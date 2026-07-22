"""Admin REST API: analytics, users, model retraining."""
import os
from flask import Blueprint, request, jsonify, current_app, g
from app.utils.decorators import admin_required
from app.extensions import get_db
from app.services.analytics_service import get_dashboard_stats, get_recent_predictions, top_toxic_keywords
from app.models.repository import serialize_user
from app.services.ml_service import ToxicityModelService

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def stats():
    return jsonify(get_dashboard_stats(get_db()))


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    db = get_db()
    users = [serialize_user(u) for u in db.users.find().sort("created_at", -1).limit(500)]
    return jsonify({"users": users, "count": len(users)})


@admin_bp.route("/predictions/recent", methods=["GET"])
@admin_required
def recent_predictions():
    limit = min(int(request.args.get("limit", 20)), 100)
    return jsonify({"items": get_recent_predictions(get_db(), limit=limit)})


@admin_bp.route("/keywords/top", methods=["GET"])
@admin_required
def top_keywords():
    return jsonify({"keywords": top_toxic_keywords(get_db())})


@admin_bp.route("/model/retrain", methods=["POST"])
@admin_required
def retrain_model():
    """Retrain classifier from configured dataset path or uploaded path."""
    data = request.get_json(silent=True) or {}
    csv_path = data.get("dataset_path") or current_app.config.get("TRAIN_DATA_PATH") or current_app.config.get(
        "SAMPLE_DATA_PATH", "data/sample_dataset.csv"
    )

    if not os.path.isfile(csv_path):
        return jsonify({"error": f"Dataset not found: {csv_path}"}), 400

    try:
        service = ToxicityModelService(current_app.config)
        metrics = service.train(csv_path)
        current_app.ml_service = service
        current_app.logger.info("Model retrained by admin %s", g.current_user["email"])
        return jsonify({"message": "Model retrained successfully.", "metrics": metrics})
    except Exception as exc:
        current_app.logger.exception("Retrain failed: %s", exc)
        return jsonify({"error": str(exc)}), 500


@admin_bp.route("/model/status", methods=["GET"])
@admin_required
def model_status():
    svc = current_app.ml_service
    return jsonify(
        {
            "loaded": svc.is_loaded(),
            "metrics": svc.metrics,
            "paths": {
                "model": svc.model_path,
                "vectorizer": svc.vectorizer_path,
                "label_encoder": svc.label_encoder_path,
            },
        }
    )
