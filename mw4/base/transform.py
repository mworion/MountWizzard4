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


def JNowToJ2000(ra, dec, timeJD):
    with _lock:
        jd = timeJD.tai
        jdtt = timeJD.tt
        ra = ra.radians
        dec = dec.radians
        print(ra, dec)
        ra = ERFA.anp(ra + ERFA.eo06a(jdtt, 0.0))
        raConv, decConv, _ = ERFA.atic13(ra,
                                         dec,
                                         jd,
                                         0.0)
        ra = skyfield.api.Angle(radians=raConv)
        dec = skyfield.api.Angle(radians=decConv)
        return ra, dec


def J2000ToJNow(ra, dec, timeJD):
    with _lock:
        jd = timeJD.tai
        ra = ra.radians
        dec = dec.radians
        raConv, decConv, eo = ERFA.atci13(ra,
                                          dec,
                                          0,
                                          0,
                                          0,
                                          0,
                                          jd,
                                          0)
        raConv = ERFA.anp(raConv - eo)
        ra = skyfield.api.Angle(radians=raConv)
        dec = skyfield.api.Angle(radians=decConv)
        return ra, dec

