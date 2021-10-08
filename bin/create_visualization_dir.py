#!/usr/bin/env python3
import argparse
import logging
import re
import tarfile
from collections import defaultdict
from pathlib import Path
from pprint import pformat
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-7s - %(message)s",
)
logger = logging.getLogger(__name__)

expression_dir_names = ["expr", "expressions"]
extensions = ["tif", "tiff"]
integer_pattern = re.compile(r"(\d+)")
region_pattern = re.compile(r"^(?P<region>reg\d+)(?P<image>_S\d+)?")


def list_directory_tree(directory: Path) -> str:
    return pformat(sorted(directory.glob("**/*"))) + "\n"


def print_directory_tree(directory: Path):
    print(list_directory_tree(directory))


def try_parse_int(value: str) -> Union[int, str]:
    if value.isdigit():
        return int(value)
    return value


def alphanum_sort_key(path: Path) -> Sequence[Union[int, str]]:
    """
    Produces a sort key for file names, alternating strings and integers.
    Always [string, (integer, string)+] in quasi-regex notation.
    >>> alphanum_sort_key(Path('s1 1 t.tiff'))
    ['s', 1, ' ', 1, ' t.tiff']
    >>> alphanum_sort_key(Path('0_4_reg001'))
    ['', 0, '_', 4, '_reg', 1, '']
    """
    return [try_parse_int(c) for c in integer_pattern.split(path.name)]


def get_img_listing(in_dir: Path) -> List[Path]:
    img_listing = []
    for extension in extensions:
        img_listing.extend(in_dir.glob(f"**/*.{extension}"))
    return sorted(img_listing, key=alphanum_sort_key)


def make_dir_if_not_exists(dir_path: Path):
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)


def get_region(path: Path) -> Optional[str]:
    if s := region_pattern.match(path.name):
        pieces = [group or "" for group in s.groups()]
        return "".join(pieces)


def get_file_paths_by_region(dir_listing: Iterable[Path]) -> Dict[str, List[Path]]:
    file_path_by_reg = defaultdict(list)

    for path in dir_listing:
        if (region := get_region(path)) is not None:
            file_path_by_reg[region].append(path)

    return file_path_by_reg


def create_relative_symlink_target(file_path: Path, file_dir: Path, file_symlink: Path) -> Path:
    relative_input_path = file_dir.name / file_path.relative_to(file_dir)
    relative_output_path_piece = Path(*[".."] * (len(file_symlink.parts) - 1))
    return relative_output_path_piece / relative_input_path


def find_expression_dir(ometiff_dir: Path) -> Path:
    for possibility in expression_dir_names:
        if (d := ometiff_dir / possibility).is_dir():
            return d
    raise ValueError("Couldn't find expression directory")


def main(ometiff_dir, sprm_output_dir):
    cytometry_ometiff_dir = ometiff_dir / "mask"
    expressions_ometiff_dir = find_expression_dir(ometiff_dir)

    logger.debug(f"{ometiff_dir=}")
    logger.debug("Cytometry OME-TIFF directory listing:")
    logger.debug("\n" + list_directory_tree(cytometry_ometiff_dir))
    logger.debug("Expressions OME-TIFF directory listing:")
    logger.debug("\n" + list_directory_tree(expressions_ometiff_dir))
    logger.debug(f"{sprm_output_dir=}")
    logger.debug("SPRM directory listing:")
    logger.debug("\n" + list_directory_tree(sprm_output_dir))

    output_dir = Path("for-visualization")
    make_dir_if_not_exists(output_dir)

    segmentation_mask_ometiffs = get_file_paths_by_region(get_img_listing(cytometry_ometiff_dir))
    expressions_ometiffs = get_file_paths_by_region(get_img_listing(expressions_ometiff_dir))
    sprm_outputs = get_file_paths_by_region(sprm_output_dir.iterdir())

    symlinks_to_archive: List[Tuple[Path, Path]] = []

    # TODO: Perhaps a proper function to do this in a less repetitive way would be nicer.
    for region in segmentation_mask_ometiffs:
        reg_dir = output_dir / region
        make_dir_if_not_exists(reg_dir)

    for region in segmentation_mask_ometiffs:
        reg_dir = output_dir / region
        symlink = reg_dir / "segmentation.ome.tiff"
        for img_path in segmentation_mask_ometiffs[region]:
            link_target = create_relative_symlink_target(img_path, ometiff_dir, symlink)
            symlinks_to_archive.append((symlink, link_target))

    for region in expressions_ometiffs:
        reg_dir = output_dir / region
        symlink = reg_dir / "antigen_exprs.ome.tiff"
        for img_path in expressions_ometiffs[region]:
            link_target = create_relative_symlink_target(img_path, ometiff_dir, symlink)
            symlinks_to_archive.append((symlink, link_target))

    for region in sprm_outputs:
        reg_dir = output_dir / region
        for sprm_file_path in sprm_outputs[region]:
            # kind of hacky, but works well enough
            symlink = reg_dir / sprm_file_path.name.split(".ome.tiff", 1)[1].lstrip("-")
            link_target = create_relative_symlink_target(sprm_file_path, sprm_output_dir, symlink)
            symlinks_to_archive.append((symlink, link_target))

    with tarfile.open("symlinks.tar", "w") as t:
        for symlink, link_target in symlinks_to_archive:
            symlink.symlink_to(link_target)
            logger.info(f"Archiving symlink {symlink} -> {link_target}")
            t.add(symlink)

    for symlink, link_target in symlinks_to_archive:
        symlink.unlink()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Set up a directory containing the files for the visualization team."
    )
    parser.add_argument(
        "ometiff_dir",
        help="Path to Cytokit output directory from OME-TIFF creation pipeline step.",
        type=Path,
    )
    parser.add_argument(
        "sprm_output_dir",
        help="Path to output directory from SPRM pipeline step.",
        type=Path,
    )

    args = parser.parse_args()
    main(args.ometiff_dir, args.sprm_output_dir)
