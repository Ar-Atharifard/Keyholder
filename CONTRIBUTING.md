# Contributing

Read [the development guide](docs/development.md) before changing code or contracts.
Use synthetic test data. Never submit customer links, real credentials, databases,
private deployment configuration or personal troubleshooting notes.

Keep changes focused, with meaningful regression tests and updated documentation.
Run pytest, Ruff, mypy and `git diff --check`. Explain behavior, validation and
compatibility in the pull request. Provider adapters need mocked contract tests;
new transports additionally need installed-core and real-network validation.

Contributions are distributed under the project's MIT license. Preserve attribution
and compatible licensing for any reused code; see
[upstream licensing](docs/development.md#upstream-licensing).

AI-assisted contributions are welcome. Describe substantial AI assistance in the
pull request, review the result, and be able to explain and maintain it. The same
testing, security and licensing requirements apply.

File server/API issues here and CLI/Telegram interaction issues in `keyholder-admin`.
Include compatible component versions and reproduction steps with synthetic data.
For coordinated backend/client changes, link the pull requests and document the
compatible versions.
