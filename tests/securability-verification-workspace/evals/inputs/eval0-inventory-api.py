"""Inventory API — warehouse item management."""

from flask import Flask, request, jsonify, g
import jwt
import sqlite3
import logging

app = Flask(__name__)

logger = logging.getLogger("inventory")
logging.basicConfig(level=logging.INFO)

JWT_SECRET = "warehouse-shared-secret"
ALLOWED_FIELDS = {"name", "sku", "quantity"}
MAX_BODY = 1 * 1024 * 1024  # 1 MB


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("inventory.db")
        g.db.row_factory = sqlite3.Row
    return g.db


@app.before_request
def enforce_body_limit():
    if request.content_length and request.content_length > MAX_BODY:
        return jsonify({"error": "Payload too large"}), 413


@app.before_request
def authenticate():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    if not token:
        return jsonify({"error": "Missing token"}), 401
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        g.user_id = payload["sub"]
        g.tenant_id = payload["tenant_id"]
    except jwt.PyJWTError:
        return jsonify({"error": "Invalid token"}), 401


@app.post("/items")
def create_item():
    data = request.get_json(force=True)
    extra = set(data.keys()) - ALLOWED_FIELDS
    if extra:
        return jsonify({"error": f"Unexpected fields: {extra}"}), 422
    db = get_db()
    db.execute(
        "INSERT INTO items (name, sku, quantity, tenant_id, created_by) VALUES (?, ?, ?, ?, ?)",
        (data["name"], data["sku"], data["quantity"], g.tenant_id, g.user_id),
    )
    db.commit()
    logger.info(
        "item_created",
        extra={"actor": g.user_id, "action": "create_item", "target": data["sku"], "outcome": "success"},
    )
    return jsonify({"status": "created"}), 201


@app.get("/items")
def list_items():
    db = get_db()
    rows = db.execute(
        "SELECT id, name, sku, quantity FROM items WHERE tenant_id = ?",
        (g.tenant_id,),
    ).fetchall()
    return jsonify([dict(r) for r in rows])
