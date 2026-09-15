"""
auth_service.py — JWT-based password-reset token issuance.

Part of the customer portal backend. Uses pyjwt for token creation
and verification. The Go auth-sidecar validates tokens on the API
gateway side using golang-jwt.
"""
import os
import jwt
import structlog
from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
logger = structlog.get_logger()

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
RESET_TOKEN_TTL = timedelta(minutes=30)


@app.post("/auth/password-reset")
def issue_reset_token():
    data = request.get_json(force=True)
    email = data.get("email")
    if not email or not isinstance(email, str):
        return jsonify({"error": "email required"}), 400

    token = jwt.encode(
        {
            "sub": email,
            "purpose": "password-reset",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + RESET_TOKEN_TTL,
        },
        SECRET_KEY,
        algorithm="HS256",
    )
    logger.info("password_reset_issued", email=email)
    # In production this sends an email; here we return it for testing
    return jsonify({"token": token}), 200


@app.post("/auth/password-reset/verify")
def verify_reset_token():
    data = request.get_json(force=True)
    token = data.get("token")
    if not token:
        return jsonify({"error": "token required"}), 400

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"],
            options={"require": ["sub", "purpose", "exp"]},
        )
    except jwt.ExpiredSignatureError:
        logger.warning("password_reset_expired")
        return jsonify({"error": "token expired"}), 401
    except jwt.InvalidTokenError as exc:
        logger.warning("password_reset_invalid", error=str(exc))
        return jsonify({"error": "invalid token"}), 401

    if payload.get("purpose") != "password-reset":
        return jsonify({"error": "wrong token purpose"}), 401

    return jsonify({"email": payload["sub"], "valid": True}), 200
