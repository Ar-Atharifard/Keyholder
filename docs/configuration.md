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

## Updating an existing installation

Keep production configuration separate from the repository example. To select a
local production Compose file with ordinary commands, put this in the checkout's
ignored `.env` (preserve any existing settings):

```dotenv
COMPOSE_FILE=compose.prod.yml
```

Keep that production file out of Git. Preserve the existing Compose project name,
data volume, public URL, credentials, encryption key and networking. Do not replace
working settings with `.env.example` during an upgrade.

After a backup and compatibility review, a code-only update built on the host is:

```sh
git pull --ff-only
docker compose config --quiet
docker compose up -d --build --no-deps api
```

Run from the checkout. Use `sudo` where Docker access requires it. For GitHub-built
images, load the verified archive and select that image in production configuration;
start with `--no-build --pull never` instead. See [CI artifacts](ci.md).

For schema changes, pause administrative writers, back up SQLite and its encryption
key, then build and migrate before starting the API:

```sh
docker compose build api
docker compose stop api
docker compose run --rm --no-deps --pull never --entrypoint /app/.venv/bin/alembic api upgrade head
docker compose up -d --no-build --no-deps api
```

Stop on failure. Verify `/health`, administration and an existing subscription before
resuming writers. Keep the previous image and backup: reverting an image does not
undo a database migration. Do not run `docker compose down --volumes` during updates.
