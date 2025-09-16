# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
latex_engine = 'xelatex'

# latex_elements = {
#     'preamble': r'''
#     '''
#     }

project = "wg_tool"
copyright = '2022-%Y, Gene C'
author = 'Gene C'
release = '8.0.rc2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
        'sphinx.ext.extlinks',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_css_files = ['custom.css']



# links
extlinks = {
   'Github': ('https://github.com/gene-git/%s', '%s'),
   'AUR': ('https://aur.archlinux.com/packages/%s', 'Archlinux %s'),
   'wg-client': ('https://github.com/gene-git/wg-client', 'wg-client'),
}

