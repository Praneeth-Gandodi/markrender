"""Tests for the release-version helper used by the publish workflow."""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / ".github" / "scripts" / "next_version.py"

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


def next_version(repo, *args):
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
    commit(path, "chore: initial", "initial.txt")
    git(path, "tag", "-a", "v1.0.7", "-m", "v1.0.7")
    return path


def test_no_commits_means_nothing_to_release(tmp_path):
    repo = make_repo(tmp_path)

    result = next_version(repo, "--bump", "auto")

    assert result.returncode == 3
    assert result.stdout == ""


def test_fix_commit_bumps_patch(tmp_path):
    repo = make_repo(tmp_path)
    commit(repo, "fix: correct rendering", "fix.txt")

    result = next_version(repo, "--bump", "auto")

    assert result.returncode == 0
    assert result.stdout.strip() == "1.0.8"


def test_feature_commit_bumps_minor(tmp_path):
    repo = make_repo(tmp_path)
    commit(repo, "feat: add a renderer option", "feature.txt")

    result = next_version(repo, "--bump", "auto")

    assert result.returncode == 0
    assert result.stdout.strip() == "1.1.0"


def test_docs_only_commit_does_not_release(tmp_path):
    repo = make_repo(tmp_path)
    commit(repo, "docs: explain the width flag", "readme.txt")

    result = next_version(repo, "--bump", "auto")

    assert result.returncode == 3


def test_chore_only_commit_does_not_release(tmp_path):
    repo = make_repo(tmp_path)
    commit(repo, "chore: remove a local harness", "chore.txt")

    result = next_version(repo, "--bump", "auto")

    assert result.returncode == 3


def test_maintenance_commits_do_not_raise_the_bump(tmp_path):
    repo = make_repo(tmp_path)
    commit(repo, "feat: add a renderer option", "feature.txt")
    commit(repo, "chore: tidy up", "chore.txt")

    result = next_version(repo, "--bump", "auto")

    assert result.returncode == 0
    assert result.stdout.strip() == "1.1.0"


def test_breaking_commit_bumps_major(tmp_path):
    repo = make_repo(tmp_path)
    commit(repo, "feat!: change the public API", "breaking.txt")

    result = next_version(repo, "--bump", "auto")

    assert result.returncode == 0
    assert result.stdout.strip() == "2.0.0"


def test_breaking_change_footer_bumps_major(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "body.txt").write_text("body", encoding="utf-8")
    git(repo, "add", "body.txt")
    git(repo, "commit", "-m", "refactor: rearrange internals", "-m", "BREAKING CHANGE: moved modules")

    result = next_version(repo, "--bump", "auto")

    assert result.returncode == 0
    assert result.stdout.strip() == "2.0.0"


def test_explicit_bump_works_without_new_commits(tmp_path):
    repo = make_repo(tmp_path)

    result = next_version(repo, "--bump", "minor")

    assert result.returncode == 0
    assert result.stdout.strip() == "1.1.0"


def test_initial_version_is_used_without_tags(tmp_path):
    repo = make_repo(tmp_path)
    git(repo, "tag", "-d", "v1.0.7")
    commit(repo, "fix: first release", "first.txt")

    result = next_version(repo, "--bump", "auto", "--initial-version", "2.0.0")

    assert result.returncode == 0
    assert result.stdout.strip() == "2.0.1"
