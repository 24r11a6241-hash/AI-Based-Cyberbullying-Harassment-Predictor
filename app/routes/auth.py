"""Authentication API routes."""
from datetime import timedelta
from flask import Blueprint, request, jsonify, current_app, session, g
from app.utils.decorators import jwt_required
from app.services.auth_service import register_user, authenticate_user, create_access_token
from app.models.repository import serialize_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")
    username = data.get("username", "")

    user, err = register_user(email, password, username)
    if err:
        current_app.logger.info("Registration failed for %s: %s", email, err)
        return jsonify({"error": err}), 400

    token = create_access_token(
        user["email"],
        current_app.config["JWT_SECRET_KEY"],
        current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
    )
    return jsonify({"message": "Registration successful.", "token": token, "user": user}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")

    user, err = authenticate_user(email, password)
    if err:
        current_app.logger.info("Login failed for %s", email)
        return jsonify({"error": err}), 401

    token = create_access_token(
        user["email"],
        current_app.config["JWT_SECRET_KEY"],
        current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
    )
    session["access_token"] = token
    return jsonify({"message": "Login successful.", "token": token, "user": serialize_user(user)})


@auth_bp.route("/me", methods=["GET"])
@jwt_required
def me():
    return jsonify({"user": serialize_user(g.current_user)})
