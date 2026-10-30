# Changelog

All notable changes to MarkRender are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/). Releases are
cut from conventional commits, and new entries are added by the publish
workflow when a release goes out.

## [1.1.1] - 2026-10-30

### Fixed

- Dim mode now renders the whole response in one uniform muted gray, including paragraphs, lists, tables, quotes, and code blocks.

### Documentation

- Clarified the CLI and Python usage examples.

## [1.1.0] - 2026-10-30

### Added

- Dim mode for streaming responses, enabled per render call.
- Theme previews in the README and a `preview-themes` command.
- `--width`, `--force-color`, and `--version` CLI flags.
- TOML config file support with warnings for unknown keys.
- Dynamic code block line-number widths.
- Better handling of split stream chunks and buffer boundaries.

### Changed

- Rewrote the README around CLI and Python usage instead of feature marketing.
- Dim mode moved from the constructor to a `render()` argument.
- Themes are now deep-copied so rendering cannot mutate shared theme state.
- Improved the parser regexes for bold + italic, inline code, links, and blockquotes.

### Fixed

- Blockquotes falling through to other block handlers.
- Dictionary themes loaded from TOML files failing to render.
- Table overflow when content is wider than the terminal.
- Encoding fallback when the output stream is not UTF-8.
- Config files now warn about unknown keys instead of failing silently.

Releases before 1.1.0 were published before this changelog existed.
