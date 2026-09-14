# Contributing to acme-billing-service

Thanks for contributing! Please follow these guidelines.

## Getting Started

1. Clone the repo and create a virtual environment:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt -r requirements-dev.txt
   ```

2. Run the test suite:
   ```bash
   pytest tests/
   ```

## Code Style

- We use **ruff** for linting and formatting. Run `ruff check .` and `ruff format .` before opening a PR.
- Type hints are required on public functions. We run **mypy** in CI.

## Pull Requests

- Branch from `main`, keep PRs focused on a single change.
- All PRs require at least one approving review from a team member.
- CI must pass before merge (pytest + mypy + ruff).
- Write tests for new features. Aim for >80% coverage on new code.

## Reporting Issues

Open a GitHub issue. For sensitive bugs, email security@acme-example.com.

## Code of Conduct

Be respectful and professional. See CODE_OF_CONDUCT.md for details.
