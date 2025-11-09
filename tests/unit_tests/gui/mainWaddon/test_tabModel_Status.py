############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide !

#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock

import pytest

# external packages
from PySide6.QtGui import QPixmap

from mw4.gui.mainWaddon.tabModel_Status import ModelStatus
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = ModelStatus(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_setupIcons(function):
    pm = QPixmap()
    with mock.patch.object(MWidget, "img2pixmap", return_value=pm):
        function.setupIcons()


def test_updateAlignGui_numberStars(function):
    function.app.mount.model.starList = []
    function.app.mount.model.numberStars = 1
    function.updateAlignGUI(function.app.mount.model)
    assert function.ui.numberStars.text() == " 1"
    assert function.ui.numberStars1.text() == " 1"


def test_updateAlignGui_altitudeError_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert function.ui.altitudeError.text() == "  0.0"


def test_updateAlignGui_errorRMS_1(function):
    function.app.mount.model.errorRMS = 1
    function.updateAlignGUI(function.app.mount.model)
    assert function.ui.errorRMS.text() == "  1.0"
    assert function.ui.errorRMS1.text() == "  1.0"


def test_updateAlignGui_azimuthError_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert function.ui.azimuthError.text() == "  0.0"


def test_updateAlignGui_terms_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert function.ui.terms.text() == " 1"


def test_updateAlignGui_orthoError_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert function.ui.orthoError.text() == "    0"


def test_updateAlignGui_positionAngle_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert function.ui.positionAngle.text() == "  0.0"


def test_updateAlignGui_polarError_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert function.ui.polarError.text() == "    0"


def test_updateTurnKnobsGUI_1(function):
    class Test:
        azimuthTurns = None
        altitudeTurns = None

    function.updateTurnKnobsGUI(Test())
    assert function.ui.altitudeTurns.text() == "-"
    assert function.ui.azimuthTurns.text() == "-"


def test_updateTurnKnobsGUI_2(function):
    class Test:
        azimuthTurns = -1
        altitudeTurns = -1

    function.updateTurnKnobsGUI(Test())
    assert function.ui.altitudeTurns.text() == "1.0 revs up"
    assert function.ui.azimuthTurns.text() == "1.0 revs right"


def test_updateTurnKnobsGUI_3(function):
    class Test:
        azimuthTurns = 1
        altitudeTurns = 1

    function.updateTurnKnobsGUI(Test())
    assert function.ui.altitudeTurns.text() == "1.0 revs down"
    assert function.ui.azimuthTurns.text() == "1.0 revs left"
