"""
integrations.py — Third-party service clients for the notification pipeline.

Part of notifications/, an internal microservice. Sends messages
via SMS, email, and push providers. Called from the task queue worker.
"""
import json
import logging
import requests

logger = logging.getLogger(__name__)

SMS_API = "https://sms-provider.example.com/v2"
EMAIL_API = "https://email-relay.internal.corp/send"
PUSH_API = "https://push-gateway.example.com/api/notify"
WEBHOOK_RELAY = "https://hooks.example.com/relay"

SMS_KEY = "sk_sms_live_xxxxxxx"
EMAIL_KEY = "sk_email_live_xxxxxxx"


def send_sms(phone: str, body: str) -> dict:
    """Send an SMS via the provider API."""
    resp = requests.post(
        f"{SMS_API}/messages",
        json={"to": phone, "body": body},
        headers={"Authorization": f"Bearer {SMS_KEY}"},
    )
    resp.raise_for_status()
    logger.info("SMS sent to %s", phone)
    return resp.json()


def send_email(to: str, subject: str, html_body: str) -> dict:
    """Send an email via the internal relay."""
    resp = requests.post(
        EMAIL_API,
        json={"to": to, "subject": subject, "html": html_body},
        headers={"X-Api-Key": EMAIL_KEY},
    )
    resp.raise_for_status()
    logger.info("Email sent to %s", to)
    return resp.json()


def send_push(device_token: str, title: str, message: str) -> dict:
    """Send a push notification."""
    resp = requests.post(
        f"{PUSH_API}",
        json={"token": device_token, "title": title, "body": message},
    )
    resp.raise_for_status()
    logger.info("Push sent to device %s", device_token[:8])
    return resp.json()


def relay_webhook(target_url: str, payload: dict) -> dict:
    """Forward an event payload to an external webhook."""
    resp = requests.post(
        WEBHOOK_RELAY,
        json={"url": target_url, "payload": payload},
    )
    resp.raise_for_status()
    logger.info("Webhook relayed to %s", target_url)
    return resp.json()
