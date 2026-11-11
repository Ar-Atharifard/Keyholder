# Development

`uv sync --frozen --extra dev` installs the complete application and development
tools. Run `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .`
and `uv run mypy src tests scripts`. Export OpenAPI with
`uv run python scripts/export_openapi.py --output /tmp/openapi.json`.

The frozen contracts under `tests/contracts` protect subscription output and
existing administrative APIs. New operations must preserve URLs, token hashes,
quota behavior and explicit confirmation. `tests/test_admin_operations.py` exercises
the authenticated transport used by external administration clients.

`uv build` builds the application wheel and source distribution. Source exports
from `scripts/export_source.py` reject runtime secrets and operational payloads.
The generic forwarding Worker is tested separately with Node and workerd in CI.

See [CI and builds](ci.md) for the job responsibilities, triggers and downloadable
build artifacts.

Administrative orchestration stays in `admin_operations.py` and the authenticated
`api/operations.py` boundary. Panel credentials and database mutations belong here;
external clients provide grammar, confirmation and display. Public software must
not import deployment/host implementations. Contract snapshots and migrations are
retained; module size alone is not a reason to create additional abstractions.

## Repository ownership

Keep reusable server logic here. `keyholder-admin` owns command grammar, SSH
transport, Telegram interaction, confirmations and presentation. Private
`keyholder-infra` owns host privileges and deployment. Neither public package imports
private infrastructure; the client does not import server models or source.

For a coordinated feature, change the server contract first or preserve compatibility
with older clients, add tests on each side, and record the compatible versions.
Use sibling checkouts when working across repositories; no submodule or matching
version numbers are required. Deployment selects exact tested artifacts separately.

| Path | Owns |
| --- | --- |
| `src/keyholder/api/`, `admin_operations.py` | Authenticated routes and account orchestration |
| `src/keyholder/backends/` | Provider integration |
| `src/keyholder/rendering/` | Subscription parsing and output |
| `src/keyholder/models.py`, `billing*.py`, `storage.py`, `object_storage.py` | Identity, financial history and optional object storage |
| `migrations/` | Database schema history |
| `integrations/cloudflare-subscription/` | Generic Worker and its tests |
| `scripts/` | Schema/source export and build helpers |
| `tests/` | Application and frozen compatibility contracts |

## Upstream licensing

Keyholder's [MIT license](../LICENSE) covers this project's code. Integration does
not relicense [Marzban](https://github.com/Gozargah/Marzban/blob/master/LICENSE) or
[Marzban Node](https://github.com/Gozargah/Marzban-node/blob/master/LICENSE), which
use AGPLv3. Keep upstream notices and satisfy the obligations of the exact versions
you modify or redistribute, including applicable corresponding-source requirements.
Do not copy upstream code assuming that API compatibility grants permission to
relicense it. Review licensing before distributing a combined or modified product.

The private operational repository is not required to contribute to this project.
Removing files from current source does not remove them from old public Git history;
review historical exposure separately rather than publishing production material.
