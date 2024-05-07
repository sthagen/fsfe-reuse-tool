# SPDX-FileCopyrightText: 2017 Free Software Foundation Europe e.V. <https://fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import os
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_version
from pathlib import Path
from shutil import copyfile

DOCS_DIR = Path(os.path.dirname(__file__))
ROOT_DIR = (DOCS_DIR / "..").resolve()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "reuse"
copyright = "2017, Free Software Foundation Europe. CC-BY-SA-4.0"
author = "Free Software Foundation Europe"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
try:
    # The full version, including alpha/beta/rc tags.
    release = get_version("reuse")
except PackageNotFoundError:
    release = "3.0.2"

# The short X.Y.Z version.
version = ".".join(release.split(".")[:3])

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinxcontrib.apidoc",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Extensions configuration ------------------------------------------------

apidoc_module_dir = str(ROOT_DIR / "src/reuse")
# apidoc_output_dir = "api"
# apidoc_excluded_paths = []
apidoc_separate_modules = True
apidoc_toc_file = False
apidoc_extra_args = ["--maxdepth", "2"]

autodoc_member_order = "bysource"

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_logo = "reuse-r-only.svg"
html_static_path = ["_static"]

# -- Options for man output --------------------------------------------------
man_pages = [
    (
        "man/reuse",
        "reuse",
        "A tool for compliance with the REUSE recommendations",
        "Free Software Foundation Europe",
        1,
    ),
    (
        "man/reuse-annotate",
        "reuse-annotate",
        "Add REUSE information to files",
        "Free Software Foundation Europe",
        1,
    ),
    (
        "man/reuse-convert-dep5",
        "reuse-convert-dep5",
        "Convert .reuse/dep5 to REUSE.toml",
        "Free Software Foundation Europe",
        1,
    ),
    (
        "man/reuse-download",
        "reuse-download",
        "Download license files",
        "Free Software Foundation Europe",
        1,
    ),
    (
        "man/reuse-lint",
        "reuse-lint",
        "Verify whether a project is compliant with the REUSE Specification",
        "Free Software Foundation Europe",
        1,
    ),
    (
        "man/reuse-spdx",
        "reuse-spdx",
        "Generate SPDX bill of materials",
        "Free Software Foundation Europe",
        1,
    ),
    (
        "man/reuse-supported-licenses",
        "reuse-supported-licenses",
        "Print a list of supported licenses",
        "Free Software Foundation Europe",
        1,
    ),
]

# -- Custom ------------------------------------------------------------------


def copy_markdown(_):
    """Copy the markdown files from the root of the project into the docs/
    directory.
    """
    copyfile(ROOT_DIR / "README.md", DOCS_DIR / "readme.md")
    copyfile(ROOT_DIR / "CHANGELOG.md", DOCS_DIR / "history.md")
    # this used to be renamed to 'contributing.md', but this caused a conflict
    # with the ToC in the README.
    copyfile(ROOT_DIR / "CONTRIBUTING.md", DOCS_DIR / "contribute.md")


def setup(app):
    app.connect("builder-inited", copy_markdown)
