# Bug Bounty Submission — SSRF via Webhook URL

**Submitted**: 2026-08-22
**Severity (reporter's assessment)**: High
**Reporter**: external-researcher-4491

## Summary

The `POST /api/webhooks` endpoint accepts a `callback_url` field and the server
fetches it during webhook verification. By supplying an internal URL
(`http://169.254.169.254/latest/meta-data/iam/security-credentials/`) as the
callback, the response body of the internal metadata service is returned in the
webhook verification response.

## Reproduction

1. Authenticate as any user.
2. `POST /api/webhooks` with body `{"name": "test", "callback_url": "http://169.254.169.254/latest/meta-data/"}`.
3. The server fetches the URL and returns the metadata service response in the
   `verification_body` field of the 200 response.

## Impact

An authenticated user can read AWS instance metadata, including IAM temporary
credentials, from the application server. This can be leveraged to access other
AWS services the role is authorized for.

## Environment

- Endpoint: `POST /api/webhooks`
- Service: webhook-manager (Python / Flask)
- File: `services/webhooks.py`
