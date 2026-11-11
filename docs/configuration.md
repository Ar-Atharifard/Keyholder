# Application configuration

The API reads `KEYHOLDER_` environment variables through `keyholder.config.Settings`.
Use `.env.example` as the complete starting point. Keep runtime environment files
outside Git. Preserve `KEYHOLDER_PUBLIC_BASE_URL`, the database, encryption key and
customer token hashes during upgrades to preserve existing subscription URLs.

Set `KEYHOLDER_ADMIN_KEY` to a strong random secret. Administrative endpoints use
Bearer authentication. Keep them on a trusted private interface. Panel credentials
belong to the API process. Clients send account requests to the authenticated API.

SQLite is the supported application database. Apply `alembic upgrade head` before
starting an upgraded application. Back up the database and encryption key together.

Receipt storage is an optional reusable billing feature; see [billing](billing.md).
The subscription forwarding integration is documented under
[the subscription integration](../integrations/cloudflare-subscription/README.md). Supply account bindings and deployment
settings externally.

The application does not install the `keyholder` command or a Telegram bot. Use the
separate public `keyholder-admin` package and a compatible authorized dispatcher.
Host services, SSH policy, backups and production deployment are operator concerns,
not application environment setup.
