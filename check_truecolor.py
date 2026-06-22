
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter, TerminalTrueColorFormatter
from rich.text import Text
from rich.console import Console

code = "def hello():\n    print('world')"
lexer = PythonLexer()

print("--- Terminal256Formatter ---")
formatter256 = Terminal256Formatter(style='monokai')
ansi256 = highlight(code, lexer, formatter256)
rich_text256 = Text.from_ansi(ansi256)
print(f"ANSI len: {len(ansi256)}")
print(f"First span style: {rich_text256.spans[0] if rich_text256.spans else 'None'}")

print("\n--- TerminalTrueColorFormatter ---")
formatterTC = TerminalTrueColorFormatter(style='monokai')
ansiTC = highlight(code, lexer, formatterTC)
rich_textTC = Text.from_ansi(ansiTC)
print(f"ANSI len: {len(ansiTC)}")
print(f"First span style: {rich_textTC.spans[0] if rich_textTC.spans else 'None'}")

print("\n--- Visual Check ---")
console = Console()
console.print("256:")
console.print(rich_text256)
console.print("TrueColor:")
console.print(rich_textTC)
