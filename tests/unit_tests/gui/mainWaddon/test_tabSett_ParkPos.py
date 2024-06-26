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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock

import logging
from PySide6.QtWidgets import QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabSett_ParkPos import SettParkPos
from gui.widgets.main_ui import Ui_MainWindow


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.app = App()
    mainW.threadPool = mainW.app.threadPool
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)

    window = SettParkPos(mainW)
    yield window


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    suc = function.initConfig()
    assert suc


def test_initConfig_3(function):
    config = function.app.config['mainW']
    for i in range(0, 10):
        config[f'posText{i:1d}'] = str(i)
        config[f'posAlt{i:1d}'] = i
        config[f'posAz{i:1d}'] = i
    function.initConfig()
    assert function.ui.posText0.text() == '0'
    assert function.ui.posAlt0.value() == 0
    assert function.ui.posAz0.value() == 0
    assert function.ui.posText4.text() == '4'
    assert function.ui.posAlt4.value() == 4
    assert function.ui.posAz4.value() == 4
    assert function.ui.posText7.text() == '7'
    assert function.ui.posAlt7.value() == 7
    assert function.ui.posAz7.value() == 7


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_setupParkPosGui(function):
    assert 10 == len(function.posButtons)
    assert 10 == len(function.posTexts)
    assert 10 == len(function.posAlt)
    assert 10 == len(function.posAz)
    assert 10 == len(function.posSaveButtons)


def test_parkAtPos_1(function):
    function.app.mount.signals.slewFinished.connect(function.parkAtPos)
    with mock.patch.object(function.app.mount.obsSite,
                           'parkOnActualPosition',
                           return_value=False):
        suc = function.parkAtPos()
        assert not suc


def test_parkAtPos_2(function):
    function.app.mount.signals.slewFinished.connect(function.parkAtPos)
    with mock.patch.object(function.app.mount.obsSite,
                           'parkOnActualPosition',
                           return_value=True):
        suc = function.parkAtPos()
        assert suc


def test_slewParkPos_1(function):
    def Sender():
        return QWidget()
    function.sender = Sender
    suc = function.slewToParkPos()
    assert not suc


def test_slewParkPos_2(function):
    def Sender():
        return function.ui.posButton0
    function.sender = Sender
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=False):
        suc = function.slewToParkPos()
        assert not suc


def test_slewParkPos_3(function):
    def Sender():
        return function.ui.posButton0
    function.sender = Sender
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'startSlewing',
                               return_value=False):
            suc = function.slewToParkPos()
            assert not suc


def test_slewParkPos_4(function):
    def Sender():
        return function.ui.posButton0
    function.sender = Sender
    function.ui.parkMountAfterSlew.setChecked(True)
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'startSlewing',
                               return_value=True):
            suc = function.slewToParkPos()
            assert not suc


def test_slewParkPos_5(function):
    def Sender():
        return function.ui.posButton0
    function.sender = Sender
    function.ui.parkMountAfterSlew.setChecked(False)
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'startSlewing',
                               return_value=True):
            suc = function.slewToParkPos()
            assert suc


def test_saveActualPosition_1(function):
    temp = function.app.mount.obsSite.Alt
    function.app.mount.obsSite.Alt = None

    suc = function.saveActualPosition()
    assert not suc
    function.app.mount.obsSite.Alt = temp


def test_saveActualPosition_2(function):
    temp = function.app.mount.obsSite.Az
    function.app.mount.obsSite.Az = None

    suc = function.saveActualPosition()
    assert not suc
    function.app.mount.obsSite.Az = temp


def test_saveActualPosition_3(function):
    def Sender():
        return QWidget()

    function.sender = Sender
    suc = function.saveActualPosition()
    assert not suc


def test_saveActualPosition_4(function):
    def Sender():
        return function.ui.posSave0

    function.sender = Sender
    suc = function.saveActualPosition()
    assert suc
