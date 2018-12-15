############################################################
# -*- coding: utf-8 -*-
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2016, 2017, 2018
#
# Licence APL2.0
#
############################################################
# standard libraries
from threading import Lock
# external packages
# noinspection PyProtectedMember
from astropy import _erfa as ERFA
import skyfield.api
# local import

_lock = Lock()


def JNowToJ2000(ra, dec, timeJD):
    with _lock:
        ra = ra.radians
        dec = dec.radians

        ra = ERFA.anp(ra + ERFA.eo06a(timeJD.tt, 0.0))

        raConv, decConv, _ = ERFA.atic13(ra, dec, timeJD.ut1, 0.0)

        ra = skyfield.api.Angle(radians=raConv, preference='hours')
        dec = skyfield.api.Angle(radians=decConv, preference='degrees')
        return ra, dec


def J2000ToJNow(ra, dec, timeJD):
    with _lock:
        ra = ra.radians
        dec = dec.radians

        raConv, decConv, eo = ERFA.atci13(ra, dec, 0, 0, 0, 0, timeJD.ut1, 0)

        raConv = ERFA.anp(raConv - eo)
        ra = skyfield.api.Angle(radians=raConv, preference='hours')
        dec = skyfield.api.Angle(radians=decConv, preference='degrees')
        return ra, dec
