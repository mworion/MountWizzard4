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
import astropy
from unittest import mock

# external packages
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QWidget
import hid

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabSett_Misc import SettMisc
import gui.mainWaddon.tabSett_Misc
from gui.widgets.main_ui import Ui_MainWindow
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.gameControllerRunning = False
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = SettMisc(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    with mock.patch.object(function,
                           'populateGameControllerList'):
        function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_sendGameControllerSignals_1(function):
    act = [0, 0, 0, 0, 0, 0, 0]
    old = [1, 1, 1, 1, 1, 1, 1]
    suc = function.sendGameControllerSignals(act, old)
    assert suc


def test_readGameController_1(function):
    class Gamepad:
        @staticmethod
        def read(a):
            return [0] * 12

    function.mainW.gameControllerRunning = True
    with mock.patch.object(Gamepad,
                           'read',
                           side_effect=Exception):
        val = function.readGameController(Gamepad())
        assert len(val) == 0


def test_readGameController_2(function):
    class Gamepad:
        @staticmethod
        def read(a):
            return []

    function.mainW.gameControllerRunning = False
    val = function.readGameController(Gamepad())
    assert len(val) == 0


def test_readGameController_3(function):
    class Gamepad:
        @staticmethod
        def read(a):
            function.mainW.gameControllerRunning = False
            return [0] * 12

    function.mainW.gameControllerRunning = True
    val = function.readGameController(Gamepad())
    assert len(val) == 12


def test_readGameController_4(function):
    class Gamepad:
        @staticmethod
        def read(a):
            function.mainW.gameControllerRunning = False
            return []

    function.mainW.gameControllerRunning = True
    val = function.readGameController(Gamepad())
    assert len(val) == 0


def test_workerGameController_1(function):
    function.mainW.gameControllerRunning = False
    suc = function.workerGameController()
    assert not suc


def test_convertData_1(function):
    val = function.convertData('test', [])
    assert val[0] == 0
    assert val[1] == 0
    assert val[2] == 0
    assert val[3] == 0
    assert val[4] == 0
    assert val[5] == 0
    assert val[6] == 0


def test_convertData_2(function):
    iR = [0, 1, 2, 3, 0, 5, 0, 7, 0, 9, 0, 11]
    name = 'Pro Controller'
    val = function.convertData(name, iR)
    assert val[0] == 1
    assert val[1] == 2
    assert val[2] == 3
    assert val[3] == 5
    assert val[4] == 7
    assert val[5] == 9
    assert val[6] == 11


def test_convertData_3(function):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0]
    name = 'Controller (XBOX 360 For Windows)'
    val = function.convertData(name, iR)
    assert val[0] == 10
    assert val[1] == 0
    assert val[2] == 0b1111
    assert val[3] == 1
    assert val[4] == 3
    assert val[5] == 5
    assert val[6] == 7


def test_convertData_4(function):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b11100]
    name = 'Controller (XBOX 360 For Windows)'
    val = function.convertData(name, iR)
    assert val[0] == 10
    assert val[1] == 0
    assert val[2] == 0b110
    assert val[3] == 1
    assert val[4] == 3
    assert val[5] == 5
    assert val[6] == 7


def test_convertData_5(function):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b10100]
    name = 'Controller (XBOX 360 For Windows)'
    val = function.convertData(name, iR)
    assert val[0] == 10
    assert val[1] == 0
    assert val[2] == 0b100
    assert val[3] == 1
    assert val[4] == 3
    assert val[5] == 5
    assert val[6] == 7


def test_convertData_6(function):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b1100]
    name = 'Controller (XBOX 360 For Windows)'
    val = function.convertData(name, iR)
    assert val[0] == 10
    assert val[1] == 0
    assert val[2] == 0b10
    assert val[3] == 1
    assert val[4] == 3
    assert val[5] == 5
    assert val[6] == 7


def test_convertData_7(function):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b100]
    name = 'Controller (XBOX 360 For Windows)'
    val = function.convertData(name, iR)
    assert val[0] == 10
    assert val[1] == 0
    assert val[2] == 0b0
    assert val[3] == 1
    assert val[4] == 3
    assert val[5] == 5
    assert val[6] == 7


def test_isNewerData_1(function):
    suc = function.isNewerData([], [])
    assert not suc


def test_isNewerData_2(function):
    suc = function.isNewerData([2], [2])
    assert not suc


def test_isNewerData_3(function):
    suc = function.isNewerData([2], [0])
    assert suc


def test_workerGameController_2(function):
    class Gamepad:
        @staticmethod
        def read(a):
            return [0] * 12

        @staticmethod
        def open(a, b):
            return

        @staticmethod
        def set_nonblocking(a):
            return

    function.mainW.gameControllerRunning = False
    function.ui.gameControllerList.clear()
    function.ui.gameControllerList.addItem('test')
    function.ui.gameControllerList.setCurrentIndex(0)
    function.gameControllerList['test'] = {'vendorId': 1, 'productId': 1}
    with mock.patch.object(hid,
                           'device',
                           return_value=Gamepad()):
        suc = function.workerGameController()
        assert suc


