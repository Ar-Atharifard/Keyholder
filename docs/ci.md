# CI and builds

One workflow runs on pushes to `master`, pull requests into `master`, and manual
runs. New runs cancel older runs for the same workflow/ref. It has three jobs:

| Job | Contents |
| --- | --- |
| Verify | Ruff lint/format, strict mypy, workflow validation, full-history secret scan, Python/contract tests and fresh SQLite migration/schema checks |
| Worker | Node tests and a real workerd test with a synthetic upstream |
| Build | After both pass: packages, source, OpenAPI, isolated wheel smoke test, Docker build and offline container migration/import checks |

Verify and Worker run in parallel. Python checks share one environment rather than
reinstalling dependencies in separate quality/test jobs. Build has a clean environment;
wheel dependencies come from the lockfile. Wheel and container smoke tests cover
installation boundaries that source tests cannot. No deployment matrix, custom
Actions framework or production runner is needed for the supported amd64 image.

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
create GitHub releases or deploy. The image tag includes the full Git SHA instead of a shared `ci`/`latest` tag.
Verify the loaded image ID against `IMAGE_ID` and record it for deployment/rollback;
a tag alone is not an immutable identity.
The old publishing workflow was removed.

For branch protection, require **Verify**, **Worker** and **Build**. Do not require
only Build: a skipped dependent job must not substitute for successful checks.
Replace the old Quality/Tests/Secret scan requirements when this workflow lands;
repository settings are not changed by committing YAML.

`keyholder-admin` has its own package checks and release lifecycle. Private infra
validates its own playbooks and pinned cross-repository integration separately.
