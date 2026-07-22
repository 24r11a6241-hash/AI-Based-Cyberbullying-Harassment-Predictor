"""Flask application factory."""
import os
from flask import Flask
from flask_cors import CORS

from app.config import config_by_name
from app.extensions import init_mongo, get_db
from app.utils.logger import setup_logging
from app.services.auth_service import ensure_admin_user
from app.services.ml_service import ToxicityModelService


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    config_name = config_name or os.getenv("FLASK_ENV", "development")
    if config_name not in config_by_name:
        config_name = "development"

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_by_name[config_name])
    CORS(app, supports_credentials=True)

    setup_logging(app)
    init_mongo(app)

    os.makedirs("logs", exist_ok=True)
    os.makedirs("saved_models", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    ml_service = ToxicityModelService(app.config)
    if not ml_service.load():
        app.logger.warning(
            "ML model not found. Run `python -m ml.train` or admin retrain API."
        )
    app.ml_service = ml_service

    from app.routes.pages import pages_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")

    with app.app_context():
        try:
            ensure_admin_user(app)
        except Exception as exc:
            app.logger.warning("Could not ensure admin user (MongoDB unavailable): %s", exc)

    @app.context_processor
    def inject_user():
        from flask import g, request
        from app.utils.decorators import decode_token, _extract_token
        from app.models.repository import serialize_user

        token = _extract_token()
        if token:
            payload = decode_token(token, app.config["JWT_SECRET_KEY"])
            if payload:
                db = get_db()
                u = db.users.find_one({"email": payload.get("sub")})
                if u:
                    return {"user": serialize_user(u)}
        return {"user": None}

    @app.errorhandler(404)
    def not_found(e):
        from flask import request, jsonify

        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource not found."}), 404
        from flask import render_template

        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import request, jsonify

        app.logger.exception("Internal server error: %s", e)
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error."}), 500
        from flask import render_template

        return render_template("500.html"), 500

    @app.errorhandler(413)
    def too_large(e):
        from flask import jsonify

        return jsonify({"error": "Request payload too large."}), 413

    return app
