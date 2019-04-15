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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
import PyQt5
from skyfield import api
from astropy import _erfa as ERFA
# local import
from mw4 import mainApp
from mw4.base import transform

test = PyQt5.QtWidgets.QApplication([])


mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config',
          'dataDir': './mw4/test/data',
          'modeldata': 'test',
          }
config = mwGlob['configDir']

app = mainApp.MountWizzard4(mwGlob=mwGlob)


def test_J2000toJNow():
    load = api.Loader(mwGlob['configDir'],
                      verbose=True,
                      expire=True,
                      )
    ts = load.timescale()
    barnard = api.Star(ra_hours=(17, 57, 48.49803),
                       dec_degrees=(4, 41, 36.2072),
                       )
    planets = load('de421.bsp')
    earth = planets['earth']

    print()
    for jd in range(2458240, 2459240, 100):

        timeTopo = ts.ut1_jd(jd)
        astrometric = earth.at(timeTopo).observe(barnard).apparent()
        raJNow = barnard.ra
        decJNow = barnard.dec

        raERFA, decERFA = transform.J2000ToJNow(raJNow, decJNow, timeTopo)
        raSKY, decSKY, dist = astrometric.radec(epoch=timeTopo)

        raSKY = raSKY.hours
        decSKY = decSKY.degrees
        raERFA = raERFA.hours
        decERFA = decERFA.degrees

        d_ra = abs(raSKY - raERFA) * 3600
        d_dec = abs(decSKY - decERFA) * 3600

        print('delta : ra:{0:8.8f} dec:{1:8.8f}'.format(d_ra, d_dec))


def test_JNowToJ2000():
    load = api.Loader(mwGlob['configDir'],
                      verbose=True,
                      expire=True,
                      )
    ts = load.timescale()
    barnard = api.Star(ra_hours=(17, 57, 48.49803),
                       dec_degrees=(4, 41, 36.2072),
                       )
    planets = load('de421.bsp')
    earth = planets['earth']

    print()
    for jd in range(2458240, 2459240, 100):

        timeTopo = ts.ut1_jd(jd)
        raJNow = barnard.ra
        decJNow = barnard.dec
        raJNow, decJNow = transform.J2000ToJNow(raJNow, decJNow, timeTopo)

        barnard_JNow = api.Star(ra=raJNow, dec=decJNow, epoch=timeTopo)
        astrometricJNow = earth.at(ts.ut1_jd(2451545)).observe(barnard_JNow)
        raJ2000, decJ2000, dist = barnard_JNow.cirs_radec(epoch=2451545.0)

        raJ2000 = raJ2000.hours
        decJ2000 = decJ2000.degrees
        raRef = barnard.ra.hours
        decRef = barnard.dec.degrees

        d_ra = abs(raJ2000 - raRef) * 3600
        d_dec = abs(decJ2000 - decRef) * 3600

        print('delta : ra:{0:8.8f} dec:{1:8.8f}'.format(d_ra, d_dec))


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