def test_workerGameController_3(function):
    class Gamepad:
        @staticmethod
        def read(a):
            return [0] * 12

        @staticmethod
        def open(a, b):
            return

        @staticmethod
        def set_nonblocking(a):
            return

    def gc(a):
        function.mainW.gameControllerRunning = False
        return []

    function.mainW.gameControllerRunning = True
    temp = function.readGameController
    function.readGameController = gc
    function.ui.gameControllerList.clear()
    function.ui.gameControllerList.addItem('test')
    function.ui.gameControllerList.setCurrentIndex(0)
    function.gameControllerList['test'] = {'vendorId': 1, 'productId': 1}
    with mock.patch.object(hid,
                           'device',
                           return_value=Gamepad()):
        with mock.patch.object(gui.mainWaddon.tabSett_Misc,
                               'sleepAndEvents'):
            suc = function.workerGameController()
            assert suc
    function.readGameController = temp


def test_workerGameController_4(function):
    class Gamepad:
        @staticmethod
        def read(a):
            return [0] * 12

        @staticmethod
        def open(a, b):
            return

        @staticmethod
        def set_nonblocking(a):
            return

    def gc(a):
        function.mainW.gameControllerRunning = False
        return [1] * 12

    function.mainW.gameControllerRunning = True
    temp = function.readGameController
    function.readGameController = gc
    function.ui.gameControllerList.clear()
    function.ui.gameControllerList.addItem('test')
    function.ui.gameControllerList.setCurrentIndex(0)
    function.gameControllerList['test'] = {'vendorId': 1, 'productId': 1}
    with mock.patch.object(hid,
                           'device',
                           return_value=Gamepad()):
        with mock.patch.object(gui.mainWaddon.tabSett_Misc,
                               'sleepAndEvents'):
            with mock.patch.object(function,
                                   'sendGameControllerSignals'):
                suc = function.workerGameController()
                assert suc
    function.readGameController = temp


def test_startGameController(function):
    with mock.patch.object(function.app.threadPool,
                           'start'):
        suc = function.startGameController()
        assert suc


def test_isValidGameControllers_1(function):
    suc = function.isValidGameControllers('test')
    assert not suc


def test_isValidGameControllers_2(function):
    suc = function.isValidGameControllers('Game')
    assert suc


def test_populateGameControllerList_1(function):
    function.ui.gameControllerGroup.setChecked(False)
    function.mainW.gameControllerRunning = True
    suc = function.populateGameControllerList()
    assert not suc


def test_populateGameControllerList_2(function):
    function.ui.gameControllerGroup.setChecked(True)
    function.mainW.gameControllerRunning = True
    suc = function.populateGameControllerList()
    assert not suc


def test_populateGameControllerList_3(function):
    function.ui.gameControllerGroup.setChecked(True)
    function.mainW.gameControllerRunning = False
    device = [{'product_string': 'test',
               'vendor_id': 1,
               'product_id': 1}]
    with mock.patch.object(hid,
                           'enumerate',
                           return_value=device):
        with mock.patch.object(function,
                               'isValidGameControllers',
                               return_value=False):
            suc = function.populateGameControllerList()
            assert not suc


def test_populateGameControllerList_4(function):
    function.ui.gameControllerGroup.setChecked(True)
    function.mainW.gameControllerRunning = False
    device = [{'product_string': 'test',
               'vendor_id': 1,
               'product_id': 1}]
    with mock.patch.object(hid,
                           'enumerate',
                           return_value=device):
        with mock.patch.object(function,
                               'isValidGameControllers',
                               return_value=True):
            with mock.patch.object(function,
                                   'startGameController'):
                suc = function.populateGameControllerList()
                assert suc
                assert function.mainW.gameControllerRunning


def test_playAudioDomeSlewFinished_1(function):
    with mock.patch.object(QSoundEffect,
                           'play'):
        suc = function.playSound('DomeSlew')
        assert not suc


def test_playAudioMountSlewFinished_1(function):
    with mock.patch.object(QSoundEffect,
                           'play'):
        suc = function.playSound('MountSlew')
        assert not suc


def test_playAudioMountAlert_1(function):
    with mock.patch.object(QSoundEffect,
                           'play'):
        suc = function.playSound('MountAlert')
        assert not suc


def test_playAudioModelFinished_1(function):
    with mock.patch.object(QSoundEffect,
                           'play'):
        suc = function.playSound('ModelFinished')
        assert not suc


def test_setupAudioSignals_1(function):
    suc = function.setupAudioSignals()
    assert suc


def test_playSound_1(function):
    suc = function.playSound()
    assert not suc


def test_playSound_2(function):
    function.audioSignalsSet['Pan1'] = 'test'
    function.guiAudioList['MountSlew'] = function.ui.soundMountSlewFinished
    function.guiAudioList['MountSlew'].clear()
    function.guiAudioList['MountSlew'].addItem('Pan1')
    with mock.patch.object(QSoundEffect,
                           'play'):
        suc = function.playSound('MountSlew')
        assert suc


def test_playSound_3(function):
    function.audioSignalsSet['Pan1'] = 'test'
    function.guiAudioList['MountSlew'] = function.ui.soundMountSlewFinished
    function.guiAudioList['MountSlew'].clear()
    function.guiAudioList['MountSlew'].addItem('Pan5')

    with mock.patch.object(QSoundEffect,
                           'play'):
        suc = function.playSound('MountSlew')
        assert not suc


def test_setAddProfileGUI(function):
    suc = function.setAddProfileGUI()
    assert suc


def test_minimizeGUI(function):
    suc = function.minimizeGUI()
    assert suc
