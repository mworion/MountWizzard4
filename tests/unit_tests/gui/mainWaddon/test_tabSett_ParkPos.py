############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock

import pytest
from gui.mainWaddon.tabSett_ParkPos import SettParkPos
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow

# external packages
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = SettParkPos(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config["mainW"] = {}
    function.initConfig()


def test_initConfig_2(function):
    function.initConfig()


def test_initConfig_3(function):
    config = function.app.config["mainW"]
    for i in range(0, 10):
        config[f"posText{i:1d}"] = str(i)
        config[f"posAlt{i:1d}"] = i
        config[f"posAz{i:1d}"] = i
    function.initConfig()
    assert function.ui.posText0.text() == "0"
    assert function.ui.posAlt0.value() == 0
    assert function.ui.posAz0.value() == 0
    assert function.ui.posText4.text() == "4"
    assert function.ui.posAlt4.value() == 4
    assert function.ui.posAz4.value() == 4
    assert function.ui.posText7.text() == "7"
    assert function.ui.posAlt7.value() == 7
    assert function.ui.posAz7.value() == 7


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_setupParkPosGui(function):
    assert len(function.posButtons) == 10
    assert len(function.posTexts) == 10
    assert len(function.posAlt) == 10
    assert len(function.posAz) == 10
    assert len(function.posSaveButtons) == 10


def test_parkAtPos_1(function):
    function.app.mount.signals.slewed.connect(function.parkAtPos)
    with mock.patch.object(
        function.app.mount.obsSite, "parkOnActualPosition", return_value=False
    ):
        function.parkAtPos()


def test_parkAtPos_2(function):
    function.app.mount.signals.slewed.connect(function.parkAtPos)
    with mock.patch.object(
        function.app.mount.obsSite, "parkOnActualPosition", return_value=True
    ):
        function.parkAtPos()


def test_slewParkPos_2(function):
    with mock.patch.object(function.app.mount.obsSite, "setTargetAltAz", return_value=False):
        function.slewToParkPos(0)


def test_slewParkPos_3(function):
    with mock.patch.object(function.app.mount.obsSite, "setTargetAltAz", return_value=True):
        with mock.patch.object(function.app.mount.obsSite, "startSlewing", return_value=False):
            function.slewToParkPos(0)


def test_slewParkPos_4(function):
    function.ui.parkMountAfterSlew.setChecked(True)
    with mock.patch.object(function.app.mount.obsSite, "setTargetAltAz", return_value=True):
        with mock.patch.object(function.app.mount.obsSite, "startSlewing", return_value=True):
            function.slewToParkPos(0)


def test_slewParkPos_5(function):
    function.ui.parkMountAfterSlew.setChecked(False)
    with mock.patch.object(function.app.mount.obsSite, "setTargetAltAz", return_value=True):
        with mock.patch.object(function.app.mount.obsSite, "startSlewing", return_value=True):
            function.slewToParkPos(0)


def test_saveActualPosition_1(function):
    function.app.mount.obsSite.Az = Angle(degrees=10)
    function.app.mount.obsSite.Alt = None

    function.saveActualPosition(0)


def test_saveActualPosition_2(function):
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = None

    function.saveActualPosition(0)


def test_saveActualPosition_3(function):
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=10)
    function.saveActualPosition(0)
