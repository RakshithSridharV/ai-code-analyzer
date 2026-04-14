"""
auth.py
───────
Flask Blueprint for user authentication.

Routes
──────
  POST /auth/register  — Create a new account
  POST /auth/login     — Login and receive a JWT access token
  GET  /auth/me        — Return current user info (JWT required)
"""

import bcrypt
import logging
from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from database import get_user_by_email, get_user_by_id, save_user

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _check_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── Routes ─────────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
def register():
    data     = request.get_json(silent=True) or {}
    email    = (data.get("email") or "").strip()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    # ── Validate email ─────────────────────────────────────────────────────────
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError as exc:
        return jsonify({"error": str(exc)}), 400

    # ── Validate username ──────────────────────────────────────────────────────
    if not username or len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400
    if len(username) > 32:
        return jsonify({"error": "Username must be 32 characters or fewer."}), 400

    # ── Validate password ──────────────────────────────────────────────────────
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    # ── Check existing user ────────────────────────────────────────────────────
    if get_user_by_email(email):
        return jsonify({"error": "An account with that email already exists."}), 409

    # ── Create user ────────────────────────────────────────────────────────────
    try:
        user_id = save_user(email, username, _hash_password(password))
    except Exception as exc:
        logger.error("Register error: %s", exc)
        # Could be a duplicate username
        return jsonify({"error": "Registration failed. Username may already be taken."}), 409

    access_token = create_access_token(identity=str(user_id))
    logger.info("New user registered: %s (id=%d)", email, user_id)
    return jsonify({
        "token":    access_token,
        "user":     {"id": user_id, "email": email, "username": username},
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json(silent=True) or {}
    email    = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = get_user_by_email(email)
    if not user or not _check_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid email or password."}), 401

    access_token = create_access_token(identity=str(user["id"]))
    logger.info("User logged in: %s (id=%d)", email, user["id"])
    return jsonify({
        "token": access_token,
        "user":  {"id": user["id"], "email": user["email"], "username": user["username"]},
    })


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user    = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({
        "id":         user["id"],
        "email":      user["email"],
        "username":   user["username"],
        "created_at": user["created_at"],
    })
