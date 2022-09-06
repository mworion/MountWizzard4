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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import os
import shutil
import glob

# external packages
from PyQt5.QtWidgets import QInputDialog
from astropy.io import fits
from skyfield.api import Angle
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from mountcontrol.convert import formatDstrToText, formatDstrToText
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabTools import Tools
import gui.mainWmixin.tabTools
import mountcontrol


@pytest.fixture(autouse=True, scope='function')
def function(qapp):

    class Mixin(MWidget, Tools):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = self.app.deviceStat
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            Tools.__init__(self)

    window = Mixin()
    yield window

    files = glob.glob('tests/workDir/image/*.fit*')
    for f in files:
        os.remove(f)


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_setupGui(function):
    suc = function.setupGui()
    assert suc
    for _, ui in function.selectorsDropDowns.items():
        assert ui.count() == 7


def test_getNumberFiles_1(function):
    number = function.getNumberFiles()
    assert number == 0


def test_getNumberFiles_2(function):
    number = function.getNumberFiles(pathDir='/Users')
    assert number == 0


def test_getNumberFiles_3(function):
    number = function.getNumberFiles(pathDir='.', search='**/*.fit*')
    assert number > 0


def test_getNumberFiles_4(function):
    number = function.getNumberFiles(pathDir='/xxx', search='**/*.fit*')
    assert number == 0


def test_getNumberFiles_5(function):
    number = function.getNumberFiles(pathDir='tests/testData', search='**/*.fit*')
    assert number == 5


def test_getNumberFiles_6(function):
    number = function.getNumberFiles(pathDir='tests/testData', search='*.fit*')
    assert number == 5


def test_getNumberFiles_7(function):
    number = function.getNumberFiles(pathDir='tests/testData')
    assert number == 0


def test_convertHeaderEntry_1(function):
    chunk = function.convertHeaderEntry(entry='', fitsKey='1')
    assert not chunk


def test_convertHeaderEntry_2(function):
    chunk = function.convertHeaderEntry(entry='1', fitsKey='')
    assert not chunk


def test_convertHeaderEntry_3(function):
    chunk = function.convertHeaderEntry(entry='2019-05-26T17:02:18.843', fitsKey='DATE-OBS')
    assert chunk == '2019-05-26_17-02-18'


def test_convertHeaderEntry_4(function):
    chunk = function.convertHeaderEntry(entry='2019-05-26T17:02:18', fitsKey='DATE-OBS')
    assert chunk == '2019-05-26_17-02-18'


def test_convertHeaderEntry_5(function):
    chunk = function.convertHeaderEntry(entry=1, fitsKey='XBINNING')
    assert chunk == 'Bin1'


def test_convertHeaderEntry_6(function):
    chunk = function.convertHeaderEntry(entry=25, fitsKey='CCD-TEMP')
    assert chunk == 'Temp025'


def test_convertHeaderEntry_7(function):
    chunk = function.convertHeaderEntry(entry='Light', fitsKey='FRAME')
    assert chunk == 'Light'


def test_convertHeaderEntry_8(function):
    chunk = function.convertHeaderEntry(entry='red', fitsKey='FILTER')
    assert chunk == 'red'


def test_convertHeaderEntry_9(function):
    chunk = function.convertHeaderEntry(entry=14, fitsKey='EXPTIME')
    assert chunk == 'Exp14s'


def test_convertHeaderEntry_11(function):
    chunk = function.convertHeaderEntry(entry='12354', fitsKey='XXX')
    assert not chunk


