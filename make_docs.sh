#!/usr/bin/env bash

# A script for generating the documentation and tutorial in various formats.

# Create documentation with sphinx (needs sphinx), uncomment as needed.
cd docs/manual
sphinx-build -b html -d _build/doctrees . _build/html
# sphinx-build -b epub -d _build/doctrees . _build/epub
# sphinx-build -b latex -d _build/doctrees . _build/latex
# make -C _build/latex all-pdf
# sphinx-build -b linkcheck -d _build/doctrees . _build/linkcheck
cd ../..

# Create tutorial with ipython (needs ipython), not there, yet.
# cd docs/tutorial
# ipython nbconvert --to html getting_started.ipynb
# cd ../..
