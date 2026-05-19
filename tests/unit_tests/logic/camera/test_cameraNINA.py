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
from mw4.base.signalsDevices import Signals
from mw4.base.tpool import Worker
from mw4.logic.camera.camera import Camera
from mw4.logic.camera.cameraNINA import CameraNINA
from mw4.logic.camera.cameraSgproNinaBase import CameraSgproNinaBase
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Parent:
    app = App()
    data = {}
    signals = Signals()
    loadConfig = True
    updateRate = 1000
    binning = 1
    exposureTime = 1
    imagePath = "tests/work/image/test.fit"
    width = 100
    height = 100
    subframe = 100
    posX = 0
    posY = 0
    threadPool = mock.Mock()
    exposeFinished = mock.Mock()
    waitStart = mock.Mock()
    waitExposed = mock.Mock()
    waitDownload = mock.Mock()
    waitSave = mock.Mock()
    waitFinish = mock.Mock()
    updateImageFitsHeaderPointing = mock.Mock()


@pytest.fixture(autouse=True, scope="module")
def function():
    camera = Camera(App())
    camera.exposureTime = 1
    camera.binning = 1
    camera.focalLength = 1
    func = CameraNINA(parent=Parent())
    yield func


def test_init(function):
    assert isinstance(function, CameraNINA)
    assert isinstance(function, CameraSgproNinaBase)
    assert function.worker is None or isinstance(function.worker, Worker)
    assert function.threadPool is Parent.threadPool
