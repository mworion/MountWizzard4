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
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import pytest

# local import
from base.alpacaBase import Camera


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = Camera()

    yield


def test_bayeroffsetx():
    val = app.bayeroffsetx()
    assert val == []


def test_bayeroffsety():
    val = app.bayeroffsety()
    assert val == []


def test_binx_1():
    val = app.binx()
    assert val == []


def test_binx_2():
    val = app.binx(BinX=1)
    assert val == []


def test_biny_1():
    val = app.biny()
    assert val == []


def test_biny_2():
    val = app.biny(BinY=1)
    assert val == []


def test_camerastate():
    val = app.camerastate()
    assert val == []


def test_cameraxsize():
    val = app.cameraxsize()
    assert val == []


def test_cameraysize():
    val = app.cameraysize()
    assert val == []


def test_canabortexposure():
    val = app.canabortexposure()
    assert val == []


def test_canasymmetricbin():
    val = app.canasymmetricbin()
    assert val == []


def test_canfastreadout():
    val = app.canfastreadout()
    assert val == []


def test_cangetcoolerpower():
    val = app.cangetcoolerpower()
    assert val == []


def test_canpulseguide():
    val = app.canpulseguide()
    assert val == []


def test_cansetccdtemperature():
    val = app.cansetccdtemperature()
    assert val == []


def test_canstopexposure():
    val = app.canstopexposure()
    assert val == []


def test_ccdtemperature():
    val = app.ccdtemperature()
    assert val == []


def test_cooleron_1():
    val = app.cooleron()
    assert val == []


def test_cooleron_2():
    val = app.cooleron(CoolerOn=True)
    assert val == []


def test_coolerpower():
    val = app.coolerpower()
    assert val == []


def test_electronsperadu():
    val = app.electronsperadu()
    assert val == []


def test_exposuremax():
    val = app.exposuremax()
    assert val == []


def test_exposuremin():
    val = app.exposuremin()
    assert val == []


def test_exposureresolution():
    val = app.exposureresolution()
    assert val == []


def test_fastreadout_1():
    val = app.fastreadout()
    assert val == []


def test_fastreadout_2():
    val = app.fastreadout(FastReadout=True)
    assert val == []


def test_fullwellcapacity():
    val = app.fullwellcapacity()
    assert val == []


def test_gain_1():
    val = app.gain()
    assert val == []


def test_gain_2():
    val = app.gain(Gain=True)
    assert val == []


def test_gainmax():
    val = app.gainmax()
    assert val == []


def test_gainmin():
    val = app.gainmin()
    assert val == []


def test_gains():
    val = app.gains()
    assert val == []


def test_hasshutter():
    val = app.hasshutter()
    assert val == []


def test_heatsinktemperature():
    val = app.heatsinktemperature()
    assert val == []


def test_imagearray():
    val = app.imagearray()
    assert val == []


def test_imagearrayvariant():
    val = app.imagearrayvariant()
    assert val == []


def test_imageready():
    val = app.imageready()
    assert val == []


def test_ispulseguiding():
    val = app.ispulseguiding()
    assert val == []


def test_lastexposureduration():
    val = app.lastexposureduration()
    assert val == []


def test_lastexposurestarttime():
    val = app.lastexposurestarttime()
    assert val == []


def test_maxadu():
    val = app.maxadu()
    assert val == []


def test_maxbinx():
    val = app.maxbinx()
    assert val == []


def test_maxbiny():
    val = app.maxbiny()
    assert val == []


def test_numx_1():
    val = app.numx()
    assert val == []


def test_numx_2():
    val = app.numx(NumX=0)
    assert val == []


def test_numy_1():
    val = app.numy()
    assert val == []


def test_numy_2():
    val = app.numy(NumY=0)
    assert val == []


def test_percentcompleted():
    val = app.percentcompleted()
    assert val == []


def test_pixelsizex():
    val = app.pixelsizex()
    assert val == []


def test_pixelsizey():
    val = app.pixelsizey()
    assert val == []


def test_readoutmode_1():
    val = app.readoutmode()
    assert val == []


def test_readoutmode_2():
    val = app.readoutmode(ReadoutMode=0)
    assert val == []


def test_readoutmodes():
    val = app.readoutmodes()
    assert val == []


def test_sensorname():
    val = app.sensorname()
    assert val == []


def test_sensortype():
    val = app.sensortype()
    assert val == []


def test_setccdtemperature_1():
    val = app.setccdtemperature()
    assert val == []


def test_setccdtemperature_2():
    val = app.setccdtemperature(SetCCDTemperature=0)
    assert val == []


def test_startx_1():
    val = app.startx()
    assert val == []


def test_startx_2():
    val = app.startx(StartX=0)
    assert val == []


def test_starty_1():
    val = app.starty()
    assert val == []


def test_starty_2():
    val = app.starty(StartY=0)
    assert val == []


def test_abortexposure():
    val = app.abortexposure()
    assert val == []


def test_pulseguide():
    val = app.pulseguide(Direction=0, Duration=1)
    assert val == []


def test_startexposure():
    val = app.startexposure(Duration=1, Light=True)
    assert val == []


def test_stopexposure():
    val = app.stopexposure()
    assert val == []
