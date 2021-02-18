#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.1

inputs:
  ometiff_dir:
    type: Directory
  sprm_output:
    type: Directory

outputs:
  symlink_archive:
    type: File
    outputSource: archive_symlinks/symlink_archive

steps:
  archive_symlinks:
    run: steps/create_dir_for_viz.cwl
    in:
      ometiff_dir: ometiff_dir
      sprm_output: sprm_output
    out: [symlink_archive]
