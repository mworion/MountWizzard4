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
import platform
import pytest
import unittest.mock as mock

if platform.system() != "Windows":
    pytest.skip("skipping windows-only tests", allow_module_level=True)

from mw4.base.ascomClass import AscomClass
from mw4.base.loggerMW import setupLogging
from mw4.logic.camera.camera import Camera
from mw4.logic.camera.cameraAlpacaAscomBase import CameraAlpacaAscomBase
from mw4.logic.camera.cameraAscom import CameraAscom
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()


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
    func = CameraAscom(camera)
    func.device = mock.MagicMock()
    yield func


def test_cameraAscom_inheritsFromBase(function):
    assert isinstance(function, CameraAlpacaAscomBase)


def test_cameraAscom_inheritsFromAscomClass(function):
    assert isinstance(function, AscomClass)


def test_cameraAscom_instantiation(function):
    assert function is not None
