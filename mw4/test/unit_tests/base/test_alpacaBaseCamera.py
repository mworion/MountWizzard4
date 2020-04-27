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

# external packages
import pytest

# local import
from mw4.base.alpacaBase import Camera


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = Camera()

    yield


def test_bayeroffsetx():
    val = app.bayeroffsetx()
    assert val is None


def test_bayeroffsety():
    val = app.bayeroffsety()
    assert val is None


def test_binx_1():
    val = app.binx()
    assert val is None


def test_binx_2():
    val = app.binx(BinX=1)
    assert val is None


def test_biny_1():
    val = app.biny()
    assert val is None


def test_biny_2():
    val = app.biny(BinY=1)
    assert val is None


def test_camerastate():
    val = app.camerastate()
    assert val is None


def test_cameraxsize():
    val = app.cameraxsize()
    assert val is None


def test_cameraysize():
    val = app.cameraysize()
    assert val is None


def test_canabortexposure():
    val = app.canabortexposure()
    assert val is None


def test_canasymmetricbin():
    val = app.canasymmetricbin()
    assert val is None


def test_canfastreadout():
    val = app.canfastreadout()
    assert val is None


def test_cangetcoolerpower():
    val = app.cangetcoolerpower()
    assert val is None


def test_canpulseguide():
    val = app.canpulseguide()
    assert val is None


def test_cansetccdtemperature():
    val = app.cansetccdtemperature()
    assert val is None


def test_canstopexposure():
    val = app.canstopexposure()
    assert val is None


def test_ccdtemperature():
    val = app.ccdtemperature()
    assert val is None


def test_cooleron_1():
    val = app.cooleron()
    assert val is None


def test_cooleron_2():
    val = app.cooleron(CoolerOn=True)
    assert val is None


def test_coolerpower():
    val = app.coolerpower()
    assert val is None


def test_electronsperadu():
    val = app.electronsperadu()
    assert val is None


def test_exposuremax():
    val = app.exposuremax()
    assert val is None


def test_exposuremin():
    val = app.exposuremin()
    assert val is None


def test_exposureresolution():
    val = app.exposureresolution()
    assert val is None


def test_fastreadout_1():
    val = app.fastreadout()
    assert val is None


def test_fastreadout_2():
    val = app.fastreadout(FastReadout=True)
    assert val is None


def test_fullwellcapacity():
    val = app.fullwellcapacity()
    assert val is None


def test_gain_1():
    val = app.gain()
    assert val is None


def test_gain_2():
    val = app.gain(Gain=True)
    assert val is None


def test_gainmax():
    val = app.gainmax()
    assert val is None


def test_gainmin():
    val = app.gainmin()
    assert val is None


def test_gains():
    val = app.gains()
    assert val is None


def test_hasshutter():
    val = app.hasshutter()
    assert val is None


def test_heatsinktemperature():
    val = app.heatsinktemperature()
    assert val is None


def test_imagearray():
    val = app.imagearray()
    assert val is None


def test_imagearrayvariant():
    val = app.imagearrayvariant()
    assert val is None


def test_imageready():
    val = app.imageready()
    assert val is None


def test_ispulseguiding():
    val = app.ispulseguiding()
    assert val is None


def test_lastexposureduration():
    val = app.lastexposureduration()
    assert val is None


def test_lastexposurestarttime():
    val = app.lastexposurestarttime()
    assert val is None


def test_maxadu():
    val = app.maxadu()
    assert val is None


def test_maxbinx():
    val = app.maxbinx()
    assert val is None


def test_maxbiny():
    val = app.maxbiny()
    assert val is None


def test_numx_1():
    val = app.numx()
    assert val is None


def test_numx_2():
    val = app.numx(NumX=0)
    assert val is None


def test_numy_1():
    val = app.numy()
    assert val is None


def test_numy_2():
    val = app.numy(NumY=0)
    assert val is None


def test_percentcompleted():
    val = app.percentcompleted()
    assert val is None


def test_pixelsizex():
    val = app.pixelsizex()
    assert val is None


def test_pixelsizey():
    val = app.pixelsizey()
    assert val is None


def test_readoutmode_1():
    val = app.readoutmode()
    assert val is None


def test_readoutmode_2():
    val = app.readoutmode(ReadoutMode=0)
    assert val is None


def test_readoutmodes():
    val = app.readoutmodes()
    assert val is None


def test_sensorname():
    val = app.sensorname()
    assert val is None


def test_sensortype():
    val = app.sensortype()
    assert val is None


def test_setccdtemperature_1():
    val = app.setccdtemperature()
    assert val is None


def test_setccdtemperature_2():
    val = app.setccdtemperature(SetCCDTemperature=0)
    assert val is None


def test_startx_1():
    val = app.startx()
    assert val is None


def test_startx_2():
    val = app.startx(StartX=0)
    assert val is None


def test_starty_1():
    val = app.starty()
    assert val is None


def test_starty_2():
    val = app.starty(StartY=0)
    assert val is None


def test_abortexposure():
    val = app.abortexposure()
    assert val is None


def test_pulseguide():
    val = app.pulseguide(Direction=0, Duration=1)
    assert val is None


def test_startexposure():
    val = app.startexposure(Duration=1, Light=True)
    assert val is None


def test_stopexposure():
    val = app.stopexposure()
    assert val is None
