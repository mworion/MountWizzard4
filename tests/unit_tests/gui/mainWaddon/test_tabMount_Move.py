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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock

import pytest

# external packages
from PySide6.QtWidgets import QInputDialog, QWidget
from skyfield.api import Angle

import mw4.gui.mainWaddon.tabMount
from mw4.gui.mainWaddon.tabMount_Move import MountMove
from mw4.gui.widgets.main_ui import Ui_MainWindow

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = MountMove(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config["mainW"] = {}
    function.initConfig()


def test_initConfig_2(function):
    del function.app.config["mainW"]
    function.initConfig()


def test_storeConfig_1(function):
    function.app.config["mainW"] = {}
    function.storeConfig()


def test_setupGuiMount_1(function):
    function.setupGuiMount()


def test_stopMoveAll(function):
    with mock.patch.object(function.app.mount.obsSite, "stopMoveAll", return_value=True):
        function.stopMoveAll()


def test_countDuration_1(function):
    with mock.patch.object(mw4.gui.mainWaddon.tabMount_Move, "sleepAndEvents"):
        function.countDuration(10)


def test_moveDuration_1(function):
    function.ui.moveDuration.setCurrentIndex(1)
    with mock.patch.object(function, "countDuration"):
        with mock.patch.object(function, "stopMoveAll"):
            suc = function.moveDuration()
            assert suc


def test_moveDuration_2(function):
    function.ui.moveDuration.setCurrentIndex(2)
    with mock.patch.object(function, "countDuration"):
        with mock.patch.object(function, "stopMoveAll"):
            suc = function.moveDuration()
            assert suc


def test_moveDuration_3(function):
    function.ui.moveDuration.setCurrentIndex(3)
    with mock.patch.object(function, "countDuration"):
        with mock.patch.object(function, "stopMoveAll"):
            suc = function.moveDuration()
            assert suc


def test_moveDuration_4(function):
    function.ui.moveDuration.setCurrentIndex(4)
    with mock.patch.object(function, "countDuration"):
        with mock.patch.object(function, "stopMoveAll"):
            suc = function.moveDuration()
            assert suc


def test_moveDuration_5(function):
    function.ui.moveDuration.setCurrentIndex(0)
    with mock.patch.object(function, "countDuration"):
        suc = function.moveDuration()
        assert not suc


def test_moveClassicGameController_1(function):
    with mock.patch.object(function, "stopMoveAll"):
        function.moveClassicGameController(128, 128)


def test_moveClassicGameController_2(function):
    with mock.patch.object(function, "moveClassic"):
        function.moveClassicGameController(0, 0)


def test_moveClassicGameController_3(function):
    with mock.patch.object(function, "moveClassic"):
        function.moveClassicGameController(255, 255)


def test_moveClassic_1(function):
    with mock.patch.object(function, "moveDuration"):
        function.moveClassic("NE")


def test_moveClassic_2(function):
    with mock.patch.object(function, "moveDuration"):
        function.moveClassic("SW")


def test_moveClassic_3(function):
    with mock.patch.object(function, "moveDuration"):
        function.moveClassic("STOP")


def test_setSlewSpeed_1(function):
    function.setSlewSpeed("max")


def test_moveAltAzDefault(function):
    suc = function.moveAltAzDefault()
    assert suc


def test_moveAltAzGameController_1(function):
    with mock.patch.object(function, "moveAltAz"):
        suc = function.moveAltAzGameController(0)
        assert suc


def test_moveAltAzGameController_2(function):
    with mock.patch.object(function, "moveAltAz"):
        suc = function.moveAltAzGameController(2)
        assert suc


def test_moveAltAzGameController_3(function):
    with mock.patch.object(function, "moveAltAz"):
        suc = function.moveAltAzGameController(4)
        assert suc


def test_moveAltAzGameController_4(function):
    with mock.patch.object(function, "moveAltAz"):
        suc = function.moveAltAzGameController(6)
        assert suc


def test_moveAltAzGameController_5(function):
    with mock.patch.object(function, "moveAltAz"):
        suc = function.moveAltAzGameController(99)
        assert not suc


def test_moveAltAz_1(function):
    function.targetAlt = None
    function.targetAz = None
    function.app.mount.obsSite.Alt = None
    function.app.mount.obsSite.Az = Angle(degrees=10)

    with mock.patch.object(function, "slewTargetAltAz", return_value=False):
        suc = function.moveAltAz([1, 1])
        assert not suc


def test_moveAltAz_2(function):
    function.targetAlt = None
    function.targetAz = None
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=10)

    with mock.patch.object(function, "slewTargetAltAz", return_value=False):
        suc = function.moveAltAz("NE")
        assert not suc


