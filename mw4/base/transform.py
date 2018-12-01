############################################################
# -*- coding: utf-8 -*-
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.5
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


def prepare(jd):
    tai1, tai2 = ERFA.utctai(jd, 0)
    tt1, tt2 = ERFA.taitt(tai1, tai2)
    jdtt = tt1 + tt2
    return jdtt


def JNowToJ2000(ra, dec, jd):
    with _lock():
        jdtt = prepare(jd)
        ra = ra.degrees
        dec = dec.degrees
        ra = ERFA.eraAnp(ra + ERFA.eraEo06a(jdtt, 0.0))
        raConv, decConv, _ = ERFA.eraAtic13(ra,
                                            dec,
                                            jd,
                                            0.0)
        ra = skyfield.api.Angle(degrees=raConv)
        dec = skyfield.api.Angle(degrees=decConv)
        return ra, dec


def J2000ToJNow(ra, dec, jd):
    with _lock():
        ra = ra.degrees
        dec = dec.degrees
        raConv, decConv, eo = ERFA.eraAtci13(ra,
                                             dec,
                                             0,
                                             0,
                                             0,
                                             0,
                                             jd,
                                             0)
        raConv = ERFA.eraAnp(raConv - eo)
        ra = skyfield.api.Angle(degrees=raConv)
        dec = skyfield.api.Angle(degrees=decConv)
        return ra, dec

