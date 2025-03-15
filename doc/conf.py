############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2024 by mworion
#
# Licence APL2.0
#
###########################################################

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = "MountWizzard4"
copyright = "2025, mworion"
author = "Michael Würtenberger"

# The full version, including alpha/beta/rc tags
version = "4.0.0a19"
release = "4.0.0a19"
master_doc = "index"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    "sphinxcontrib.drawio",
    "sphinx_simplepdf",
]

autosectionlabel_prefix_document = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_theme_options = {
    "logo": "mw4.png",
    "logo_name": True,
    "fixed_sidebar": True,
    "page_width": "1400px",
    "sidebar_width": "300px",
    "base_bg": "#FFFFFFFF",
    "base_text": "#FFFFFFFF",
    "body_bg": "#FFFFFFFF",
}

simplepdf_file_name = "mountwizzard4-" + version + ".pdf"
simplepdf_use_weasyprint_api = True
simplepdf_vars = {
    "primary": "rgb(32, 128, 208)",
    "primary_opaque": "#186098",
    "secondary": "#186098",
    "cover": "#ffffff",
    "white": "#ffffff",
    "links": "rgb(32, 128, 208)",
    "cover-bg": "url(mw4.png) no-repeat center",
    "cover-overlay": "rgba(32, 128, 208, 0.25)",
    "top-left-content": "counter(page)",
    "bottom-center-content": "version",
}
