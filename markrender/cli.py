#!/usr/bin/env python3
"""
Command-line interface for MarkRender
Convenience wrapper around markrender.__main__
"""

import sys
from .__main__ import main

if __name__ == '__main__':
    sys.exit(main())
