[![Build Status](https://travis-ci.com/hubmapconsortium/codex-pipeline.svg?branch=master)](https://travis-ci.com/hubmapconsortium/create-vis-symlink-archive)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Imaging symlink archiving

This pipeline accepts output of Cytokit and SPRM, and creates a `.tar`
archive containing symbolic links with filename conventions that are
useful for HuBMAP user interface code.

CWL workflows cannot return symbolic links directly, hence the `.tar` output.
The output of this pipeline is extracted by Airflow.
