# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

from mw4.mountcontrol.progStar import ProgStar
from skyfield.api import Angle, Star


def test_APoint_pierside_1():
    aPoint = ProgStar(
        Star(ra_hours=0, dec_degrees=0),
        Star(ra_hours=0, dec_degrees=0),
        Angle(hours=0),
        "e",
    )
    aPoint.pierside = "E"
    assert aPoint.pierside == "E"


def test_APoint_pierside_2():
    aPoint = ProgStar(
        Star(ra_hours=0, dec_degrees=0),
        Star(ra_hours=0, dec_degrees=0),
        Angle(hours=0),
        "e",
    )
    aPoint.pierside = "x"
    assert aPoint.pierside == "E"
