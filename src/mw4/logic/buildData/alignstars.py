# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
from pathlib import Path

ALIGN_STARS_FILE = Path(__file__).with_name("alignStars.json")


def generateAlignStars() -> dict[str, list[float]]:
    """
    generateAlignStars returns the alignment stars which are present in the
    mount computer from the hipparcos catalogue. for a correct calculation we
    need beside the J2000 coordinates the proper motion in ra and dec, the
    parallax and the radial velocity as the stars move over time. the data was
    calculated from the hipparcos catalogue using the skyfield library and is
    stored in alignStars.json next to this module.

    each star is stored as
    [ra, dec, ra proper motion, dec proper motion, parallax, radial velocity]
    based on J2000 epoch. the units are fitting erfa needs:
    [radians, radians, radians / year, radians / year, arc sec, km / s]
    """
    with ALIGN_STARS_FILE.open(encoding="utf-8") as handle:
        return json.load(handle)
