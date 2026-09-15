"""Inventory management API for a warehouse system."""

import sqlite3
import json
import jwt
import requests
from flask import Flask, request, jsonify, g

app = Flask(__name__)

DB_PATH = "/var/data/inventory.db"
PARTNER_API = "https://partner.example.com/api/v2"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
    return g.db


def current_user():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    return jwt.decode(token, "secret-key-here")


@app.route("/items", methods=["GET"])
def list_items():
    db = get_db()
    category = request.args.get("category", "")
    query = f"SELECT * FROM items WHERE category = '{category}'"
    rows = db.execute(query).fetchall()
    return jsonify(rows)


@app.route("/items/<item_id>", methods=["GET"])
def get_item(item_id):
    db = get_db()
    query = f"SELECT * FROM items WHERE id = '{item_id}'"
    row = db.execute(query).fetchone()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(row)


@app.route("/items", methods=["POST"])
def create_item():
    user = current_user()
    data = request.get_json()
    db = get_db()
    db.execute(
        f"INSERT INTO items (name, category, quantity, owner) "
        f"VALUES ('{data['name']}', '{data['category']}', "
        f"{data['quantity']}, '{user['sub']}')"
    )
    db.commit()
    print(f"Item created by {user['sub']}: {data['name']}")
    return jsonify({"status": "created"}), 201


@app.route("/items/<item_id>/transfer", methods=["POST"])
def transfer_item(item_id):
    data = request.get_json()
    target_warehouse = data.get("warehouse_id")
    db = get_db()
    try:
        resp = requests.post(
            f"{PARTNER_API}/receive",
            json={"item_id": item_id, "warehouse": target_warehouse},
        )
        if resp.status_code == 200:
            db.execute(f"DELETE FROM items WHERE id = '{item_id}'")
            db.commit()
            print(f"Item {item_id} transferred to {target_warehouse}")
        return jsonify(resp.json())
    except:
        return jsonify({"error": "transfer failed"}), 500


@app.route("/report", methods=["GET"])
def generate_report():
    db = get_db()
    start = request.args.get("start_date")
    end = request.args.get("end_date")
    query = (
        f"SELECT category, SUM(quantity) FROM items "
        f"WHERE created_at BETWEEN '{start}' AND '{end}' "
        f"GROUP BY category"
    )
    rows = db.execute(query).fetchall()
    return jsonify({"report": rows})
