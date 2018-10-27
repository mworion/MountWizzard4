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
import logging
import math
import datetime
from mw4.base import erfa


def JNowToJ2000(star, obsSite):
    raConv, decConv, eo = self.ERFA.eraAtic13(self.ERFA.eraAnp(ra + self.ERFA.eraEo06a(jdtt, 0.0)),
                                     dec,
                                     jd,
                                     0.0)

def J2000ToJNow(star, obsSite):
    jd, jdtt = prepare(obsSite)
    raConv, decConv, eo = self.ERFA.eraAtci13(ra,
                                              dec,
                                              0,
                                              0,
                                              0,
                                              0,
                                              jd,
                                              0)
    raConv = self.ERFA.eraAnp(raConv - eo)

