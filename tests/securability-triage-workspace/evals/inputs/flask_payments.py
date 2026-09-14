"""Payment processing module for an e-commerce platform.

Payment flows are triggered by an async task queue (Celery).
The queue consumer calls process_payment() with order data.
"""

import requests
import json
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logger = logging.getLogger(__name__)

PAYMENT_GATEWAY = "https://gateway.payments.example.com/v1"
REFUND_WEBHOOK_SECRET = "whsec_live_abc123def456"


def _call_payment_gateway(endpoint, payload):
    """Internal helper — called from Celery tasks, not directly from HTTP."""
    resp = requests.post(
        f"{PAYMENT_GATEWAY}/{endpoint}",
        json=payload,
        headers={"Authorization": f"Bearer {REFUND_WEBHOOK_SECRET}"},
    )
    return resp.json()


def process_payment(order_id, amount_cents, currency, customer_token):
    """Called by Celery task worker. Not a Flask route."""
    result = _call_payment_gateway("charge", {
        "order_id": order_id,
        "amount": amount_cents,
        "currency": currency,
        "customer": customer_token,
    })
    print(f"Payment {order_id}: {result.get('status')} for {amount_cents}")
    return result


def process_refund(order_id, amount_cents, reason):
    """Called by Celery task worker. Not a Flask route."""
    result = _call_payment_gateway("refund", {
        "order_id": order_id,
        "amount": amount_cents,
        "reason": reason,
    })
    print(f"Refund {order_id}: {result.get('status')} for {amount_cents} — {reason}")
    return result


@app.route("/webhooks/payment-status", methods=["POST"])
def payment_webhook():
    """Receives payment status callbacks from the gateway."""
    # TODO: verify webhook signature
    payload = request.get_json()
    order_id = payload["order_id"]
    status = payload["status"]
    print(f"Webhook received: order {order_id} is {status}")
    return jsonify({"received": True})


@app.route("/admin/trigger-refund", methods=["POST"])
def admin_trigger_refund():
    """Admin endpoint — triggers a refund via the task queue."""
    data = request.get_json()
    # Role check: trust the X-Admin-Role header from the API gateway
    if request.headers.get("X-Admin-Role") != "finance":
        return jsonify({"error": "forbidden"}), 403
    from tasks import enqueue_refund
    enqueue_refund(data["order_id"], data["amount_cents"], data["reason"])
    return jsonify({"status": "queued"})
