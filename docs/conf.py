# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ten8t'
copyright = '2025, Chuck Bass'
author = 'Chuck Bass'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # For generating API documentation from docstrings
    'sphinx.ext.napoleon',  # For Google/NumPy-style docstrings
    'sphinx.ext.viewcode',  # View source code links
]

html_theme = 'sphinx_rtd_theme'

templates_path = ['_templates']
exclude_patterns = []

# Make sure Sphinx can find your library
import os
import sys

sys.path.insert(0, os.path.abspath('../src'))  # Path to your library

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_static_path = ['_static']