def test_moveAltAz_3(function):
    function.targetAlt = 10
    function.targetAz = 10
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=10)

    with mock.patch.object(function, "slewTargetAltAz", return_value=True):
        suc = function.moveAltAz("NE")
        assert suc


def test_setRA_1(function):
    with mock.patch.object(QInputDialog, "getText", return_value=("", False)):
        suc = function.setRA()
        assert not suc


def test_setRA_2(function):
    with mock.patch.object(QInputDialog, "getText", return_value=("", True)):
        suc = function.setRA()
        assert not suc


def test_setRA_3(function):
    with mock.patch.object(QInputDialog, "getText", return_value=("12H", True)):
        suc = function.setRA()
        assert suc


def test_setDEC_1(function):
    with mock.patch.object(QInputDialog, "getText", return_value=("", False)):
        suc = function.setDEC()
        assert not suc


def test_setDEC_2(function):
    with mock.patch.object(QInputDialog, "getText", return_value=("", True)):
        suc = function.setDEC()
        assert not suc


def test_setDEC_3(function):
    with mock.patch.object(QInputDialog, "getText", return_value=("12", True)):
        suc = function.setDEC()
        assert suc


def test_moveAltAzAbsolute_1(function):
    function.ui.moveCoordinateAlt.setText("50h")
    function.ui.moveCoordinateAz.setText("50h")
    suc = function.moveAltAzAbsolute()
    assert not suc


def test_moveAltAzAbsolute_2(function):
    function.ui.moveCoordinateAlt.setText("50")
    function.ui.moveCoordinateAz.setText("50h")
    suc = function.moveAltAzAbsolute()
    assert not suc


def test_moveAltAzAbsolute_3(function):
    function.app.mount.setting.horizonLimitLow = 10
    function.app.mount.setting.horizonLimitHigh = 70
    function.ui.moveCoordinateAlt.setText("50")
    function.ui.moveCoordinateAz.setText("50")
    with mock.patch.object(function, "slewTargetAltAz", return_value=False):
        suc = function.moveAltAzAbsolute()
        assert not suc


def test_moveAltAzAbsolute_4(function):
    function.app.mount.setting.horizonLimitLow = 10
    function.app.mount.setting.horizonLimitHigh = 70
    function.ui.moveCoordinateAlt.setText("50")
    function.ui.moveCoordinateAz.setText("50")
    with mock.patch.object(function, "slewTargetAltAz", return_value=True):
        suc = function.moveAltAzAbsolute()
        assert suc


def test_moveRaDecAbsolute_1(function):
    function.ui.moveCoordinateRa.setText("asd")
    function.ui.moveCoordinateDec.setText("asd")
    suc = function.moveRaDecAbsolute()
    assert not suc


def test_moveRaDecAbsolute_2(function):
    function.ui.moveCoordinateRa.setText("12H")
    function.ui.moveCoordinateDec.setText("asd")
    suc = function.moveRaDecAbsolute()
    assert not suc


def test_moveRaDecAbsolute_3(function):
    function.ui.moveCoordinateRa.setText("12H")
    function.ui.moveCoordinateDec.setText("30 30")
    with mock.patch.object(function, "slewTargetRaDec", return_value=False):
        suc = function.moveRaDecAbsolute()
        assert not suc


def test_moveRaDecAbsolute_4(function):
    function.ui.moveCoordinateRa.setText("12H")
    function.ui.moveCoordinateDec.setText("30 30")
    with mock.patch.object(function, "slewTargetRaDec", return_value=True):
        suc = function.moveRaDecAbsolute()
        assert suc
