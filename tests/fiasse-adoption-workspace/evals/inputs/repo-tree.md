# Repository Structure — acme-billing-service

This document describes the structure of the `acme-billing-service` repository,
a Python/Flask billing microservice handling payment processing and invoice
generation for a B2B SaaS product.

```
acme-billing-service/
├── README.md
├── CONTRIBUTING.md               # provided separately
├── CODEOWNERS                     # @billing-team for src/, @infra for deploy/
├── .github/
│   └── workflows/
│       └── ci.yml                 # runs pytest, mypy, ruff
├── src/
│   ├── __init__.py
│   ├── app.py                     # Flask app factory
│   ├── handlers/
│   │   ├── invoices.py            # POST /invoices, GET /invoices/:id
│   │   ├── payments.py            # POST /payments/charge, POST /payments/refund
│   │   └── webhooks.py            # POST /webhooks/stripe (incoming Stripe events)
│   ├── models/
│   │   ├── invoice.py
│   │   └── payment.py
│   ├── services/
│   │   ├── billing.py             # orchestrates invoice + charge
│   │   └── stripe_client.py       # wraps Stripe SDK calls
│   └── utils/
│       ├── auth.py                # JWT verification middleware
│       └── logging.py             # print()-based logging helpers
├── tests/
│   ├── test_invoices.py           # 14 tests, mostly happy-path
│   ├── test_payments.py           # 8 tests
│   └── conftest.py                # shared fixtures
├── deploy/
│   ├── Dockerfile
│   └── k8s/
│       ├── deployment.yaml
│       └── service.yaml
├── requirements.txt               # Flask==3.0.0, stripe==7.9.0, PyJWT==2.8.0
└── pyproject.toml
```

## Notable characteristics

- **Team size**: ~6 engineers (2 senior, 4 mid-level). No dedicated security team.
- **Review practice**: PRs require 1 approval; no PR template exists.
- **Test coverage**: Tests exist but are concentrated on happy paths. No security-focused test cases.
- **Logging**: Uses `print()` via a thin wrapper in `utils/logging.py`. No structured logging.
- **No `.securable/` directory** — no securable contract exists.
- **No securability tooling installed** — no agent skills, no securability reports in CI.
- **No SSEM or FIASSE references** anywhere in the repository.
- **CI runs**: pytest, mypy, ruff. No security scanning.
