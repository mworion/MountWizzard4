############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import pytest
import unittest.mock as mock
from mw4.base.alpacaClass import AlpacaClass
from mw4.logic.camera.camera import Camera
from mw4.logic.camera.cameraAlpaca import CameraAlpaca
from mw4.logic.camera.cameraAlpacaAscomBase import CameraAlpacaAscomBase
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    camera = Camera(App())
    camera.exposureTime = 1
    camera.binning = 1
    camera.focalLength = 1
    camera.posXASCOM = 0
    camera.posYASCOM = 0
    camera.widthASCOM = 100
    camera.heightASCOM = 100
    camera.fastReadout = False
    camera.imagePath = "/tmp/test.fits"
    func = CameraAlpaca(camera)
    func.device = mock.MagicMock()
    yield func


def test_cameraAlpaca_inheritsFromBase(function):
    assert isinstance(function, CameraAlpacaAscomBase)


def test_cameraAlpaca_inheritsFromAlpacaClass(function):
    assert isinstance(function, AlpacaClass)


def test_cameraAlpaca_instantiation(function):
    assert function is not None
