"""
Regression tests for parser, renderer, color, and configuration bugs.
"""

from io import StringIO

from markrender import MarkdownRenderer
from markrender.colors import strip_ansi


def render(markdown, **kwargs):
    output = StringIO()
    renderer = MarkdownRenderer(output=output, **kwargs)
    renderer.render(markdown)
    renderer.finalize()
    return strip_ansi(output.getvalue())


class TestIssueTwoRegression:
    """The section order from issue #2 must stay intact."""

    def test_sections_keep_their_order(self):
        markdown = """## Managing sudo Users
Users that are able to become root are managed by the
`/etc/sudoers.d/99-cyberinv-custom` file.  Use the
`visudo(8)` command if you have to.


## Managing PAM Config
TL;DR - Don't touch it!
pam-auth-update(8) will break the PAM config badly, because some of the
/etc/pam.d/* files are manually modified, so don't do it.

The good news is that pam-auth-update does backup the individual files.

## Adding Groups to Who Can Login
These must be added in two places:
 * The `AllowGroups` line in `/etc/ssh/sshd_config`
 * The `ldap_access_filter` in `/etc/sssd/sssd.conf`
"""
        result = render(markdown)

        sudo = result.index("Managing sudo Users")
        pam_heading = result.index("Managing PAM Config")
        pam_body = result.index("TL;DR")
        groups_heading = result.index("Adding Groups to Who Can Login")

        assert sudo < pam_heading < pam_body < groups_heading
        # The lone asterisk in the PAM path must survive.
        assert "/etc/pam.d/*" in result


class TestBlockquoteRegressions:
    def test_text_after_blockquote_is_not_swallowed(self):
        result = render("> quoted line\nthis line should appear\n")

        assert "quoted line" in result
        assert "this line should appear" in result
        assert result.index("quoted line") < result.index("this line should appear")

    def test_inline_formatting_inside_blockquote(self):
        result = render("> **bold** and *italic* and `code`\n\n")

        assert "**" not in result
        assert "bold" in result
        assert "italic" in result
        assert "`code`" in result

    def test_inline_formatting_inside_alert(self):
        result = render("> [!NOTE]\n> **bold** text\n\n")

        assert "NOTE" in result
        assert "**" not in result
        assert "bold" in result


class TestInlineFormattingRegressions:
    def test_asterisks_inside_inline_code_are_literal(self):
        result = render("`Code with *italic* markup`\n")

        assert "`Code with *italic* markup`" in result

    def test_emoji_inside_inline_code_is_literal(self):
        result = render("`:rocket:` is not an emoji here\n")

        assert "`:rocket:`" in result

    def test_nested_italic_inside_bold(self):
        result = render("**bold with *nested italic***\n")

        assert "bold with nested italic" in result
        assert "*" not in result

    def test_nested_bold_inside_italic(self):
        result = render("*italic with **nested bold***\n")

        assert "italic with nested bold" in result
        assert "*" not in result

    def test_bold_inside_link_text(self):
        result = render("[link with **bold text**](https://example.com)\n")

        assert "link with bold text" in result
        assert "**" not in result
        assert "https://example.com" in result

    def test_unpaired_asterisks_are_preserved(self):
        result = render("The /etc/pam.d/* files and 2 * 3 are not emphasis\n")

        assert "/etc/pam.d/*" in result
        assert "2 * 3" in result


