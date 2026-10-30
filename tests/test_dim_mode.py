"""Dim mode renders the whole block in one muted gray tone."""

from io import StringIO

from markrender import MarkdownRenderer
from markrender.colors import strip_ansi

GRAY = "\x1b[90m"
RESET = "\x1b[0m"


def render(markdown, dim_mode=True, force_color=True):
    output = StringIO()
    renderer = MarkdownRenderer(
        output=output,
        force_color=force_color,
        line_numbers=False,
    )
    renderer.render(markdown, dim_mode=dim_mode)
    renderer.finalize()
    return output.getvalue()


def assert_uniform_gray(result):
    assert "\x1b[38;" not in result
    assert "\x1b[1m" not in result
    assert "\x1b[2m" not in result
    for line in result.splitlines():
        if line:
            assert line.startswith(GRAY)
            assert line.endswith(RESET)


def test_paragraph_is_fully_dimmed():
    result = render("plain **bold** and *italic* text\n")

    assert result == f"{GRAY}plain bold and italic text{RESET}\n"


def test_list_text_is_dimmed_not_just_the_bullet():
    result = render("- item with **bold**\n")

    assert f"{GRAY}• item with bold{RESET}\n" in result
    assert_uniform_gray(result)


def test_table_contents_are_dimmed():
    result = render("| A | B |\n|---|---|\n| one | two |\n")

    assert_uniform_gray(result)
    visible = strip_ansi(result)
    assert "│ one │ two │" in visible


def test_blockquote_text_is_dimmed():
    result = render("> quote with **bold**\n")

    assert f"{GRAY}│ quote with bold{RESET}\n" in result
    assert_uniform_gray(result)


def test_alert_text_is_dimmed():
    result = render("> [!NOTE]\n> useful information\n")

    assert_uniform_gray(result)
    assert "useful information" in strip_ansi(result)


def test_heading_is_dimmed():
    result = render("# Heading\n")

    assert f"{GRAY}# Heading{RESET}\n" in result
    assert_uniform_gray(result)


def test_code_keeps_content_but_not_syntax_colors():
    result = render("```python\ndef hello():\n    return 1\n```\n")

    visible = strip_ansi(result)
    assert "def hello():" in visible
    assert "return 1" in visible
    assert_uniform_gray(result)


def test_dim_mode_applies_only_to_its_own_call():
    output = StringIO()
    renderer = MarkdownRenderer(
        output=output,
        force_color=True,
        line_numbers=False,
    )
    renderer.render("dim\n", dim_mode=True)
    renderer.render("normal\n")
    renderer.finalize()

    result = output.getvalue()
    assert f"{GRAY}dim{RESET}\n" in result
    assert result.endswith("normal\n")
    assert f"{GRAY}normal" not in result


def test_dim_mode_preserves_block_spacing():
    output = StringIO()
    renderer = MarkdownRenderer(
        output=output,
        force_color=True,
        line_numbers=False,
    )
    renderer.render("# Heading\n\n", dim_mode=True)
    renderer.render("paragraph\n")
    renderer.finalize()

    assert strip_ansi(output.getvalue()) == "\n# Heading\n\nparagraph\n"


def test_dim_mode_emits_no_ansi_without_color_support():
    result = render("plain\n", force_color=False)

    assert result == "plain\n"
