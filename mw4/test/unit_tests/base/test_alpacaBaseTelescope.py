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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock

# external packages
import pytest

# local import
from mw4.base.alpacaBase import Telescope


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = Telescope()
    yield
    del app


def test_alignmentmode():
    val = app.alignmentmode()
    assert val is None


def test_altitude():
    val = app.altitude()
    assert val is None


def test_aperturearea():
    val = app.aperturearea()
    assert val is None


def test_aperturediameter():
    val = app.aperturediameter()
    assert val is None


def test_athome():
    val = app.athome()
    assert val is None


def test_atpark():
    val = app.atpark()
    assert val is None


def test_azimuth():
    val = app.azimuth()
    assert val is None


def test_canfindhome():
    val = app.canfindhome()
    assert val is None


def test_canpark():
    val = app.canpark()
    assert val is None


def test_canpulseguide():
    val = app.canpulseguide()
    assert val is None


def test_cansetdeclinationrate():
    val = app.cansetdeclinationrate()
    assert val is None


def test_cansetguiderates():
    val = app.cansetguiderates()
    assert val is None


def test_cansetpark():
    val = app.cansetpark()
    assert val is None


def test_cansetpierside():
    val = app.cansetpierside()
    assert val is None


def test_cansetrightascensionrate():
    val = app.cansetrightascensionrate()
    assert val is None


def test_cansettracking():
    val = app.cansettracking()
    assert val is None


def test_canslew():
    val = app.canslew()
    assert val is None


def test_canslewaltaz():
    val = app.canslewaltaz()
    assert val is None


def test_canslewaltazasync():
    val = app.canslewaltazasync()
    assert val is None


def test_cansync():
    val = app.cansync()
    assert val is None


def test_cansyncaltaz():
    val = app.cansyncaltaz()
    assert val is None


def test_declination():
    val = app.declination()
    assert val is None


def test_declinationrate_1():
    val = app.declinationrate()
    assert val is None


def test_declinationrate_2():
    val = app.declinationrate(DeclinationRate=0)
    assert val is None


def test_doesrefraction_1():
    val = app.doesrefraction()
    assert val is None


def test_doesrefraction_2():
    val = app.doesrefraction(DoesRefraction=True)
    assert val is None


def test_equatorialsystem():
    val = app.equatorialsystem()
    assert val is None


def test_focallength():
    val = app.focallength()
    assert val is None


def test_guideratedeclination_1():
    val = app.guideratedeclination()
    assert val is None


def test_guideratedeclination_2():
    val = app.guideratedeclination(GuideRateDeclination=True)
    assert val is None


def test_guideraterightascension_1():
    val = app.guideraterightascension()
    assert val is None


def test_guideraterightascension_2():
    val = app.guideraterightascension(GuideRateRightAscension=True)
    assert val is None


def test_ispulseguiding():
    val = app.ispulseguiding()
    assert val is None


def test_rightascension():
    val = app.rightascension()
    assert val is None


def test_rightascensionrate_1():
    val = app.rightascensionrate()
    assert val is None


def test_rightascensionrate_2():
    val = app.rightascensionrate(RightAscensionRate=0)
    assert val is None


def test_sideofpier_1():
    val = app.sideofpier()
    assert val is None


def test_sideofpier_2():
    val = app.sideofpier(SideOfPier=0)
    assert val is None


def test_siderealtime():
    val = app.siderealtime()
    assert val is None


def test_siteelevation_1():
    val = app.siteelevation()
    assert val is None


def test_siteelevation_2():
    val = app.siteelevation(SiteElevation=0)
    assert val is None


def test_sitelatitude_1():
    val = app.sitelatitude()
    assert val is None


def test_sitelatitude_2():
    val = app.sitelatitude(SiteLatitude=0)
    assert val is None


def test_sitelongitude_1():
    val = app.sitelongitude()
    assert val is None


def test_sitelongitude_2():
    val = app.sitelongitude(SiteLongitude=0)
    assert val is None


def test_slewing():
    val = app.slewing()
    assert val is None


def test_slewsettletime_1():
    val = app.slewsettletime()
    assert val is None


def test_slewsettletime_2():
    val = app.slewsettletime(SlewSettleTime=0)
    assert val is None


def test_targetdeclination_1():
    val = app.targetdeclination()
    assert val is None


def test_targetdeclination_2():
    val = app.targetdeclination(TargetDeclination=0)
    assert val is None


def test_targetrightascension_1():
    val = app.targetrightascension()
    assert val is None


def test_targetrightascension_2():
    val = app.targetrightascension(TargetRightAscension=0)
    assert val is None


def test_tracking_1():
    val = app.tracking()
    assert val is None


def test_tracking_2():
    val = app.tracking(Tracking=0)
    assert val is None


def test_trackingrate_1():
    val = app.trackingrate()
    assert val is None


def test_trackingrate_2():
    val = app.trackingrate(TrackingRate=0)
    assert val is None


def test_trackingrates():
    val = app.trackingrates()
    assert val is None


def test_utcdate_2():
    val = app.utcdate(UTCDate=0)
    assert val is None


def test_abortslew():
    val = app.abortslew()
    assert val is None


def test_axisrates():
    val = app.axisrates(Axis=1)
    assert val is None


def test_canmoveaxis():
    val = app.canmoveaxis(Axis=1)
    assert val is None


def test_destinationsideofpier():
    val = app.destinationsideofpier(RightAscension=0, Declination=0)
    assert val is None


def test_findhome():
    val = app.findhome()
    assert val is None


def test_moveaxis():
    val = app.moveaxis(Axis=1, Rate=0)
    assert val is None


def test_park():
    val = app.park()
    assert val is None


def test_pulseguide():
    val = app.pulseguide(Direction=0, Duration=0)
    assert val is None


def test_setpark():
    val = app.setpark()
    assert val is None


def test_slewtoaltaz():
    val = app.slewtoaltaz(Azimuth=0, Altitude=0)
    assert val is None


def test_slewtoaltazasync():
    val = app.slewtoaltazasync(Azimuth=0, Altitude=0)
    assert val is None


def test_slewtocoordinates():
    val = app.slewtocoordinates(RightAscension=0, Declination=0)
    assert val is None


def test_slewtocoordinatesasync():
    val = app.slewtocoordinatesasync(RightAscension=0, Declination=0)
    assert val is None


def test_slewtotarget():
    val = app.slewtotarget()
    assert val is None


def test_slewtotargetasync():
    val = app.slewtotargetasync()
    assert val is None


def test_synctoaltaz():
    val = app.synctoaltaz(Azimuth=0, Altitude=0)
    assert val is None


def test_synctocoordinates():
    val = app.synctocoordinates(RightAscension=0, Declination=0)
    assert val is None


def test_synctotarget():
    val = app.synctotarget()
    assert val is None


def test_unpark():
    val = app.unpark()
    assert val is None