class TestCodeBlockRegressions:
    def test_leading_blank_line_is_preserved(self):
        result = render("```\n\nfirst\n```\n", line_numbers=True)

        assert "   1  " in result
        assert "   2  first" in result

    def test_plus_list_and_checkbox(self):
        result = render("+ item\n+ [x] done\n")

        assert "item" in result
        assert "done" in result
        assert "[x]" not in result

    def test_partial_code_line_is_buffered_until_newline(self):
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        for chunk in ["```python\ndef hello", "():\n", "```\n"]:
            renderer.render(chunk)
        renderer.finalize()

        result = strip_ansi(output.getvalue())
        assert "def hello():" in result
        assert "def hello\n" not in result

    def test_language_with_symbols_in_fence(self):
        result = render("```c++\nint x = 1;\n```\n")

        assert "int x = 1;" in result

    def test_fence_with_extra_info_string(self):
        result = render('```python title="demo"\nprint("hi")\n```\n')

        assert 'print("hi")' in result

    def test_longer_fence_keeps_shorter_fence_as_content(self):
        result = render("````markdown\n```python\nx = 1\n```\n````\n")

        assert "```python" in result
        assert "x = 1" in result

    def test_crlf_chunks_are_normalized(self):
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        renderer.render("# Title\r\n")
        renderer.render("Text\r\n")
        renderer.finalize()

        result = strip_ansi(output.getvalue())
        assert "# Title\nText\n" in result
        assert "\r" not in result

    def test_code_background_covers_code(self):
        output = StringIO()
        renderer = MarkdownRenderer(
            output=output,
            force_color=True,
            line_numbers=False,
            code_background=True,
        )
        renderer.render("```\nx = 1\n```\n")
        renderer.finalize()

        result = output.getvalue()
        assert "\x1b[100m" in result
        assert "x = 1" in result

    def test_dim_mode_dims_code_content(self):
        output = StringIO()
        renderer = MarkdownRenderer(
            output=output,
            force_color=True,
            line_numbers=False,
        )
        renderer.render("```python\nx = 1\n```\n", dim_mode=True)
        renderer.finalize()

        result = output.getvalue()
        assert "\x1b[90m" in result
        assert "x = 1" in result
        assert "\x1b[38;" not in result


class TestEncodingFallback:
    def test_non_utf8_stream_does_not_crash(self):
        class AsciiOnlyStream:
            def __init__(self):
                self.parts = []

            def write(self, text):
                self.parts.append(text.encode("ascii").decode("ascii"))

            def flush(self):
                pass

        output = AsciiOnlyStream()
        renderer = MarkdownRenderer(output=output)
        renderer.render("Café\n")
        renderer.finalize()

        assert "Caf" in "".join(output.parts)


class TestTableStreamingRegressions:
    def test_partial_table_row_is_buffered_until_newline(self):
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        for chunk in ["| A |", " B |\n", "|---", "|---|\n", "| 1 |", " 2 |\n", "\n"]:
            renderer.render(chunk)
        renderer.finalize()

        result = strip_ansi(output.getvalue())
        assert "│ A │ B │" in result
        assert "│ 1 │ 2 │" in result


class TestStripAnsiRegressions:
    def test_private_csi_sequence(self):
        assert strip_ansi("\x1b[?25l") == ""

    def test_clear_screen(self):
        assert strip_ansi("\x1b[2J") == ""

    def test_osc_title(self):
        assert strip_ansi("\x1b]0;title\x07") == ""

    def test_osc_hyperlink_keeps_visible_text(self):
        value = "\x1b]8;;https://example.com\x1b\\link\x1b]8;;\x1b\\"
        assert strip_ansi(value) == "link"

    def test_charset_sequence(self):
        assert strip_ansi("\x1b(B") == ""

    def test_stray_escape(self):
        assert strip_ansi("\x1b") == ""

    def test_c1_control(self):
        assert strip_ansi("a\x9b31mb") == "a31mb"


class TestConfigIntegration:
    def test_renderer_loads_config_file(self, tmp_path, monkeypatch):
        (tmp_path / ".markrender.toml").write_text(
            """
[theme]
name = "dracula"

[rendering]
line_numbers = false
code_background = true

[output]
width = 42

[features]
stream_code = false
""",
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)

        renderer = MarkdownRenderer(output=StringIO())

        assert renderer.theme_config["name"] == "dracula"
        assert renderer.line_numbers is False
        assert renderer.code_background is True
        assert renderer.width == 42
        assert renderer.stream_code is False

    def test_explicit_arguments_override_config(self, tmp_path, monkeypatch):
        (tmp_path / ".markrender.toml").write_text(
            '[theme]\nname = "dracula"\n\n[rendering]\nline_numbers = false\n',
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)

        renderer = MarkdownRenderer(
            theme="nord",
            line_numbers=True,
            output=StringIO(),
        )

        assert renderer.theme_config["name"] == "nord"
        assert renderer.line_numbers is True

    def test_config_can_be_disabled(self, tmp_path, monkeypatch):
        (tmp_path / ".markrender.toml").write_text(
            '[theme]\nname = "dracula"\n',
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)

        renderer = MarkdownRenderer(output=StringIO(), use_config=False)

        assert renderer.theme_config["name"] == "github-dark"
