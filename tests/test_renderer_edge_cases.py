"""
Tests for edge cases in the MarkdownRenderer
"""

import unittest
import io
import re
from markrender import MarkdownRenderer

def strip_ansi(text):
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

class TestMarkdownRendererEdgeCases(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        self.renderer = MarkdownRenderer(output=self.output)

    def get_output(self):
        return self.output.getvalue()

    def test_incomplete_bold_at_end_of_chunk(self):
        self.renderer.render("This is **bold")
        self.renderer.render(" and this is not**.")
        self.renderer.finalize()
        
        output = self.get_output()
        # This is still tricky, but we can check for the bold ANSI codes
        self.assertIn("\x1b[1m", output)
        self.assertIn("\x1b[0m", output)

    def test_table_split_across_chunks(self):
        self.renderer.render("| Header 1 |")
        self.renderer.render(" Header 2 |\n")
        self.renderer.render("|---|---|\n")
        self.renderer.render("| Cell 1 |")
        self.renderer.render(" Cell 2 |")
        self.renderer.finalize()

        output = self.get_output()
        self.assertIn("Header 1", output)
        self.assertIn("Header 2", output)
        self.assertIn("Cell 1", output)
        self.assertIn("Cell 2", output)

    def test_nested_blockquotes(self):
        self.renderer.render("> Outer\n")
        self.renderer.render("> > Inner\n")
        self.renderer.render("> Outer again\n")
        self.renderer.finalize()

        output = self.get_output()
        clean_output = strip_ansi(output)
        # This will likely fail, as nested blockquotes are not supported.
        self.assertIn("│ Outer", clean_output)
        self.assertIn("│ Inner", clean_output)
        self.assertIn("│ Outer again", clean_output)

    def test_stray_backticks_in_code_block(self):
        self.renderer.render("```python\n")
        self.renderer.render("print('```')\n")
        self.renderer.render("```\n")
        self.renderer.finalize()

        output = self.get_output()
        self.assertIn("print", output)
        self.assertIn("```", output)
    
    def test_table_split_across_chunks_and_incomplete_row(self):
        self.renderer.render("| Header 1 |")
        self.renderer.render(" Header 2 |\n")
        self.renderer.render("|---|---|\n")
        self.renderer.render("| Cell 1 |")
        self.renderer.render(" Cell 2 |\n")
        self.renderer.render("| Cell 3 |")
        self.renderer.finalize()

        output = self.get_output()
        self.assertIn("Header 1", output)
        self.assertIn("Header 2", output)
        self.assertIn("Cell 1", output)
        self.assertIn("Cell 2", output)
        self.assertIn("Cell 3", output)


if __name__ == '__main__':
    unittest.main()
