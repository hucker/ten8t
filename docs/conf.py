# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


def copy_readme_to_docs():
    """
    Copies the README.md file from the root folder to the docs folder
    while adjusting image paths using a simple string replacement.
    """
    import os

    # Paths for the source and destination README.md files
    source_path = os.path.abspath("../README.md")  # Root-level README.md
    destination_path = os.path.abspath("README.md")  # Copy to the docs folder

    try:
        # Read the original README.md content
        with open(source_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Replace the image paths (assuming specific paths need adjustment)
        # Example: Change 'docs/_static/' to './_static/' for Sphinx.  This makes
        # github and readthedocs work
        adjusted_content = content.replace("docs/_static/", "./_static/")

        # Write the adjusted content to the docs/README.md file
        with open(destination_path, "w", encoding="utf-8") as file:
            file.write(adjusted_content)

        print(f"Copied and adjusted README.md from {source_path} to {destination_path}")

    except Exception as e:
        print(f"An error occurred while copying README.md: {e}")



# This really should be a symlink so it could be two way?
copy_readme_to_docs()

project = 'ten8t'
copyright = '2025, Chuck Bass'
author = 'Chuck Bass'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration



extensions = [
    'sphinx.ext.autodoc',  # For generating API documentation from docstrings
    'sphinx.ext.autosummary',  # Creates module/function/class summaries
    'sphinx.ext.napoleon',  # For Google/NumPy-style docstrings
    'sphinx.ext.viewcode',  # View source code links\
    'sphinx.ext.intersphinx',
    'myst_parser',  # Mark down
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),  # For the Python standard library
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/latest/', None),  # SQLAlchemy library
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "openpyxl": ("https://openpyxl.readthedocs.io/en/stable/", None),

}

# Configure MyST-Parser
myst_enable_extensions = [
    "colon_fence",  # Optional: Allows ::: fence for better Markdown support
]
myst_suppress_warnings = ["myst.header"]
myst_config = {
    "suppress_warnings": ["myst.header"]
}


templates_path = ['_templates']
exclude_patterns = ['_build',
                    'Thumbs.db',
                    '.DS_Store',
                    'src/ten8t/examples/**',
                    'src/ten8t/cli/**',
                    'src/ten8t/st_ten8t/**',
                    'src/ten8t/setup.py',
                    ]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

autodoc_mock_imports = ["ping3", "openpyxl", "camelot", "pandas", "sqlalchemy"]

autodoc_type_aliases = {
    "pd": "pandas",
    "np": "numpy",
}

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']

# Specify source file extensions
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

suppress_warnings = ["epub.duplicate"]


autosummary_generate = True

nitpicky = True

# Per stack overflow, type aliases are not handled by sphinx so you need to override.
nitpick_ignore = [('py:class', 'type'),
                  ('py:class', '_type_'),
                  ('py:class', 'optional'),
                  ('py:class', 'TR'),
                  ('py:class', 'StrListOrNone'),
                  ('py:class', 'StrOrNone'),
                  ('py:class', 'callable'),
                  ('py:class', 'defaultdict'),
                  ('py:class', 'StrListOrNone'),
                  ('py:class', 'Function'),
                  ("py:class", "ten8t_score.ScoreByFunctionBinary.strategy_names"),
                  ("py:func", "ten8t_score.ScoreByFunctionBinary.strategy_name")

                  ]

# Make sure Sphinx can find your library
import os
import sys

sys.path.insert(0, os.path.abspath('../../src'))  # Path to your library
sys.path.insert(0, os.path.abspath('../src'))  # Path to your library

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
