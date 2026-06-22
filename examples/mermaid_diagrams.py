"""
Mermaid Diagram Rendering Example
Demonstrates rendering Mermaid diagrams in the terminal
"""

from markrender import MarkdownRenderer


def main():
    """Demonstrate Mermaid diagram rendering"""
    
    renderer = MarkdownRenderer(
        theme='github-dark',
        line_numbers=False
    )
    
    markdown_content = """
# Mermaid Diagram Examples

Mermaid diagrams are rendered as ASCII/Unicode art in the terminal.

## Flowchart Example

```mermaid
graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> B
    C --> E[End]
```

## Simple Sequence

```mermaid
graph LR
    A[Client] --> B[Server]
    B --> C[Database]
    C --> B
    B --> A
```

## Process Flow

```mermaid
graph TD
    Step1[Receive Input] --> Step2[Validate]
    Step2 --> Step3[Process]
    Step3 --> Step4[Save]
    Step4 --> Step5[Return Result]
```

## Class Diagram Style

```mermaid
graph TB
    User[User Class] --> Controller[Controller]
    Controller --> Model[Model]
    Controller --> View[View]
    Model --> Database[(Database)]
```

## Decision Tree

```mermaid
graph TD
    Q1[Is it alive?] -->|Yes| Q2[Does it move?]
    Q1 -->|No| A1[It's a rock]
    Q2 -->|Yes| A2[It's an animal]
    Q2 -->|No| A3[It's a plant]
```

These diagrams are automatically parsed and rendered as ASCII art!
"""
    
    print("=" * 70)
    print("Mermaid Diagram Rendering Demo")
    print("=" * 70)
    print()
    
    renderer.render(markdown_content)
    renderer.finalize()
    
    print()
    print("=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
