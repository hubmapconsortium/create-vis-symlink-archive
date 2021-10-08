cwlVersion: v1.1
class: CommandLineTool
label: Create directory containing symlinks to relevant files for visualization team
hints:
  DockerRequirement:
    dockerPull: hubmap/create-vis-symlink-archive
baseCommand: ["/opt/create_visualization_dir.py"]

inputs:
  ometiff_dir:
    type: Directory
    inputBinding:
      position: 1
  sprm_output:
    type: Directory
    inputBinding:
      position: 2
outputs:
  symlink_archive:
    type: File
    outputBinding:
      glob: symlinks.tar
