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
import pytest
import logging
from unittest import mock

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
from skyfield.api import wgs84

# local import
from tests.baseTestSetupMixins import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabSettDome import SettDome
from logic.dome.dome import Dome


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    class Mixin(MWidget, SettDome):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.deviceStat = self.app.deviceStat
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            SettDome.__init__(self)

    window = Mixin()
    yield window


def test_tab1(function):
    function.tab1()


def test_tab2(function):
    function.tab2()


def test_tab3(function):
    function.tab3()


def test_tab4(function):
    function.tab4()


def test_tab5(function):
    function.tab5()


def test_tab6(function):
    function.tab6()


def test_tab7(function):
    function.tab7()


def test_tab8(function):
    function.tab8()


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_setZoffGEMInMount(function):
    suc = function.setZoffGEMInMount()
    assert suc


def test_setZoff10micronInMount(function):
    suc = function.setZoff10micronInMount()
    assert suc


def test_setUseGeometryInMount_1(function):
    function.ui.autoDomeDriver.setChecked(False)
    suc = function.setUseGeometryInMount()
    assert suc


def test_setUseGeometryInMount_2(function):
    function.ui.autoDomeDriver.setChecked(True)
    with mock.patch.object(function,
                           'updateDomeGeometryToGui'):
        suc = function.setUseGeometryInMount()
        assert suc


def test_setUseDomeGeometry_1(function):
    function.ui.useDomeGeometry.setChecked(True)
    suc = function.setUseDomeGeometry()
    assert suc
    assert function.app.dome.useGeometry


def test_setUseDomeGeometry_2(function):
    function.ui.useDomeGeometry.setChecked(False)
    suc = function.setUseDomeGeometry()
    assert suc
    assert not function.app.dome.useGeometry


def test_updateDomeGeometry_1(function):
    suc = function.updateDomeGeometryToGui()
    assert suc


def test_setDomeSettlingTime_1(function):
    suc = function.setDomeSettlingTime()
    assert suc


def test_updateShutterStatGui_1(function):
    function.app.dome.data['DOME_SHUTTER.SHUTTER_OPEN'] = True
    function.app.dome.data['Status.Shutter'] = 'test'
    suc = function.updateShutterStatGui()
    assert suc
    assert function.ui.domeShutterStatusText.text() == 'test'


def test_updateShutterStatGui_2(function):
    function.app.dome.data['DOME_SHUTTER.SHUTTER_OPEN'] = False
    function.app.dome.data['Status.Shutter'] = 'test'
    suc = function.updateShutterStatGui()
    assert suc
    assert function.ui.domeShutterStatusText.text() == 'test'


def test_updateShutterStatGui_3(function):
    function.app.dome.data['DOME_SHUTTER.SHUTTER_OPEN'] = None
    function.app.dome.data['Status.Shutter'] = 'test'
    suc = function.updateShutterStatGui()
    assert suc
    assert function.ui.domeShutterStatusText.text() == 'test'


def test_domeAbortSlew_1(function):
    with mock.patch.object(function.app.dome,
                           'abortSlew',
                           return_value=False):
        suc = function.domeAbortSlew()
        assert not suc


def test_domeAbortSlew_2(function):
    with mock.patch.object(function.app.dome,
                           'abortSlew',
                           return_value=True):
        suc = function.domeAbortSlew()
        assert suc


def test_domeOpenShutter_1(function):
    with mock.patch.object(function.app.dome,
                           'openShutter',
                           return_value=False):
        suc = function.domeOpenShutter()
        assert not suc


def test_domeOpenShutter_2(function):
    with mock.patch.object(function.app.dome,
                           'openShutter',
                           return_value=True):
        suc = function.domeOpenShutter()
        assert suc


def test_domeCloseShutter_1(function):
    with mock.patch.object(function.app.dome,
                           'closeShutter',
                           return_value=False):
        suc = function.domeCloseShutter()
        assert not suc


def test_domeCloseShutter_2(function):
    with mock.patch.object(function.app.dome,
                           'closeShutter',
                           return_value=True):
        suc = function.domeCloseShutter()
        assert suc
