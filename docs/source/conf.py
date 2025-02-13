# Configuration file for the Sphinx documentation builder.
import sys
import os
sys.path.insert(0, os.path.abspath('../..'))
# -- Project information

project = 'ROVEaC'
# copyright = '2024, Adam Lehavi'
# author = 'Adam Lehavi'
copyright = '2024, Anonymized for Paper Submission'
author = 'Anonymized for Paper Submission'

version = '1.0.0'
release = version

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'

autosummary_generate = True
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
}