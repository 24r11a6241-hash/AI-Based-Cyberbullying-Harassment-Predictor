"""Public REST API for predictions and history."""
from flask import Blueprint, request, jsonify, current_app, g
from app.utils.decorators import jwt_required
from app.utils.validators import validate_prediction_text
from app.extensions import get_db
from app.models.repository import save_prediction, get_user_predictions, serialize_prediction

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "model_loaded": current_app.ml_service.is_loaded(),
        }
    )


@api_bp.route("/predict", methods=["POST"])
@jwt_required
def predict():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    save_history = data.get("save_history", True)

    ok, err = validate_prediction_text(text)
    if not ok:
        return jsonify({"error": err}), 400

    if not current_app.ml_service.is_loaded():
        return jsonify({"error": "Model not available. Contact administrator."}), 503

    try:
        result = current_app.ml_service.predict(text)
    except Exception as exc:
        current_app.logger.exception("Prediction failed: %s", exc)
        return jsonify({"error": "Prediction failed."}), 500

    prediction_id = None
    if save_history:
        prediction_id = save_prediction(db=get_db(), user_email=g.current_user["email"], text=text, result=result)

    payload = {**result, "prediction_id": prediction_id}
    return jsonify(payload)


@api_bp.route("/history", methods=["GET"])
@jwt_required
def history():
    limit = min(int(request.args.get("limit", 50)), 200)
    skip = max(int(request.args.get("skip", 0)), 0)
    items = get_user_predictions(get_db(), g.current_user["email"], limit=limit, skip=skip)
    return jsonify({"items": items, "count": len(items)})


@api_bp.route("/history/<prediction_id>", methods=["GET"])
@jwt_required
def history_item(prediction_id):
    from app.models.repository import oid

    db = get_db()
    oid_val = oid(prediction_id)
    if not oid_val:
        return jsonify({"error": "Invalid prediction id."}), 400
    doc = db.predictions.find_one({"_id": oid_val, "user_email": g.current_user["email"]})
    if not doc:
        return jsonify({"error": "Prediction not found."}), 404
    return jsonify(serialize_prediction(doc))


@api_bp.route("/metrics", methods=["GET"])
@jwt_required
def metrics():
    """Return last training metrics (available to logged-in users)."""
    return jsonify({"metrics": current_app.ml_service.metrics or {}})
