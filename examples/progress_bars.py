"""
Progress Bars Example
Demonstrates - [X%] task progress syntax
"""

from markrender import MarkdownRenderer


def main():
    """Demonstrate progress bar rendering"""
    
    renderer = MarkdownRenderer(
        theme='github-dark',
        line_numbers=False
    )
    
    markdown_content = """
# Progress Bar Examples

Track task progress with visual progress bars using - [X%] syntax.

## Basic Progress

- [0%] Not started
- [10%] Just started
- [25%] In progress (early stage)
- [50%] Halfway complete
- [75%] Almost done
- [90%] Nearly finished
- [100%] Completed ✅

## Project Timeline

### Phase 1: Planning
- [100%] Requirements gathering
- [100%] Stakeholder interviews
- [100%] Technical specification

### Phase 2: Design
- [100%] Architecture design
- [75%] UI/UX mockups
- [50%] Database schema

### Phase 3: Development
- [50%] Backend API
- [25%] Frontend components
- [0%] Integration testing

### Phase 4: Deployment
- [0%] Staging deployment
- [0%] User acceptance testing
- [0%] Production release

## Color Coding

Progress bars are color-coded:

- [15%] 🔴 Red: 0-24% (Just started)
- [35%] 🟠 Orange: 25-49% (Making progress)
- [60%] 🟡 Yellow: 50-74% (Halfway there)
- [85%] 🟢 Green: 75-99% (Almost done)
- [100%] ✅ Checkmark: Complete!

## Sprint Progress

Sprint 24 Progress:

- [100%] Setup development environment
- [100%] Create database models
- [100%] Implement authentication
- [75%] Build REST API endpoints
- [50%] Write unit tests
- [25%] Create documentation
- [0%] Deploy to staging

Keep track of your tasks with progress bars!
"""
    
    print("=" * 70)
    print("Progress Bars Demo")
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
