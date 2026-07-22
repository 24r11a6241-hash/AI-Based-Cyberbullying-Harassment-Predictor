"""Server-rendered page routes."""
from flask import Blueprint, render_template, g, redirect, url_for
from app.utils.decorators import login_required_page, admin_required_page
from app.extensions import get_db
from app.services.analytics_service import get_dashboard_stats
from app.models.repository import get_user_predictions, serialize_user

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def home():
    return render_template("home.html")


@pages_bp.route("/login")
def login():
    return render_template("login.html")


@pages_bp.route("/register")
def register():
    return render_template("register.html")


@pages_bp.route("/dashboard")
@login_required_page
def dashboard():
    db = get_db()
    stats = get_dashboard_stats(db)
    user_stats = {
        "my_predictions": db.predictions.count_documents({"user_email": g.current_user["email"]}),
    }
    return render_template(
        "dashboard.html",
        user=serialize_user(g.current_user),
        stats=stats,
        user_stats=user_stats,
    )


@pages_bp.route("/predict")
@login_required_page
def predict_page():
    return render_template("predict.html", user=serialize_user(g.current_user))


@pages_bp.route("/history")
@login_required_page
def history():
    db = get_db()
    history_items = get_user_predictions(db, g.current_user["email"], limit=100)
    return render_template(
        "history.html",
        user=serialize_user(g.current_user),
        history=history_items,
    )


@pages_bp.route("/admin")
@admin_required_page
def admin_panel():
    from app.services.analytics_service import get_recent_predictions, top_toxic_keywords

    db = get_db()
    stats = get_dashboard_stats(db)
    recent = get_recent_predictions(db, limit=15)
    keywords = top_toxic_keywords(db)
    metrics = {}
    from flask import current_app

    if current_app.ml_service.metrics:
        metrics = current_app.ml_service.metrics
    return render_template(
        "admin.html",
        user=serialize_user(g.current_user),
        stats=stats,
        recent=recent,
        keywords=keywords,
        metrics=metrics,
        model_loaded=current_app.ml_service.is_loaded(),
    )


@pages_bp.route("/reports/confusion-matrix.png")
@login_required_page
def confusion_matrix_image():
    from flask import send_from_directory
    import os
    path = os.path.abspath("reports")
    return send_from_directory(path, "confusion_matrix.png")


@pages_bp.route("/reports")
@login_required_page
def reports():
    from flask import current_app
    import os

    metrics = current_app.ml_service.metrics or {}
    cm_exists = os.path.isfile("reports/confusion_matrix.png")
    return render_template(
        "reports.html",
        user=serialize_user(g.current_user),
        metrics=metrics,
        cm_exists=cm_exists,
    )


@pages_bp.route("/logout")
def logout():
    from flask import session

    session.pop("access_token", None)
    return redirect(url_for("pages.login") + "?logout=1")
