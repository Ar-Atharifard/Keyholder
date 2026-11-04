import subprocess
from pathlib import Path

import pytest

from scripts.export_source import source_files


def test_source_export_excludes_private_notes_but_includes_untracked_source(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text(".private/\n.env\n")
    (tmp_path / "README.md").write_text("Public")
    p = tmp_path / ".private"
    p.mkdir()
    (p / "personal.md").write_text("Private")
    (tmp_path / ".env").write_text("private")
    assert source_files(tmp_path) == [Path(".gitignore"), Path("README.md")]


def test_export_refuses_tracked_credentials(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    (tmp_path / ".env").write_text("private")
    subprocess.run(["git", "-C", str(tmp_path), "add", ".env"], check=True)
    with pytest.raises(ValueError, match="publication refused"):
        source_files(tmp_path)


def test_public_export_refuses_operational_payloads(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    (tmp_path / "deploy").mkdir()
    (tmp_path / "deploy/production.json").write_text("{}")
    with pytest.raises(ValueError, match="Operational source"):
        source_files(tmp_path)
