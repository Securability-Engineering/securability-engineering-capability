# Repository Structure — partner-portal

A Python/Django B2B partner portal for managing integrations and API keys.

```
partner-portal/
├── README.md
├── CONTRIBUTING.md               # see attached
├── CODEOWNERS                     # @platform-team for all files
├── .github/
│   ├── pull_request_template.md   # exists but contains only "## Description\n## Testing"
│   └── workflows/
│       └── ci.yml                 # runs pytest, black, flake8
├── .securable/
│   └── requirements.yaml          # see summary below
├── docs/
│   └── adr/
│       └── 001-api-key-rotation.md  # mentions "security" but no SSEM terms
├── src/
│   ├── manage.py
│   ├── portal/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── views/
│   │   │   ├── partners.py        # CRUD for partner accounts
│   │   │   ├── api_keys.py        # create/rotate/revoke API keys
│   │   │   └── webhooks.py        # receives partner webhook registrations
│   │   ├── models/
│   │   │   ├── partner.py
│   │   │   └── api_key.py
│   │   ├── serializers/
│   │   │   ├── partner.py
│   │   │   └── api_key.py
│   │   └── middleware/
│   │       └── audit.py           # logs request method + path to stdout
├── tests/
│   ├── test_partners.py           # 22 tests
│   ├── test_api_keys.py           # 18 tests
│   ├── test_webhooks.py           # 6 tests
│   └── conftest.py
├── requirements.txt
└── pyproject.toml
```

## .securable/requirements.yaml summary

- `asvs_level`: 1
- 6 features defined (F-01 through F-06)
- 4 of 6 features have acceptance criteria (F-03 and F-05 lack them)
- All requirements have `status: planned` — none are `implemented` or `verified`
- No `threat_scenarios` fields populated
- One requirement references ASVS V6.3 (Authentication — valid 5.0 reference)
- One requirement references ASVS V8.1 (Authorization — valid 5.0 reference)

## Team context

- 8 engineers total. Seniority distribution unknown from code.
- PR template exists but has no securability content.
- CODEOWNERS is broad (one team owns everything).
- ADR exists but uses no SSEM vocabulary.
- CI runs tests and formatters but no security scanning.
- audit.py middleware exists but uses `print()` — no structured logging.
- No securability tooling installed (no agent skills, no securability reports).
