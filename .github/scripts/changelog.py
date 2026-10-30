#!/usr/bin/env python3
"""Turn conventional commits into changelog entries.

The Publish workflow uses this to build GitHub release notes and to keep
CHANGELOG.md up to date without hand-editing.
"""

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

# Commit type -> changelog section. Types that are not listed here (tests,
# chores, CI, build, style) are left out of the changelog.
SECTION_TITLES = {
    "feat": "Added",
    "fix": "Fixed",
    "perf": "Changed",
    "refactor": "Changed",
    "revert": "Fixed",
    "docs": "Documentation",
}
SECTION_ORDER = ["Added", "Changed", "Fixed", "Documentation"]
COMMIT_PATTERN = re.compile(
    r"^(?P<type>[a-zA-Z]+)"
    r"(?:\((?P<scope>[^)]*)\))?"
    r"(?P<breaking>!)?"
    r":\s*(?P<subject>.+)$"
)
RELEASE_HEADING = re.compile(r"^## \[(?!Unreleased\]).*$", re.MULTILINE)
EMPTY_ENTRY = "- No user-facing changes in this release."


def git(*args):
    """Run git and return stripped stdout."""
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def previous_tag(current_tag):
    """Return the nearest release tag that is not the one being released."""
    try:
        return git(
            "describe",
            "--tags",
            "--abbrev=0",
            "--match",
            "v[0-9]*",
            "--exclude",
            current_tag,
            "HEAD",
        )
    except subprocess.CalledProcessError:
        return None


def commit_subjects(previous):
    """Return commit subjects for the current release range."""
    revision = f"{previous}..HEAD" if previous else "HEAD"
    output = git("log", "--no-merges", "--format=%s", revision)
    return [line.strip() for line in output.splitlines() if line.strip()]


def collect_entries(previous):
    """Group conventional commit subjects into changelog sections."""
    sections = {}
    for subject in commit_subjects(previous):
        match = COMMIT_PATTERN.match(subject)
        if not match:
            continue
        section = SECTION_TITLES.get(match.group("type").lower())
        if not section:
            continue

        text = match.group("subject").strip()
        text = text[0].upper() + text[1:]
        if match.group("scope"):
            text = f"**{match.group('scope')}:** {text}"
        if match.group("breaking"):
            text = f"**Breaking:** {text}"
        sections.setdefault(section, []).append(text)
    return sections


def render_body(sections):
    """Render changelog sections as a markdown body."""
    if not sections:
        return EMPTY_ENTRY

    parts = []
    for section in SECTION_ORDER:
        entries = sections.get(section)
        if not entries:
            continue
        parts.append(f"### {section}\n")
        parts.extend(f"- {entry}" for entry in entries)
        parts.append("")
    return "\n".join(parts).strip()


def render_entry(version, date, sections):
    """Render a full changelog section for one version."""
    return f"## [{version}] - {date}\n\n{render_body(sections)}\n"


def insert_entry(changelog, version, entry):
    """Insert a release section above the newest released version."""
    if re.search(rf"^## \[{re.escape(version)}\]", changelog, re.MULTILINE):
        return changelog

    match = RELEASE_HEADING.search(changelog)
    if match:
        head = changelog[: match.start()]
        tail = changelog[match.start() :]
        return f"{head}{entry}\n{tail}"

    return f"{changelog.rstrip()}\n\n{entry}" if changelog.strip() else entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="Version being released")
    parser.add_argument("--tag", help="Release tag; defaults to v<version>")
    parser.add_argument(
        "--date",
        default=datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
        help="Release date in YYYY-MM-DD form; defaults to today (UTC)",
    )
    parser.add_argument(
        "--notes-file",
        type=Path,
        help="Write GitHub release notes (section body only) to this path",
    )
    parser.add_argument(
        "--write",
        type=Path,
        metavar="CHANGELOG",
        help="Insert the release section into this changelog file",
    )
    args = parser.parse_args()

    tag = args.tag or f"v{args.version}"
    sections = collect_entries(previous_tag(tag))
    entry = render_entry(args.version, args.date, sections)

    if args.notes_file:
        args.notes_file.write_text(render_body(sections) + "\n", encoding="utf-8")
        print(f"Wrote release notes to {args.notes_file}")

    if args.write:
        changelog = args.write.read_text(encoding="utf-8")
        updated = insert_entry(changelog, args.version, entry)
        if updated == changelog:
            print(f"{args.write} already has an entry for {args.version}")
        else:
            args.write.write_text(updated, encoding="utf-8")
            print(f"Added {args.version} to {args.write}")

    if not args.notes_file and not args.write:
        sys.stdout.write(entry)
    return 0


if __name__ == "__main__":
    sys.exit(main())
