#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MarkRender - Professional Terminal Markdown Renderer
A production-ready library for rendering streaming LLM markdown responses.
"""

from setuptools import setup, find_packages
import os

# Read long description from README
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = __doc__

setup(
    name='markrender',
    version='1.0.0',
    description='Professional terminal markdown renderer for streaming LLM responses',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Praneeth Gandodi',
    author_email='',
    url='https://github.com/Praneeth-Gandodi/markrender',
    packages=find_packages(exclude=['tests', 'tests.*', 'examples']),
    python_requires='>=3.7',
    install_requires=[
        'pygments>=2.7.0',
        'emoji>=1.6.0',
        'rich>=13.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.10.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup',
        'Topic :: Terminals',
    ],
    keywords='markdown terminal rendering streaming llm cli',
    project_urls={
        'Bug Reports': 'https://github.com/Praneeth-Gandodi/markrender/issues',
        'Source': 'https://github.com/Praneeth-Gandodi/markrender',
    },
)
