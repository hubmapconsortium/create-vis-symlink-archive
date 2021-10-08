from pathlib import Path
from typing import List, Tuple
from unittest import TestCase

from create_visualization_dir import get_region

data: List[Tuple[Path, str]] = [
    (Path("reg011_S20030077_region_011_mask.ome.tiff"), "reg011_S20030077"),
    (Path("reg1_stitched_expressions.ome.tiff"), "reg1"),
    (Path("no_image"), None),
]


class FilenameMatchTest(TestCase):
    def test_known_patterns(self):
        for path, region in data:
            with self.subTest(path):
                self.assertEqual(region, get_region(path))
