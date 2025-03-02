############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
from PySide6.QtCore import QMutex
import numpy as np
import erfa
from skyfield.api import Angle
from skyfield.toposlib import GeographicPosition

# local import

__all__ = [
    "J2000ToJNow",
    "J2000ToAltAz",
    "JNowToJ2000",
    "diffModulusAbs",
    "diffModulusSign",
]

log = logging.getLogger()
mutex = QMutex()


def JNowToJ2000(ra: Angle, dec: Angle, timeJD: float) -> (Angle, Angle):
    """ """
    mutex.lock()
    ra = ra.radians
    dec = dec.radians
    ra = erfa.anp(ra + erfa.eo06a(timeJD.tt, 0.0))
    raConv, decConv, _ = erfa.atic13(ra, dec, timeJD.ut1, 0.0)
    ra = Angle(radians=raConv, preference="hours")
    dec = Angle(radians=decConv, preference="degrees")
    mutex.unlock()
    return ra, dec


def J2000ToJNow(ra: Angle, dec: Angle, timeJD: float) -> (Angle, Angle):
    """ """
    mutex.lock()
    ra = ra.radians
    dec = dec.radians
    raConv, decConv, eo = erfa.atci13(ra, dec, 0, 0, 0, 0, timeJD.ut1, 0)
    raConv = erfa.anp(raConv - eo)
    ra = Angle(radians=raConv, preference="hours")
    dec = Angle(radians=decConv, preference="degrees")
    mutex.unlock()
    return ra, dec


def J2000ToAltAz(
    ra: Angle, dec: Angle, timeJD: float, location: GeographicPosition
) -> (Angle, Angle):
    """ """
    mutex.lock()
    ra = ra.radians
    dec = dec.radians
    lat = location.latitude.radians
    lon = location.longitude.radians
    elevation = location.elevation.m

    v = erfa.atco13(
        ra,
        dec,
        0.0,
        0.0,
        0.0,
        0.0,
        timeJD.ut1,
        0.0,
        0,
        lon,
        lat,
        elevation,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )
    aob, zob, hob, dob, rob, eo = v
    decConv = np.pi / 2 - zob

    azimuth = Angle(radians=aob, preference="degrees")
    altitude = Angle(radians=decConv, preference="degrees")
    mutex.unlock()
    return azimuth, altitude


def diffModulusAbs(x: float, y: float, m: int) -> float:
    diff = abs(y - x)
    diff = diff % m
    return min(diff, abs(diff - m))


def diffModulusSign(x: float, y: float, m: int) -> float:
    x = (x + m) % m
    y = (y + m) % m
    diff = y - x
    diff = diff % m
    if diff > m / 2:
        diff -= m
    return diff


"""
remarks from discussions about correct transformation thread in 10micron forum
https://www.10micron.eu/forum/viewtopic.php?f=18&t=791

The correct result is SOFA Atci13 (at least, it is consistent with the 10micron
coordinate transformation, with a < 1 arcsecond difference). It seems that
libNOVA/NOVAS are correct, but they don't account for nutation and light
aberration (the difference between these two is negligible) - i.e. these are
coordinates of the "mean equinox of date".

The "Jnow" coordinates accepted by the mount shouldn't account for refraction
(well: it depends on the side you are looking from, let's say that in order to
compute the Jnow coordinates from the J2000.0 coordinates you don't need to
correct for refraction).

The refraction correction is done transparently by the mount using the current
refraction parameters when it converts the Jnow coordinates to angular readouts
of the encoders (and back).

If Atco13 with refraction set to zero and Atci13 agree to 1 arcsecond, I'd say
that it's equivalent to use any of them.

Sorry, I was meaning: NOVAS is "correct" in the sense that it computes a correct
precession, but does not account for nutation, so it isn't "correct" in the sense
that is the right transformation to use. If you take the NOVAS result and apply
nutation/light aberration, you should obtain the right transformation.

Atci13 (or Atco13 with zero refraction), which account for precession, nutation
and light aberration, but NOT for refraction, seems ok.

By the way, there are some subtle effects of less than one arcsecond that aren't
worth to model (such as diurnal aberration for example), but these can be the
source of the small differences between different algorithms.

Finally:
I looked at the SOFA AstrometryTools documentation. The algorithms used in the
mount don't use the CIRS (celestial intermediate reference system), but use what
it is defined as "classical geocentric apparent place" in the "Quick start"
section of the document. So you would obtain the correct coordinates by using
iauAtci13. Also in section 2.2 - Current Coordinates of that document the
definitions are consistent. Residual (and negligible) differences will be due to
the fact that the mount algorithms are less refined that the ones used in SOFA.
"""
