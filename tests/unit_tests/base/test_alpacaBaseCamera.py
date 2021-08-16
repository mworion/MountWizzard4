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
    val is None


def test_bayeroffsety():
    val = app.bayeroffsety()
    val is None


def test_binx_1():
    val = app.binx()
    val is None


def test_binx_2():
    val = app.binx(BinX=1)
    val is None


def test_biny_1():
    val = app.biny()
    val is None


def test_biny_2():
    val = app.biny(BinY=1)
    val is None


def test_camerastate():
    val = app.camerastate()
    val is None


def test_cameraxsize():
    val = app.cameraxsize()
    val is None


def test_cameraysize():
    val = app.cameraysize()
    val is None


def test_canabortexposure():
    val = app.canabortexposure()
    val is None


def test_canasymmetricbin():
    val = app.canasymmetricbin()
    val is None


def test_canfastreadout():
    val = app.canfastreadout()
    val is None


def test_cangetcoolerpower():
    val = app.cangetcoolerpower()
    val is None


def test_canpulseguide():
    val = app.canpulseguide()
    val is None


def test_cansetccdtemperature():
    val = app.cansetccdtemperature()
    val is None


def test_canstopexposure():
    val = app.canstopexposure()
    val is None


def test_ccdtemperature():
    val = app.ccdtemperature()
    val is None


def test_cooleron_1():
    val = app.cooleron()
    val is None


def test_cooleron_2():
    val = app.cooleron(CoolerOn=True)
    val is None


def test_coolerpower():
    val = app.coolerpower()
    val is None


def test_electronsperadu():
    val = app.electronsperadu()
    val is None


def test_exposuremax():
    val = app.exposuremax()
    val is None


def test_exposuremin():
    val = app.exposuremin()
    val is None


def test_exposureresolution():
    val = app.exposureresolution()
    val is None


def test_fastreadout_1():
    val = app.fastreadout()
    val is None


def test_fastreadout_2():
    val = app.fastreadout(FastReadout=True)
    val is None


def test_fullwellcapacity():
    val = app.fullwellcapacity()
    val is None


def test_gain_1():
    val = app.gain()
    val is None


def test_gain_2():
    val = app.gain(Gain=True)
    val is None


def test_gainmax():
    val = app.gainmax()
    val is None


def test_gainmin():
    val = app.gainmin()
    val is None


def test_gains():
    val = app.gains()
    val is None


def test_hasshutter():
    val = app.hasshutter()
    val is None


def test_heatsinktemperature():
    val = app.heatsinktemperature()
    val is None


def test_imagearray():
    val = app.imagearray()
    val is None


def test_imagearrayvariant():
    val = app.imagearrayvariant()
    val is None


def test_imageready():
    val = app.imageready()
    val is None


def test_ispulseguiding():
    val = app.ispulseguiding()
    val is None


def test_lastexposureduration():
    val = app.lastexposureduration()
    val is None


def test_lastexposurestarttime():
    val = app.lastexposurestarttime()
    val is None


def test_maxadu():
    val = app.maxadu()
    val is None


def test_maxbinx():
    val = app.maxbinx()
    val is None


def test_maxbiny():
    val = app.maxbiny()
    val is None


def test_numx_1():
    val = app.numx()
    val is None


def test_numx_2():
    val = app.numx(NumX=0)
    val is None


def test_numy_1():
    val = app.numy()
    val is None


def test_numy_2():
    val = app.numy(NumY=0)
    val is None


def test_percentcompleted():
    val = app.percentcompleted()
    val is None


def test_pixelsizex():
    val = app.pixelsizex()
    val is None


def test_pixelsizey():
    val = app.pixelsizey()
    val is None


def test_readoutmode_1():
    val = app.readoutmode()
    val is None


def test_readoutmode_2():
    val = app.readoutmode(ReadoutMode=0)
    val is None


def test_readoutmodes():
    val = app.readoutmodes()
    val is None


def test_sensorname():
    val = app.sensorname()
    val is None


def test_sensortype():
    val = app.sensortype()
    val is None


def test_setccdtemperature_1():
    val = app.setccdtemperature()
    val is None


def test_setccdtemperature_2():
    val = app.setccdtemperature(SetCCDTemperature=0)
    val is None


def test_startx_1():
    val = app.startx()
    val is None


def test_startx_2():
    val = app.startx(StartX=0)
    val is None


def test_starty_1():
    val = app.starty()
    val is None


def test_starty_2():
    val = app.starty(StartY=0)
    val is None


def test_abortexposure():
    val = app.abortexposure()
    val is None


def test_pulseguide():
    val = app.pulseguide(Direction=0, Duration=1)
    val is None


def test_startexposure():
    val = app.startexposure(Duration=1, Light=True)
    val is None


def test_stopexposure():
    val = app.stopexposure()
    val is None
