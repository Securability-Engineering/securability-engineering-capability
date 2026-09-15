"""
profile_api.py — User profile management for the customer portal.

Part of customerportal/, a B2C SaaS app. Database is PostgreSQL.
Authentication is provided by Flask-Login session middleware.
"""
import logging
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
import psycopg2

bp = Blueprint("profile", __name__, url_prefix="/api/profile")

logger = logging.getLogger(__name__)

# Database connection — injected at app init
db_conn = None


def init_db(conn):
    global db_conn
    db_conn = conn


@bp.route("/me", methods=["GET"])
@login_required
def get_profile():
    cur = db_conn.cursor()
    cur.execute(
        "SELECT id, email, display_name, role, is_admin FROM users WHERE id = %s",
        (current_user.id,),
    )
    row = cur.fetchone()
    cur.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(
        {
            "id": row[0],
            "email": row[1],
            "display_name": row[2],
            "role": row[3],
            "is_admin": row[4],
        }
    )


@bp.route("/me", methods=["PATCH"])
@login_required
def update_profile():
    """Update current user's profile fields."""
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "empty body"}), 400

    # Build SET clause from whatever the client sent
    set_parts = []
    values = []
    for key, value in data.items():
        set_parts.append(f"{key} = %s")
        values.append(value)

    values.append(current_user.id)
    sql = f"UPDATE users SET {', '.join(set_parts)} WHERE id = %s"
    cur = db_conn.cursor()
    cur.execute(sql, values)
    db_conn.commit()
    cur.close()

    print(f"Updated profile for user {current_user.id}")
    return jsonify({"status": "updated"})


@bp.route("/me/avatar", methods=["POST"])
@login_required
def upload_avatar():
    """Upload a profile avatar image."""
    avatar = request.files.get("avatar")
    if not avatar:
        return jsonify({"error": "no file"}), 400

    # Save to disk under the user's id
    avatar.save(f"/var/uploads/avatars/{current_user.id}.png")
    print(f"Avatar uploaded for {current_user.id}")
    return jsonify({"status": "uploaded"})
