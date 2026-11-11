# CI and builds

One workflow runs on pushes to `master`, pull requests into `master`, and manual
runs. New runs cancel older runs for the same workflow/ref. It has three jobs:

| Job | Contents |
| --- | --- |
| Verify | Ruff lint/format, strict mypy, workflow validation, full-history secret scan, Python/contract tests and fresh SQLite migration/schema checks |
| Worker | Node tests and a real workerd test with a synthetic upstream |
| Build | After both pass: packages, source, OpenAPI, isolated wheel smoke test, Docker build and offline container migration/import checks |

Verify and Worker run in parallel. Python checks share one environment. Build uses a clean environment with locked
dependencies and validates the installed wheel and container separately.

All jobs have timeouts and read-only repository permissions. Actions use commit
pins; downloaded validation tools use version/checksum pins. Lockfile installs are
frozen. No production credentials or server connections are involved.

PRs build and smoke-test the software, but do not save the large image archive.
Default-branch builds also export the image and upload `keyholder-<commit>` under
the run's **Artifacts** section for seven days. A manual default-branch run can
rebuild expired artifacts; it is a new build, not proof of byte-identical output.

The download contains the wheel, sdist, reviewed source archive, OpenAPI schema,
compressed Docker image, `COMMIT`, `IMAGE`, `IMAGE_ID` and `SHA256SUMS`. After extracting:

```sh
sha256sum -c SHA256SUMS
docker load -i keyholder-image.tar.gz
```

These are CI artifacts, not published releases. The workflow does not push images,
create GitHub releases or deploy. Image tags include the full Git commit SHA.
Verify the loaded image ID against `IMAGE_ID` and record it for deployment/rollback;
a tag alone is not an immutable identity.

For branch protection, require **Verify**, **Worker** and **Build**. Do not require
only Build: a skipped dependent job must not substitute for successful checks.
Configure required checks in the repository settings.

`keyholder-admin` has its own package checks and release lifecycle.
