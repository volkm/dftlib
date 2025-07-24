# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Needed for version information
import dftlib

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "dftlib"
copyright = "2018 - 2025 Matthias Volk"
author = "Matthias Volk"
release = dftlib.__version__
language = "en"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autosummary",
    #'sphinx.ext.intersphinx',
    "sphinx.ext.githubpages",
    "sphinx_copybutton",
]
autosectionlabel_prefix_document = True
autosummary_generate = True

# Autodoc options
autoclass_content = "both"  # Add documentation for both the class and __init__

templates_path = ["_templates"]
exclude_patterns = []

add_module_names = False


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_nefertiti"
html_theme_options = {
    ## Font options
    "sans_serif_font": "Nunito",
    "monospace_font": "Ubuntu Sans Mono",
    ## Style options
    "style": "orange",
    "style_header_neutral": False,
    "pygments_light_style": "pastie",
    "pygments_dark_style": "dracula",
    ## Repos
    "repository_name": "dftlib",
    "repository_url": "https://github.com/volkm/dftlib",
    ## Header options
    "header_links_in_2nd_row": False,
    "header_links": [
        {
            "text": "Installation",
            "link": "installation",
        },
        {
            "text": "API",
            "link": "api",
            "match": "api/*",
        },
        {
            "text": "DFT Visualization",
            "link": "https://moves-rwth.github.io/dft-gui/",
        },
    ],
    ## Footer options
    "footer_links": [
        {
            "text": "Documentation",
            "link": "https://volkm.github.io/dftlib/",
        },
        {
            "text": "Package",
            "link": "https://pypi.org/project/dftlib/",
        },
        {
            "text": "Repository",
            "link": "https://github.com/volkm/dftlib/",
        },
        {
            "text": "Issues",
            "link": "https://github.com/volkm/dftlib/issues",
        },
    ],
    "show_powered_by": True,
}
html_static_path = ["_static"]
html_css_files = ["custom.css"]