def test_processSelectors_1(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('DATE-OBS', '2019-05-26T17:02:18.843')
    name = function.processSelectors(fitsHeader=header)
    assert not name


def test_processSelectors_2(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('DATE-OBS', '2019-05-26T17:02:18.843')
    name = function.processSelectors(fitsHeader=header, selection='Frame')
    assert not name


def test_processSelectors_3(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('DATE-OBS', '2019-05-26T17:02:18.843')
    name = function.processSelectors(fitsHeader=header, selection='Datetime')
    assert name == '2019-05-26_17-02-18'


def test_processSelectors_4(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('DATE-OBS', '2019-05-26T17:02:18.843')
    name = function.processSelectors(selection='Datetime')
    assert not name


def test_renameFile_1(function):
    suc = function.renameFile()
    assert not suc


def test_renameFile_2(function):
    suc = function.renameFile('tests/workDir/image/m51.fit')
    assert not suc


def test_renameFile_3(function):
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')

    with mock.patch.object(os,
                           'rename'):
        suc = function.renameFile('tests/workDir/image/m51.fit')
        assert suc


def test_renameFile_4(function):
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    function.ui.newObjectName.setText('test')

    with mock.patch.object(os,
                           'rename'):
        suc = function.renameFile('tests/workDir/image/m51.fit')
        assert suc


def test_renameFile_5(function):
    hdu = fits.PrimaryHDU(np.arange(100.0))
    hduList = fits.HDUList([hdu])
    hduList.writeto('tests/workDir/image/m51.fit')

    with mock.patch.object(os,
                           'rename'):
        suc = function.renameFile('tests/workDir/image/m51.fit')
        assert suc


def test_renameFile_6(function):
    hdu = fits.PrimaryHDU(np.arange(100.0))
    hdu.header['FILTER'] = 'test'
    hduList = fits.HDUList([hdu])
    hduList.writeto('tests/workDir/image/m51.fit')

    function.ui.rename1.clear()
    function.ui.rename1.addItem('Filter')

    with mock.patch.object(os,
                           'rename'):
        suc = function.renameFile('tests/workDir/image/m51.fit')
        assert suc


def test_renameRunGUI_1(function):
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    function.ui.renameDir.setText('')
    suc = function.renameRunGUI()
    assert not suc


def test_renameRunGUI_2(function):
    function.ui.renameDir.setText('tests/workDir/image')
    suc = function.renameRunGUI()
    assert not suc


def test_renameRunGUI_3(function):
    function.ui.includeSubdirs.setChecked(True)
    function.ui.renameDir.setText('tests/workDir/image')
    suc = function.renameRunGUI()
    assert not suc


def test_renameRunGUI_4(function):
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    function.ui.renameDir.setText('tests/workDir/image')
    with mock.patch.object(function,
                           'renameFile',
                           return_value=True):
        suc = function.renameRunGUI()
        assert suc


def test_renameRunGUI_5(function):
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    function.ui.renameDir.setText('tests/workDir/image')
    with mock.patch.object(function,
                           'renameFile',
                           return_value=False):
        suc = function.renameRunGUI()
        assert suc


def test_chooseDir_1(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('', '', '')):
        suc = function.chooseDir()
        assert suc


def test_chooseDir_2(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', '', '')):
        suc = function.chooseDir()
        assert suc


def test_moveDuration_1(function):
    function.ui.moveDuration.setCurrentIndex(1)
    with mock.patch.object(gui.mainWmixin.tabTools,
                           'sleepAndEvents'):
        with mock.patch.object(function,
                               'stopMoveAll'):
            suc = function.moveDuration()
            assert suc


def test_moveDuration_2(function):
    function.ui.moveDuration.setCurrentIndex(2)
    with mock.patch.object(gui.mainWmixin.tabTools,
                           'sleepAndEvents'):
        with mock.patch.object(function,
                               'stopMoveAll'):
            suc = function.moveDuration()
            assert suc


def test_moveDuration_3(function):
    function.ui.moveDuration.setCurrentIndex(3)
    with mock.patch.object(gui.mainWmixin.tabTools,
                           'sleepAndEvents'):
        with mock.patch.object(function,
                               'stopMoveAll'):
            suc = function.moveDuration()
            assert suc


def test_moveDuration_4(function):
    function.ui.moveDuration.setCurrentIndex(4)
    with mock.patch.object(gui.mainWmixin.tabTools,
                           'sleepAndEvents'):
        with mock.patch.object(function,
                               'stopMoveAll'):
            suc = function.moveDuration()
            assert suc


def test_moveDuration_5(function):
    function.ui.moveDuration.setCurrentIndex(0)
    with mock.patch.object(gui.mainWmixin.tabTools,
                           'sleepAndEvents'):
        suc = function.moveDuration()
        assert not suc


def test_moveClassicGameController_1(function):
    with mock.patch.object(function,
                           'stopMoveAll'):
        suc = function.moveClassicGameController(128, 128)
        assert suc


def test_moveClassicGameController_2(function):
    with mock.patch.object(function,
                           'moveClassic'):
        suc = function.moveClassicGameController(0, 0)
        assert suc


def test_moveClassicGameController_3(function):
    with mock.patch.object(function,
                           'moveClassic'):
        suc = function.moveClassicGameController(255, 255)
        assert suc


def test_moveClassicUI_1(function):
    def Sender():
        return function.ui.moveNorthEast

    function.deviceStat['mount'] = False
    function.sender = Sender
    suc = function.moveClassicUI()
    assert not suc


def test_moveClassicUI_2(function):
    def Sender():
        return function.ui.moveNorthEast

    function.deviceStat['mount'] = True
    function.sender = Sender
    suc = function.moveClassicUI()
    assert suc


def test_moveClassic_1(function):
    with mock.patch.object(function,
                           'moveDuration'):
        suc = function.moveClassic([1, 1])
        assert suc


def test_moveClassic_2(function):
    with mock.patch.object(function,
                           'moveDuration'):
        suc = function.moveClassic([-1, -1])
        assert suc


def test_moveClassic_3(function):
    with mock.patch.object(function,
                           'moveDuration'):
        suc = function.moveClassic([0, 0])
        assert suc


def test_stopMoveAll(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'stopMoveAll',
                           return_value=True):
        suc = function.stopMoveAll()
        assert suc


def test_setSlewSpeed_1(function):
    def Sender():
        return function.ui.renameStart

    function.sender = Sender

    suc = function.setSlewSpeed()
    assert not suc


def test_setSlewSpeed_2(function):
    def Sender():
        return function.ui.slewSpeedMax

    def test():
        return

    function.slewSpeeds = {function.ui.slewSpeedMax: test}
    function.sender = Sender

    suc = function.setSlewSpeed()
    assert suc


def test_slewSelectedTargetWithDome_0(function):
    function.app.mount.obsSite.AltTarget = None
    function.app.deviceStat['dome'] = None
    suc = function.slewSelectedTargetWithDome()
    assert not suc


def test_slewSelectedTargetWithDome_2(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=10)
    function.app.mount.obsSite.AzTarget = Angle(degrees=10)
    function.app.deviceStat['dome'] = False
    with mock.patch.object(function.app.mount.obsSite,
                           'startSlewing',
                           return_value=True):
        suc = function.slewSelectedTargetWithDome()
        assert suc


def test_slewSelectedTargetWithDome_3(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=10)
    function.app.mount.obsSite.AzTarget = Angle(degrees=10)
    function.app.deviceStat['dome'] = False
    with mock.patch.object(function.app.mount.obsSite,
                           'startSlewing',
                           return_value=False):
        suc = function.slewSelectedTargetWithDome()
        assert not suc


def test_slewSelectedTargetWithDome_4(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=10)
    function.app.mount.obsSite.AzTarget = Angle(degrees=10)
    function.app.deviceStat['dome'] = True
    with mock.patch.object(function.app.mount.obsSite,
                           'startSlewing',
                           return_value=False):
        with mock.patch.object(function.app.dome,
                               'slewDome',
                               return_value=10):
            suc = function.slewSelectedTargetWithDome()
            assert not suc


def test_slewTargetAltAz_1(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=False):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=False):
            suc = function.slewTargetAltAz(100, 10)
            assert not suc


def test_slewTargetAltAz_2(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=False):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=True):
            suc = function.slewTargetAltAz(-10, 10)
            assert not suc


def test_slewTargetAltAz_3(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=True):
            suc = function.slewTargetAltAz(100, 10)
            assert suc


def test_moveAltAzDefault(function):
    suc = function.moveAltAzDefault()
    assert suc


def test_moveAltAzUI_1(function):
    def Sender():
        return function.ui.moveNorthEastAltAz

    function.sender = Sender
    function.deviceStat['mount'] = False
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzUI()
        assert not suc


def test_moveAltAzUI_2(function):
    def Sender():
        return function.ui.moveNorthEastAltAz

    function.sender = Sender
    function.deviceStat['mount'] = True
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzUI()
        assert not suc


def test_moveAltAzGameController_1(function):
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzGameController(0)
        assert suc


def test_moveAltAzGameController_2(function):
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzGameController(2)
        assert suc


def test_moveAltAzGameController_3(function):
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzGameController(4)
        assert suc


def test_moveAltAzGameController_4(function):
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzGameController(6)
        assert suc


def test_moveAltAzGameController_5(function):
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzGameController(99)
        assert not suc


def test_moveAltAz_1(function):
    function.targetAlt = None
    function.targetAz = None
    function.app.mount.obsSite.Alt = None
    function.app.mount.obsSite.Az = Angle(degrees=10)

    with mock.patch.object(function,
                           'slewTargetAltAz',
                           return_value=False):
        suc = function.moveAltAz([1, 1])
        assert not suc


def test_moveAltAz_2(function):
    function.targetAlt = None
    function.targetAz = None
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=10)

    with mock.patch.object(function,
                           'slewTargetAltAz',
                           return_value=False):
        suc = function.moveAltAz([1, 1])
        assert not suc


def test_moveAltAz_3(function):
    function.targetAlt = 10
    function.targetAz = 10
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=10)

    with mock.patch.object(function,
                           'slewTargetAltAz',
                           return_value=True):
        suc = function.moveAltAz([1, 1])
        assert suc


def test_setRA_1(function):
    with mock.patch.object(QInputDialog,
                           'getText',
                           return_value=('', False)):
        suc = function.setRA()
        assert not suc


def test_setRA_2(function):
    with mock.patch.object(QInputDialog,
                           'getText',
                           return_value=('', True)):
        suc = function.setRA()
        assert not suc


def test_setRA_3(function):
    with mock.patch.object(QInputDialog,
                           'getText',
                           return_value=('12H', True)):
        suc = function.setRA()
        assert suc


def test_setDEC_1(function):
    with mock.patch.object(QInputDialog,
                           'getText',
                           return_value=('', False)):
        suc = function.setDEC()
        assert not suc


def test_setDEC_2(function):
    with mock.patch.object(QInputDialog,
                           'getText',
                           return_value=('', True)):
        suc = function.setDEC()
        assert not suc


def test_setDEC_3(function):
    with mock.patch.object(QInputDialog,
                           'getText',
                           return_value=('12', True)):
        suc = function.setDEC()
        assert suc


def test_moveAltAzAbsolute_1(function):
    function.ui.moveCoordinateAlt.setText('50h')
    function.ui.moveCoordinateAz.setText('50h')
    suc = function.moveAltAzAbsolute()
    assert not suc


def test_moveAltAzAbsolute_2(function):
    function.ui.moveCoordinateAlt.setText('50')
    function.ui.moveCoordinateAz.setText('50h')
    suc = function.moveAltAzAbsolute()
    assert not suc


def test_moveAltAzAbsolute_3(function):
    function.app.mount.setting.horizonLimitLow = 10
    function.app.mount.setting.horizonLimitHigh = 70
    function.ui.moveCoordinateAlt.setText('50')
    function.ui.moveCoordinateAz.setText('50')
    with mock.patch.object(function,
                           'slewTargetAltAz',
                           return_value=False):
        suc = function.moveAltAzAbsolute()
        assert not suc


def test_moveAltAzAbsolute_4(function):
    function.app.mount.setting.horizonLimitLow = 10
    function.app.mount.setting.horizonLimitHigh = 70
    function.ui.moveCoordinateAlt.setText('50')
    function.ui.moveCoordinateAz.setText('50')
    with mock.patch.object(function,
                           'slewTargetAltAz',
                           return_value=True):
        suc = function.moveAltAzAbsolute()
        assert suc


def test_moveRaDecAbsolute_1(function):
    function.ui.moveCoordinateRa.setText('asd')
    function.ui.moveCoordinateDec.setText('asd')
    suc = function.moveRaDecAbsolute()
    assert not suc


def test_moveRaDecAbsolute_2(function):
    function.ui.moveCoordinateRa.setText('12H')
    function.ui.moveCoordinateDec.setText('asd')
    suc = function.moveRaDecAbsolute()
    assert not suc


def test_moveRaDecAbsolute_3(function):
    function.ui.moveCoordinateRa.setText('12H')
    function.ui.moveCoordinateDec.setText('30 30')
    a = function.app.mount.obsSite.timeJD
    function.app.mount.obsSite.timeJD = None
    suc = function.moveRaDecAbsolute()
    assert not suc
    function.app.mount.obsSite.timeJD = a


def test_moveRaDecAbsolute_4(function):
    function.ui.moveCoordinateRa.setText('12H')
    function.ui.moveCoordinateDec.setText('30 30')
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetRaDec'):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=False):
            suc = function.moveRaDecAbsolute()
            assert not suc


def test_moveRaDecAbsolute_5(function):
    function.ui.moveCoordinateRa.setText('12H')
    function.ui.moveCoordinateDec.setText('30 30')
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetRaDec'):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=True):
            suc = function.moveRaDecAbsolute()
            assert suc


def test_moveRaDecAbsolute_6(function):
    function.ui.moveCoordinateRa.setText('12H')
    function.ui.moveCoordinateDec.setText('30 30')
    with mock.patch.object(function.app.mount.obsSite,
                           'timeJD',
                           return_value=None):
        with mock.patch.object(function.app.mount.obsSite,
                               'setTargetRaDec'):
            with mock.patch.object(function,
                                   'slewSelectedTargetWithDome',
                                   return_value=False):
                suc = function.moveRaDecAbsolute()
                assert not suc


def test_commandRaw_1(function):
    with mock.patch.object(mountcontrol.connection.Connection,
                           'communicateRaw',
                           return_value=(True, False, '')):
        suc = function.commandRaw()
        assert suc


def test_commandRaw_2(function):
    with mock.patch.object(mountcontrol.connection.Connection,
                           'communicateRaw',
                           return_value=(True, True, '')):
        suc = function.commandRaw()
        assert suc
