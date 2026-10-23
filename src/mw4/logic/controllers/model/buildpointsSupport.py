# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from astroquery.simbad import Simbad
from collections.abc import Callable
from skyfield.api import Angle

MAX_ITERATIONS: int = 20


def generateUntilTarget(
    generate: Callable[[int], None],
    filterPoints: Callable[[], None],
    countPoints: Callable[[], int],
    numberTarget: int,
    stopWhenEmpty: bool = False,
) -> None:
    """Generate points and filter them until the filtered count reaches the target.

    Every pass asks the generator for more points, as the filter removes some of
    them. The loop is limited to MAX_ITERATIONS passes, and optionally stops as
    soon as the filter leaves no point at all.
    """
    numberPoints = 0
    numberFiltered = 0
    iteration = MAX_ITERATIONS
    while numberFiltered < numberTarget:
        numberPoints += numberTarget - numberFiltered
        iteration -= 1
        if iteration <= 0:
            break
        generate(numberPoints)
        filterPoints()
        numberFiltered = countPoints()
        if stopWhenEmpty and numberFiltered == 0:
            break


def querySimbad(ident: str) -> tuple[Angle, Angle] | None:
    """Resolve an object name with SIMBAD, returns RA and DEC or None if unknown."""
    result = Simbad.query_object(ident)
    if not result:
        return None
    return Angle(degrees=float(result["ra"])), Angle(degrees=float(result["dec"]))
