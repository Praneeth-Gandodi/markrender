"""Tests for the changelog helper used by the publish workflow."""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / ".github" / "scripts" / "changelog.py"

pytestmark = pytest.mark.skipif(
    not SCRIPT.exists(), reason="release helper is not part of this checkout"
)


def git(repo, *args):
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def commit(repo, message, filename):
    (repo / filename).write_text(filename, encoding="utf-8")
    git(repo, "add", filename)
    git(repo, "commit", "-m", message)


def run_changelog(repo, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=repo,
        capture_output=True,
        text=True,
    )


def make_repo(path):
    git(path, "init", "-q")
    git(path, "config", "user.email", "test@example.com")
    git(path, "config", "user.name", "Test")
    commit(path, "feat: initial release", "initial.txt")
    git(path, "tag", "-a", "v1.1.0", "-m", "v1.1.0")
    commit(path, "feat(renderer): add table alignment", "table.txt")
    commit(path, "fix: stop crushing short columns", "fit.txt")
    commit(path, "docs: mention the changelog", "readme.txt")
    commit(path, "chore: tidy up", "chore.txt")
    commit(path, "test: cover narrow tables", "test.txt")
    return path


def test_entry_groups_conventional_commits(tmp_path):
    repo = make_repo(tmp_path)

    result = run_changelog(
        repo, "--version", "1.1.1", "--tag", "v1.1.1", "--date", "2026-10-30"
    )

    assert result.returncode == 0
    assert "## [1.1.1] - 2026-10-30" in result.stdout
    assert "### Added" in result.stdout
    assert "**renderer:** Add table alignment" in result.stdout
    assert "### Fixed" in result.stdout
    assert "Stop crushing short columns" in result.stdout
    assert "### Documentation" in result.stdout
    assert "Tidy up" not in result.stdout
    assert "Cover narrow tables" not in result.stdout


def test_notes_file_omits_the_version_heading(tmp_path):
    repo = make_repo(tmp_path)
    notes = repo / "notes.md"

    result = run_changelog(
        repo,
        "--version",
        "1.1.1",
        "--tag",
        "v1.1.1",
        "--date",
        "2026-10-30",
        "--notes-file",
        str(notes),
    )

    assert result.returncode == 0
    body = notes.read_text(encoding="utf-8")
    assert "## [1.1.1]" not in body
    assert "### Added" in body


def test_write_inserts_above_the_newest_release(tmp_path):
    repo = make_repo(tmp_path)
    changelog = repo / "CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n"
        "## [1.1.0] - 2026-10-01\n\n"
        "### Added\n\n- Initial release.\n",
        encoding="utf-8",
    )

    result = run_changelog(
        repo,
        "--version",
        "1.1.1",
        "--tag",
        "v1.1.1",
        "--date",
        "2026-10-30",
        "--write",
        str(changelog),
    )

    assert result.returncode == 0
    text = changelog.read_text(encoding="utf-8")
    assert text.index("## [1.1.1]") < text.index("## [1.1.0]")
    assert text.startswith("# Changelog")


def test_write_is_idempotent(tmp_path):
    repo = make_repo(tmp_path)
    changelog = repo / "CHANGELOG.md"
    changelog.write_text("# Changelog\n", encoding="utf-8")

    args = ("--version", "1.1.1", "--tag", "v1.1.1", "--write", str(changelog))
    run_changelog(repo, *args)
    first = changelog.read_text(encoding="utf-8")
    run_changelog(repo, *args)

    assert changelog.read_text(encoding="utf-8") == first
    assert first.count("## [1.1.1]") == 1


def test_release_with_only_maintenance_commits(tmp_path):
    repo = tmp_path
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    commit(repo, "feat: initial release", "initial.txt")
    git(repo, "tag", "-a", "v1.1.0", "-m", "v1.1.0")
    commit(repo, "chore: tidy up", "chore.txt")

    result = run_changelog(repo, "--version", "1.1.1", "--tag", "v1.1.1")

    assert result.returncode == 0
    assert "No user-facing changes" in result.stdout
