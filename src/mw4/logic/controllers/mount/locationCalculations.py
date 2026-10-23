# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from skyfield.api import Angle, wgs84
from skyfield.toposlib import GeographicPosition


def buildLocation(
    current: GeographicPosition,
    lat: Angle | None = None,
    lon: Angle | None = None,
    elev: float | None = None,
) -> tuple[GeographicPosition, str]:
    """
    Builds a new position from the given parts; missing parts are taken from the current
    location. returns the position and the log text.
    """
    lat = current.latitude if lat is None else lat
    lon = current.longitude if lon is None else lon
    elev = current.elevation.m if elev is None else elev
    topo = wgs84.latlon(
        longitude_degrees=lon.degrees,
        latitude_degrees=lat.degrees,
        elevation_m=elev,
    )
    text = f"Location set to:     [{lat.degrees:3.2f} deg, "
    text += f"{lon.degrees:3.2f} deg, {elev:4.1f} m]"
    return topo, text
