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

Administrative orchestration stays in `admin_operations.py` and the authenticated
`api/operations.py` boundary. Panel credentials and database mutations belong here;
external clients provide grammar, confirmation and display. Public software must
not import deployment/host implementations. Contract snapshots and migrations are
retained; module size alone is not a reason to create additional abstractions.
