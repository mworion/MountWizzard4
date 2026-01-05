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
# Licence APL2.0
#
###########################################################

import mw4.gui.mainWaddon.tabMount
import pytest
import unittest.mock as mock
from mw4.gui.mainWaddon.tabMount_Move import MountMove
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QInputDialog, QWidget
from skyfield.api import Angle
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
            function.moveDuration()


def test_moveDuration_2(function):
    function.ui.moveDuration.setCurrentIndex(2)
    with mock.patch.object(function, "countDuration"):
        with mock.patch.object(function, "stopMoveAll"):
            function.moveDuration()


def test_moveDuration_3(function):
    function.ui.moveDuration.setCurrentIndex(3)
    with mock.patch.object(function, "countDuration"):
        with mock.patch.object(function, "stopMoveAll"):
            function.moveDuration()


def test_moveDuration_4(function):
    function.ui.moveDuration.setCurrentIndex(4)
    with mock.patch.object(function, "countDuration"):
        with mock.patch.object(function, "stopMoveAll"):
            function.moveDuration()


def test_moveDuration_5(function):
    function.ui.moveDuration.setCurrentIndex(0)
    with mock.patch.object(function, "countDuration"):
        function.moveDuration()


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
    function.moveAltAzDefault()


def test_moveAltAzGameController_1(function):
    with mock.patch.object(function, "moveAltAz"):
        function.moveAltAzGameController(0)


def test_moveAltAzGameController_2(function):
    with mock.patch.object(function, "moveAltAz"):
        function.moveAltAzGameController(2)


def test_moveAltAzGameController_3(function):
    with mock.patch.object(function, "moveAltAz"):
        function.moveAltAzGameController(4)


def test_moveAltAzGameController_4(function):
    with mock.patch.object(function, "moveAltAz"):
        function.moveAltAzGameController(6)


def test_moveAltAzGameController_5(function):
    with mock.patch.object(function, "moveAltAz"):
        function.moveAltAzGameController(99)


def test_moveAltAz_3(function):
    function.targetAlt = Angle(degrees=10)
    function.targetAz = Angle(degrees=10)
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=10)

    with mock.patch.object(function.slewInterface, "slewTargetAltAz", return_value=True):
        function.moveAltAz("NE")


def test_setRA_1(function):
    with mock.patch.object(QInputDialog, "getText", return_value=("", False)):
        function.setRA()


def test_setRA_2(function):
    with mock.patch.object(QInputDialog, "getText", return_value=("", True)):
        function.setRA()


def test_setRA_3(function):
    with mock.patch.object(QInputDialog, "getText", return_value=("12H", True)):
        function.setRA()


def test_setDEC_1(function):
    with mock.patch.object(QInputDialog, "getText", return_value=("", False)):
        function.setDEC()


def test_setDEC_2(function):
    with mock.patch.object(QInputDialog, "getText", return_value=("", True)):
        function.setDEC()


def test_setDEC_3(function):
    with mock.patch.object(QInputDialog, "getText", return_value=("12", True)):
        function.setDEC()


def test_moveAltAzAbsolute_1(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=0)
    function.app.mount.obsSite.AzTarget = Angle(degrees=0)
    function.ui.moveCoordinateAlt.setText("50h")
    function.ui.moveCoordinateAz.setText("50h")
    function.moveAltAzAbsolute()


def test_moveAltAzAbsolute_2(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=0)
    function.app.mount.obsSite.AzTarget = Angle(degrees=0)
    function.ui.moveCoordinateAlt.setText("50")
    function.ui.moveCoordinateAz.setText("50h")
    function.moveAltAzAbsolute()


def test_moveAltAzAbsolute_3(function):
    function.app.mount.setting.horizonLimitLow = 10
    function.app.mount.setting.horizonLimitHigh = 70
    function.ui.moveCoordinateAlt.setText("50")
    function.ui.moveCoordinateAz.setText("50")
    with mock.patch.object(function.slewInterface, "slewTargetAltAz", return_value=False):
        function.moveAltAzAbsolute()


def test_moveAltAzAbsolute_4(function):
    function.app.mount.setting.horizonLimitLow = 10
    function.app.mount.setting.horizonLimitHigh = 70
    function.ui.moveCoordinateAlt.setText("50")
    function.ui.moveCoordinateAz.setText("50")
    with mock.patch.object(function.slewInterface, "slewTargetAltAz", return_value=True):
        function.moveAltAzAbsolute()


def test_moveRaDecAbsolute_1(function):
    function.app.mount.obsSite.haJNowTarget = Angle(degrees=0)
    function.app.mount.obsSite.decJNowTarget = Angle(degrees=0)
    function.ui.moveCoordinateRa.setText("asd")
    function.ui.moveCoordinateDec.setText("asd")
    function.moveRaDecAbsolute()


def test_moveRaDecAbsolute_2(function):
    function.app.mount.obsSite.haJNowTarget = Angle(degrees=0)
    function.app.mount.obsSite.decJNowTarget = Angle(degrees=0)
    function.ui.moveCoordinateRa.setText("12H")
    function.ui.moveCoordinateDec.setText("asd")
    function.moveRaDecAbsolute()


def test_moveRaDecAbsolute_3(function):
    function.ui.moveCoordinateRa.setText("12H")
    function.ui.moveCoordinateDec.setText("30 30")
    with mock.patch.object(function.slewInterface, "slewTargetRaDec", return_value=False):
        function.moveRaDecAbsolute()


def test_moveRaDecAbsolute_4(function):
    function.ui.moveCoordinateRa.setText("12H")
    function.ui.moveCoordinateDec.setText("30 30")
    with mock.patch.object(function.slewInterface, "slewTargetRaDec", return_value=True):
        function.moveRaDecAbsolute()
