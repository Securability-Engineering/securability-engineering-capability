# Contributing to partner-portal

## Development Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python src/manage.py migrate
python src/manage.py runserver
```

## Code Review Guidelines

- All PRs require at least one approval.
- Run `black .` and `flake8 .` before opening a PR.
- Write tests for new functionality.
- If your change touches the API, update the OpenAPI spec in `docs/`.

## Architecture Notes

- We follow a standard Django project layout with DRF serializers.
- Database migrations are auto-generated — review them before committing.
- The `audit.py` middleware captures request metadata for debugging.

## Security

If you discover a security vulnerability, please email security@example.com
rather than opening a public issue.
