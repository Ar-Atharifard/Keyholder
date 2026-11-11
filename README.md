# Keyholder

Keyholder is a lightweight backend for managing proxy subscriptions. It integrates
with Marzban to manage accounts and deliver connection profiles through stable
customer URLs. Optional features record purchases, payments, referrals and private
receipt images without automatically changing a customer's proxy plan.

## Related projects

| Repository | Responsibility |
| --- | --- |
| **keyholder** (this repository) | API, SQLite database and migrations, account operations, subscription rendering and billing/storage rules |
| [keyholder-admin](https://github.com/Ar-Atharifard/keyholder-admin) | Independently installed CLI and Telegram management client |
| **keyholder-infra** (private) | Operator-specific deployment, networking, monitoring, host dispatcher and disaster recovery |

These are independent repositories, not submodules. The backend does not require
client source or access to the private repository. Clients communicate through the
administrative API; deployment tools install reviewed images and packages. Package
versions are independent, with compatibility defined by the API/protocol contract.

## Run locally

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). From a source checkout:

```sh
uv sync --frozen --extra dev
cp .env.example .env
```

Set strong `KEYHOLDER_ADMIN_KEY` and `KEYHOLDER_TOKEN_ENCRYPTION_KEY` values and your
upstream settings in `.env`, then:

```sh
uv run alembic upgrade head
uv run uvicorn keyholder.main:create_app --factory --host 127.0.0.1 --port 18000
```

The Dockerfile builds the API image; `docker-compose.yml` is an application example,
not a complete VPS deployment. Apply migrations explicitly and keep administration
on a trusted private interface. SQLite with one application worker is supported;
arbitrary database engines and panel APIs are not.

## Documentation

| Guide | Contents |
| --- | --- |
| [Configuration](docs/configuration.md) | Environment, credentials and persistent identity |
| [API](docs/api.md) | Authentication, account operations and subscription contracts |
| [Billing](docs/billing.md) | Ledger, receipts and storage rules; examples use the separate admin client |
| [Development](docs/development.md) | Code ownership, compatibility and local checks |
| [CI and builds](docs/ci.md) | Checks, downloadable packages/images and their limitations |
| [Subscription Worker](integrations/cloudflare-subscription/README.md) | Optional generic forwarding integration |

Existing subscription URLs must survive upgrades and remapping. Preserve the
public base URL, database and token encryption key. Credentials, customer data,
production inventories and personal runbooks do not belong in public Git.

## License and contributions

Licensed under [MIT](LICENSE). Marzban and other dependencies retain their own
licenses; see [upstream licensing](docs/development.md#upstream-licensing).
Read [Contributing](CONTRIBUTING.md) and [Security](SECURITY.md) before submitting changes.

Developed with substantial direct assistance from OpenAI Codex. Human maintainers
review changes and remain responsible for releases and operation.
