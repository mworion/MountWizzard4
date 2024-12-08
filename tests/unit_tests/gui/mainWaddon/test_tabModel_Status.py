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
# GUI with PySide for python !

#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest

# external packages
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabModel_Status import ModelStatus
from gui.widgets.main_ui import Ui_MainWindow


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = ModelStatus(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_setupIcons(function):
    pm = QPixmap()
    with mock.patch.object(function, "img2pixmap", return_value=pm):
        function.setupIcons()


def test_updateAlignGui_numberStars(function):
    function.app.mount.model.starList = []
    function.app.mount.model.numberStars = 1
    function.updateAlignGUI(function.app.mount.model)
    assert " 1" == function.ui.numberStars.text()
    assert " 1" == function.ui.numberStars1.text()


def test_updateAlignGui_altitudeError_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert "  0.0" == function.ui.altitudeError.text()


def test_updateAlignGui_errorRMS_1(function):
    function.app.mount.model.errorRMS = 1
    function.updateAlignGUI(function.app.mount.model)
    assert "  1.0" == function.ui.errorRMS.text()
    assert "  1.0" == function.ui.errorRMS1.text()


def test_updateAlignGui_azimuthError_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert "  0.0" == function.ui.azimuthError.text()


def test_updateAlignGui_terms_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert " 1" == function.ui.terms.text()


def test_updateAlignGui_orthoError_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert "    0" == function.ui.orthoError.text()


def test_updateAlignGui_positionAngle_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert "  0.0" == function.ui.positionAngle.text()


def test_updateAlignGui_polarError_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert "    0" == function.ui.polarError.text()


def test_updateTurnKnobsGUI_1(function):
    class Test:
        azimuthTurns = None
        altitudeTurns = None

    function.updateTurnKnobsGUI(Test())
    assert "-" == function.ui.altitudeTurns.text()
    assert "-" == function.ui.azimuthTurns.text()


def test_updateTurnKnobsGUI_2(function):
    class Test:
        azimuthTurns = -1
        altitudeTurns = -1

    function.updateTurnKnobsGUI(Test())
    assert "1.0 revs up" == function.ui.altitudeTurns.text()
    assert "1.0 revs right" == function.ui.azimuthTurns.text()


def test_updateTurnKnobsGUI_3(function):
    class Test:
        azimuthTurns = 1
        altitudeTurns = 1

    function.updateTurnKnobsGUI(Test())
    assert "1.0 revs down" == function.ui.altitudeTurns.text()
    assert "1.0 revs left" == function.ui.azimuthTurns.text()
