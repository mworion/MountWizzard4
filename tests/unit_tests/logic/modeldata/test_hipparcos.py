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
#
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages
from skyfield.api import wgs84
from mountcontrol.mount import Mount

# local import
from logic.modeldata.hipparcos import Hipparcos


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test():
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=20,
                                              longitude_degrees=10,
                                              elevation_m=500)

    global app
    app = Hipparcos(app=Test())

    yield


def test_data_available():
    assert len(app.alignStars) > 0


def test_calculateAlignStarPositionsAltAz_1():
    star = dict()
    star['Achernar'] = [0.42636313743386084, -0.9989721040992605, 4.267359632399454e-07,
                        -1.9431237114262957e-07, 0.022680000001570513, 4.512483521476569e-05]
    app.alignStars = star

    app.calculateAlignStarPositionsAltAz()
    assert ['Achernar'] == app.name


def test_calculateAlignStarPositionsAltAz_2():
    star = dict()
    star['Achernar'] = [0.42636313743386084, -0.9989721040992605, 4.267359632399454e-07,
                        -1.9431237114262957e-07, 0.022680000001570513, 4.512483521476569e-05]
    star['Acrux'] = [3.257647500944081, -1.1012877251083137, -1.7147915360582993e-07,
                     -7.141291885025191e-08, 0.010169999999992536, 0.00018371089505169385]
    app.alignStars = star

    app.calculateAlignStarPositionsAltAz()
    assert ['Achernar', 'Acrux'] == app.name


def test_calculateAlignStarPositionsAltAz_3():
    star = dict()
    star['Achernar'] = [0.42636313743386084, -0.9989721040992605, 4.267359632399454e-07,
                        -1.9431237114262957e-07, 0.022680000001570513, 4.512483521476569e-05]
    star['Acrux'] = [3.257647500944081, -1.1012877251083137, -1.7147915360582993e-07,
                     -7.141291885025191e-08, 0.010169999999992536, 0.00018371089505169385]
    app.alignStars = star
    app.app.mount.obsSite.location = None
    suc = app.calculateAlignStarPositionsAltAz()
    assert not suc


def test_getAlignStarRaDecFromName_1():
    star = dict()
    star['Achernar'] = [0.42636313743386084, -0.9989721040992605, 4.267359632399454e-07,
                        -1.9431237114262957e-07, 0.022680000001570513, 4.512483521476569e-05]
    star['Acrux'] = [3.257647500944081, -1.1012877251083137, -1.7147915360582993e-07,
                     -7.141291885025191e-08, 0.010169999999992536, 0.00018371089505169385]
    app.alignStars = star
    ra, dec = app.getAlignStarRaDecFromName('Achernar')
    assert ra is not None
    assert dec is not None


def test_getAlignStarRaDecFromName_2():
    star = dict()
    star['Achernar'] = [0.42636313743386084, -0.9989721040992605, 4.267359632399454e-07,
                        -1.9431237114262957e-07, 0.022680000001570513, 4.512483521476569e-05]
    star['Acrux'] = [3.257647500944081, -1.1012877251083137, -1.7147915360582993e-07,
                     -7.141291885025191e-08, 0.010169999999992536, 0.00018371089505169385]
    app.alignStars = star
    ra, dec = app.getAlignStarRaDecFromName('Test')
    assert ra is None
    assert dec is None
