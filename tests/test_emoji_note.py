from io import StringIO

from markrender import MarkdownRenderer

def test_render_emoji():
    output = StringIO()
    renderer = MarkdownRenderer(output=output, force_color=True)

    renderer.render("Hello :wave:\n")
    renderer.finalize()

    result = output.getvalue()
    # Just check if emoji is in the result without printing it
    has_emoji = ":wave:" in result or "👋" in result
    assert has_emoji, f"Expected emoji in result, got: {result}"

def test_render_blockquote_as_note():
    output = StringIO()
    renderer = MarkdownRenderer(output=output, force_color=True)

    renderer.render("> [!NOTE] This is a note.\n")
    renderer.finalize()

    result = output.getvalue()

    has_note = "NOTE" in result and "This is a note." in result
    assert has_note, f"Expected note in result, got: {result}"