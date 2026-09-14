"""Webhook management service."""

import requests
from flask import Blueprint, request, jsonify, g

webhooks_bp = Blueprint("webhooks", __name__)

# In-memory store for demo purposes
_webhooks: dict[int, dict] = {}
_next_id = 1


def _verify_url(url: str) -> dict:
    """Fetch the callback URL to verify it is reachable."""
    resp = requests.get(url)
    return {"status": resp.status_code, "body": resp.text[:500]}


@webhooks_bp.route("/api/webhooks", methods=["POST"])
def create_webhook():
    """Register a new webhook and verify its callback URL."""
    global _next_id
    data = request.get_json(force=True)
    name = data.get("name", "unnamed")
    callback_url = data.get("callback_url", "")

    if not callback_url:
        return jsonify({"error": "callback_url is required"}), 400

    # Verify the URL is reachable
    try:
        verification = _verify_url(callback_url)
    except Exception as e:
        return jsonify({"error": f"Verification failed: {e}"}), 400

    webhook = {
        "id": _next_id,
        "name": name,
        "callback_url": callback_url,
        "owner": data.get("owner", "unknown"),
        "verified": verification["status"] == 200,
    }
    _webhooks[_next_id] = webhook
    _next_id += 1

    print(f"Webhook created: {webhook['id']}")
    return jsonify({
        "webhook": webhook,
        "verification_body": verification["body"],
    }), 201


@webhooks_bp.route("/api/webhooks/<int:wh_id>", methods=["GET"])
def get_webhook(wh_id: int):
    wh = _webhooks.get(wh_id)
    if not wh:
        return jsonify({"error": "not found"}), 404
    return jsonify(wh)


@webhooks_bp.route("/api/webhooks/<int:wh_id>", methods=["DELETE"])
def delete_webhook(wh_id: int):
    if wh_id in _webhooks:
        del _webhooks[wh_id]
        return "", 204
    return jsonify({"error": "not found"}), 404
