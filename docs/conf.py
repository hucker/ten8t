# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information



def copy_readme_to_docs(ignore_errors=True):
    """
    Copies the README.md file from the root folder to the docs folder.

    Parameters:
        ignore_errors (bool): If True, ignores errors like file not found.
    """
    source_path = None
    try:
        import os
        import shutil

        source_path = os.path.abspath("../README.md")  # The README.md in the root folder
        destination_path = os.path.abspath("README.md")  # The README.md to be placed in the docs folder

        # Copy the README.md file
        shutil.copy(source_path, destination_path)
        print(f"Copied {source_path} to {destination_path}")
    except FileNotFoundError as e:
        if not ignore_errors:
            print(f"Error: Source file {source_path} not found.")
        else:
            print(f"Ignored error: {e}")
    except Exception as e:
        if not ignore_errors:
            print(f"An unexpected error occurred: {e}")
        else:
            print(f"Ignored unexpected error: {e}")


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

# Allows hyperlinking to stdlibrary stuff like pathlib, os, sys
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# Configure MyST-Parser
myst_enable_extensions = [
    "colon_fence",  # Optional: Allows ::: fence for better Markdown support
]

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
html_static_path = ['_static', '../img']

# Specify source file extensions
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

autosummary_generate = True

nitpicky = True

# Make sure Sphinx can find your library
import os
import sys

sys.path.insert(0, os.path.abspath('../../src'))  # Path to your library
sys.path.insert(0, os.path.abspath('../src'))  # Path to your library

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
