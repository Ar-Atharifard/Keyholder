# Marzban-Keyholder

Reusable subscription delivery with FastAPI, SQLite, provider adapters, permanent
customer subscription URLs, account administration and optional billing/receipts.

## Development

Requires Python 3.12+ and uv.

```sh
uv sync --frozen --extra dev
cp .env.example .env
# Set strong administrator and encryption keys and your upstream settings.
uv run alembic upgrade head
uv run uvicorn keyholder.main:create_app --factory --host 127.0.0.1 --port 18000
uv run pytest -q
uv build
```

The Dockerfile builds the application image. `docker-compose.yml` is a local
application example. Protect the authenticated administrator interface with private
network access. Keep runtime credentials, databases and archives outside Git.

The independently installable public `keyholder-admin` package provides CLI and
Telegram clients over SSH/private access. The API owns credentials, provisioning,
quota and inbound-selection behavior; clients own interaction and confirmations.

See [API contracts](docs/api.md), [configuration](docs/configuration.md) and
[billing](docs/billing.md). The generic subscription forwarding Worker and its tests
are in `integrations/cloudflare-subscription`; deployment settings are external.

Release wheels and images contain reusable software. Deployment policy, production
inventories, monitoring, recovery and privileged host implementations are maintained
separately. Moving files does not remove material from previously published history.
