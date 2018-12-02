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
# GUI with PyQT5 for python
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
from skyfield import api
from astropy import _erfa as ERFA
# local import
from mw4.base import transform


def test_J2000toJNow():
    ts = api.load.timescale()
    barnard = api.Star(ra_hours=(17, 57, 48.49803),
                       dec_degrees=(4, 41, 36.2072),
                       )
    planets = api.load('de421.bsp')
    earth = planets['earth']

    print()
    for jd in range(2458240, 2459240, 100):

        timeTopo = ts.ut1_jd(jd)
        timeTopoTT = ts.tt_jd(jd)
        astrometric = earth.at(timeTopo).observe(barnard).apparent()
        astrometricTT = earth.at(timeTopoTT).observe(barnard).apparent()
        raJNow = barnard.ra
        decJNow = barnard.dec

        raERFA, decERFA = transform.J2000ToJNow(raJNow, decJNow, timeTopo)
        raSKY, decSKY, dist = astrometricTT.radec(epoch=timeTopoTT)
        raSKYTT, decSKYTT, dist = astrometric.radec(epoch=timeTopo)

        raSKYTT = raSKYTT.hours
        decSKYTT = decSKYTT.degrees
        raSKY = raSKY.hours
        decSKY = decSKY.degrees
        raERFA = raERFA.hours
        decERFA = decERFA.degrees

        d_ra_tt = abs(raSKY - raSKYTT) * 3600
        d_dec_tt = abs(decSKY - decSKYTT) * 3600
        d_ra_ERFA = abs(raSKYTT - raERFA) * 3600
        d_dec_ERFA = abs(decSKYTT - decERFA) * 3600
        d_ra = abs(raSKY - raERFA) * 3600
        d_dec = abs(decSKY - decERFA) * 3600

        print('delta : ra:{0:8.8f} {1:8.8f} {2:8.8f}  dec:{3:8.8f} {4:8.8f} {5:8.8f}'
              .format(d_ra_tt, d_ra_ERFA, d_ra, d_dec_tt, d_dec_ERFA, d_dec))


def test_time():
    ts = api.load.timescale()

    print()
    for jd in range(2458240, 2459240, 100):

        timeJD = ts.ut1_jd(jd)
        # print(timeJD.dut1)

        tai1, tai2 = ERFA.utctai(jd, 0)
        tt1, tt2 = ERFA.taitt(tai1, tai2)
        jdtt = tt1 + tt2

        d_t = abs(jdtt - timeJD.tt - timeJD.dut1 / 86400) * 86400

        print('{0:10.4f}'.format(d_t))

