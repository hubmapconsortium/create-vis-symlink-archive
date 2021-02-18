# Imaging symlink archiving

This pipeline accepts output of Cytokit and SPRM, and creates a `.tar`
archive containing symbolic links with filename conventions that are
useful for HuBMAP user interface code.

CWL workflows cannot return symbolic links directly, hence the `.tar` output.
The output of this pipeline is extracted by Airflow.
