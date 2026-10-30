#!/usr/bin/env python3
"""Work out the next release version from git tags and conventional commits.

The package version itself comes from setuptools_scm, so this script only
decides which tag to create. It is used by the Publish workflow.

Exit codes:
    0 - version written to stdout
    3 - nothing to release (only with --bump auto)
    1 - invalid tag/version input
"""

import argparse
import os
import re
import subprocess
import sys

TAG_PATTERN = re.compile(r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")
BREAKING_SUBJECT = re.compile(r"^[a-zA-Z][\w-]*(\([^)]*\))?!:")
FEATURE_SUBJECT = re.compile(r"^feat(\([^)]*\))?!?:", re.IGNORECASE)
NON_RELEASE_SUBJECT = re.compile(
    r"^(docs|test|tests|ci|build|chore|style)(\([^)]*\))?!?:", re.IGNORECASE
)
BREAKING_BODY = re.compile(r"^BREAKING[ -]CHANGE:", re.MULTILINE | re.IGNORECASE)


def git(*args):
    """Run git and return stripped stdout."""
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def parse_version(value):
    match = TAG_PATTERN.match(value.strip())
    if not match:
        raise ValueError(f"Invalid version: {value!r}")
    return tuple(int(match.group(key)) for key in ("major", "minor", "patch"))


def latest_version(default="1.0.7"):
    """Return (tag, (major, minor, patch)) for the newest semver tag."""
    tags = git("tag", "--list", "v*", "--sort=-v:refname").splitlines()
    for tag in tags:
        match = TAG_PATTERN.match(tag.strip())
        if match:
            return tag.strip(), parse_version(tag)
    return None, parse_version(default)


def commits_since(tag):
    """Return (subject, body) pairs for commits after the latest tag."""
    revision = f"{tag}..HEAD" if tag else "HEAD"
    output = git("log", revision, "--format=%s%x00%b%x1e")
    commits = []
    for record in output.split("\x1e"):
        subject, _, body = record.partition("\x00")
        subject = subject.strip()
        if not subject:
            continue
        commits.append((subject, body.strip()))
    return commits


def detect_bump(commits):
    """Pick the highest conventional-commit bump, or None if nothing counts.

    Docs, tests, CI, build, chore, and style commits do not change the
    package, so they never trigger a release on their own.
    """
    if not commits:
        return None

    bump = None
    for subject, body in commits:
        if NON_RELEASE_SUBJECT.match(subject):
            continue
        if BREAKING_SUBJECT.match(subject) or BREAKING_BODY.search(body):
            return "major"
        if FEATURE_SUBJECT.match(subject):
            bump = "minor"
        elif bump != "minor":
            bump = "patch"
    return bump


def bump_version(current, bump):
    major, minor, patch = current
    if bump == "major":
        return major + 1, 0, 0
    if bump == "minor":
        return major, minor + 1, 0
    return major, minor, patch + 1


def write_output(name, value):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bump",
        choices=("auto", "patch", "minor", "major"),
        default="auto",
        help="Version bump to apply; auto reads conventional commit messages",
    )
    parser.add_argument(
        "--initial-version",
        default="1.0.7",
        help="Version to start from when the repository has no tags",
    )
    args = parser.parse_args()

    tag, current = latest_version(args.initial_version)
    commits = commits_since(tag)
    detected = detect_bump(commits)
    bump = detected if args.bump == "auto" else args.bump

    if bump is None:
        print("No commits since the latest tag; nothing to release.", file=sys.stderr)
        return 3

    version = ".".join(str(part) for part in bump_version(current, bump))
    write_output("version", version)
    write_output("tag", f"v{version}")
    write_output("bump", bump)
    print(version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
