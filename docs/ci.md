# CI and builds

One workflow runs on pushes to `master`, pull requests into `master`, and manual
runs from the Actions tab. New runs cancel older runs for the same branch or PR.

| Job | Responsibility |
| --- | --- |
| Quality | Ruff lint/format, strict mypy and workflow validation |
| Tests | Application/contract tests, fresh SQLite migration and schema consistency |
| Worker | Node unit tests and a real workerd test against a synthetic upstream |
| Secret scan | Gitleaks against the complete checked-out Git history |
| Build | After all four checks pass: packages, source, OpenAPI and Docker image; isolated wheel and container checks |

The first four jobs run in parallel. The build runs once, on Linux amd64 with
Python 3.12, matching the application image. All jobs have timeouts and read-only
repository permissions. Actions are pinned by commit; downloaded validation tools
are pinned by version and checksum. No production secrets are required.

Download `keyholder-<commit>` from a successful run's **Artifacts** section within
seven days. It contains the wheel, source distribution, reviewed source archive,
OpenAPI schema, compressed Docker image, `COMMIT` and `SHA256SUMS`. After extracting:

```sh
sha256sum -c SHA256SUMS
docker load -i keyholder-image.tar.gz
```

These are CI build artifacts, not published releases. The workflow does not push
images, create GitHub releases, deploy services or contact operational servers.
The previous manual publishing workflow has been removed.

For branch protection on `master`, require **Quality**, **Tests**, **Worker**,
**Secret scan** and **Build**. Require all five: a skipped dependent build alone
must not stand in for successful validation. Configure this in GitHub repository
settings; committing the workflow does not enable branch protection.

The separately checked-out admin client is not part of this repository yet. Its
pipeline stays independent until the package is moved into this public repository.
