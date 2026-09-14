"""Password reset handler — eval fixture.

This handler has an intentional defect: reset tokens are NOT invalidated
after first use, so F-01-R2 (single-use token) is refutable.
F-01-R1 (enumeration parity) IS satisfied: same response for both paths.
F-01-R3 (logging) uses print() — structured logging is absent.
"""

from flask import Flask, request, jsonify
import hashlib
import secrets
import time

app = Flask(__name__)

# In-memory stores for the fixture
USERS = {"alice@example.com": {"id": "u-1", "password_hash": "..."}}
TOKENS = {}  # token_hash -> {email, issued_at}


@app.post("/reset")
def request_reset():
    data = request.get_json(force=True)
    email = data.get("email", "").strip().lower()
    if not email or "@" not in email:
        return jsonify({"error": "Invalid email format"}), 422

    # Enumeration parity: same response regardless of whether email exists
    if email in USERS:
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        TOKENS[token_hash] = {"email": email, "issued_at": time.time()}
        # Would send email here
        print(f"Reset token issued for {email}")

    return jsonify({"message": "If an account exists, a reset link was sent."}), 200


@app.post("/reset/confirm")
def confirm_reset():
    data = request.get_json(force=True)
    token = data.get("token", "")
    new_password = data.get("password", "")
    if not token or not new_password:
        return jsonify({"error": "Missing fields"}), 400

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    record = TOKENS.get(token_hash)

    if not record:
        return jsonify({"error": "Invalid or expired token"}), 400

    # Check expiry (15 minutes)
    if time.time() - record["issued_at"] > 900:
        return jsonify({"error": "Invalid or expired token"}), 400

    # BUG: token is NOT deleted after use — reuse is possible
    # This means F-01-R2 acceptance criterion is NOT met.
    user = USERS.get(record["email"])
    if user:
        user["password_hash"] = hashlib.sha256(new_password.encode()).hexdigest()
        print(f"Password reset for {record['email']}")

    return jsonify({"message": "Password has been reset."}), 200
