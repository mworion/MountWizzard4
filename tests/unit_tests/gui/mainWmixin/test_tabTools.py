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
# written in python3 , (c) 2019, 2020 by mworion
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
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtTest import QTest
from astropy.io import fits
from mountcontrol.qtmount import Mount
from skyfield.api import Angle

# local import
from gui.mainWmixin.tabTools import Tools
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, app

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/data')
        update1s = pyqtSignal()
        message = pyqtSignal(str, int)
        mwGlob = {'imageDir': 'tests/image'}
        deviceStat = {}

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = Tools(app=Test(), ui=ui,
                clickable=MWidget().clickable)

    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.openDir = MWidget().openDir
    app.deleteLater = MWidget().deleteLater
    qtbot.addWidget(app)

    yield

    files = glob.glob('tests/image/*.fit*')
    for f in files:
        os.remove(f)


def test_initConfig_1():
    app.app.config['mainW'] = {}
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_setupGui():
    suc = app.setupGui()
    assert suc
    for _, ui in app.selectorsDropDowns.items():
        assert ui.count() == 7


def test_getNumberFiles_1():
    number = app.getNumberFiles()
    assert number == 0


def test_getNumberFiles_2():
    number = app.getNumberFiles(pathDir='/Users')
    assert number == 0


def test_getNumberFiles_3():
    number = app.getNumberFiles(pathDir='.', search='**/*.fit*')
    assert number > 0


def test_getNumberFiles_4():
    number = app.getNumberFiles(pathDir='/xxx', search='**/*.fit*')
    assert number == 0


def test_getNumberFiles_5():
    number = app.getNumberFiles(pathDir='tests/testData', search='**/*.fit*')
    assert number == 2


def test_getNumberFiles_6():
    number = app.getNumberFiles(pathDir='tests/testData', search='*.fit*')
    assert number == 2


def test_convertHeaderEntry_1():
    chunk = app.convertHeaderEntry(entry='', fitsKey='1')
    assert not chunk


def test_convertHeaderEntry_2():
    chunk = app.convertHeaderEntry(entry='1', fitsKey='')
    assert not chunk


def test_convertHeaderEntry_3():
    chunk = app.convertHeaderEntry(entry='2019-05-26T17:02:18.843', fitsKey='DATE-OBS')
    assert chunk == '2019-05-26_17-02-18'


def test_convertHeaderEntry_4():
    chunk = app.convertHeaderEntry(entry='2019-05-26T17:02:18', fitsKey='DATE-OBS')
    assert chunk == '2019-05-26_17-02-18'


def test_convertHeaderEntry_5():
    chunk = app.convertHeaderEntry(entry=1, fitsKey='XBINNING')
    assert chunk == 'Bin-1'


def test_convertHeaderEntry_6():
    chunk = app.convertHeaderEntry(entry=25, fitsKey='CCD-TEMP')
    assert chunk == 'Temp025'


def test_convertHeaderEntry_7():
    chunk = app.convertHeaderEntry(entry='Light', fitsKey='FRAME')
    assert chunk == 'Frame-Light'


def test_convertHeaderEntry_8():
    chunk = app.convertHeaderEntry(entry='red', fitsKey='FILTER')
    assert chunk == 'Filter-red'


def test_convertHeaderEntry_9():
    chunk = app.convertHeaderEntry(entry=14, fitsKey='EXPTIME')
    assert chunk == 'Exp-0014s'


def test_convertHeaderEntry_10():
    app.ui.renameText.setText('test')
    chunk = app.convertHeaderEntry(entry='test', fitsKey='RenameText')
    assert chunk == 'TEST'


def test_convertHeaderEntry_11():
    chunk = app.convertHeaderEntry(entry='12354', fitsKey='XXX')
    assert not chunk


def test_processSelectors_1():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('DATE-OBS', '2019-05-26T17:02:18.843')
    name = app.processSelectors(fitsHeader=header)
    assert not name


def test_processSelectors_2():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('DATE-OBS', '2019-05-26T17:02:18.843')
    name = app.processSelectors(fitsHeader=header, selection='Frame')
    assert not name


def test_processSelectors_3():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('DATE-OBS', '2019-05-26T17:02:18.843')
    name = app.processSelectors(fitsHeader=header, selection='Datetime')
    assert name == '2019-05-26_17-02-18'


def test_processSelectors_4():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('DATE-OBS', '2019-05-26T17:02:18.843')
    name = app.processSelectors(selection='Datetime')
    assert not name


def test_renameFile_1():
    suc = app.renameFile()
    assert not suc


def test_renameFile_2():
    suc = app.renameFile('tests/image/m51.fit')
    assert not suc


def test_renameFile_3():
    shutil.copy('tests/testData/m51.fit', 'tests/image/m51.fit')

    with mock.patch.object(os,
                           'rename'):
        suc = app.renameFile('tests/image/m51.fit')
        assert suc


def test_renameRunGUI_1(qtbot):
    shutil.copy('tests/testData/m51.fit', 'tests/image/m51.fit')
    app.ui.renameDir.setText('')
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.renameRunGUI()
        assert not suc
    assert ['No valid input directory given', 2] == blocker.args


def test_renameRunGUI_2(qtbot):
    app.ui.renameDir.setText('tests/image')
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.renameRunGUI()
        assert not suc
    assert ['No files to rename', 0] == blocker.args


def test_renameRunGUI_3(qtbot):
    app.ui.checkIncludeSubdirs.setChecked(True)
    app.ui.renameDir.setText('tests/image')
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.renameRunGUI()
        assert not suc
    assert ['No files to rename', 0] == blocker.args


def test_renameRunGUI_4(qtbot):
    shutil.copy('tests/testData/m51.fit', 'tests/image/m51.fit')
    app.ui.renameDir.setText('tests/image')
    with mock.patch.object(app,
                           'renameFile',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.renameRunGUI()
            assert suc
        assert ['1 images were renamed', 0] == blocker.args


def test_chooseDir_1():
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('', '', '')):
        suc = app.chooseDir()
        assert suc


def test_chooseDir_2():
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', '', '')):
        suc = app.chooseDir()
        assert suc


def test_moveDuration_1():
    app.ui.moveDuration.setCurrentIndex(1)
    with mock.patch.object(QTest,
                           'qWait'):
        with mock.patch.object(app,
                               'stopMoveAll'):
            suc = app.moveDuration()
            assert suc


def test_moveDuration_2():
    app.ui.moveDuration.setCurrentIndex(2)
    with mock.patch.object(QTest,
                           'qWait'):
        with mock.patch.object(app,
                               'stopMoveAll'):
            suc = app.moveDuration()
            assert suc


def test_moveDuration_3():
    app.ui.moveDuration.setCurrentIndex(3)
    with mock.patch.object(QTest,
                           'qWait'):
        with mock.patch.object(app,
                               'stopMoveAll'):
            suc = app.moveDuration()
            assert suc


def test_moveDuration_4():
    app.ui.moveDuration.setCurrentIndex(4)
    with mock.patch.object(QTest,
                           'qWait'):
        with mock.patch.object(app,
                               'stopMoveAll'):
            suc = app.moveDuration()
            assert suc


def test_moveDuration_5():
    app.ui.moveDuration.setCurrentIndex(0)
    with mock.patch.object(QTest,
                           'qWait'):
        suc = app.moveDuration()
        assert not suc


def test_moveClassic_1():
    def sender():
        return 0

    app.sender = sender
    with mock.patch.object(app,
                           'moveDuration'):
        suc = app.moveClassic()
        assert not suc


def test_moveClassic_2():
    def sender():
        return app.ui.moveNorthEast

    app.sender = sender
    with mock.patch.object(app,
                           'moveDuration'):
        suc = app.moveClassic()
        assert suc


def test_moveClassic_3():
    def sender():
        return app.ui.moveSouthWest

    app.sender = sender
    with mock.patch.object(app,
                           'moveDuration'):
        suc = app.moveClassic()
        assert suc


def test_stopMoveAll():
    with mock.patch.object(app.app.mount.obsSite,
                           'stopMoveAll',
                           return_value=True):
        suc = app.stopMoveAll()
        assert suc


def test_setSlewSpeed_1():
    def Sender():
        return ui.slewSpeedHigh

    app.sender = Sender

    suc = app.setSlewSpeed()
    assert suc


def test_setSlewSpeed_2():
    def Sender():
        return ui.slewSpeedMax

    app.sender = Sender

    def test():
        return

    app.slewSpeeds = {app.ui.slewSpeedMax: test}

    suc = app.setSlewSpeed()
    assert suc


def test_slewSelectedTarget_1():
    suc = app.slewSelectedTarget()
    assert not suc


def test_slewSelectedTarget_2():
    app.app.mount.obsSite.AltTarget = Angle(degrees=10)
    app.app.mount.obsSite.AzTarget = Angle(degrees=10)
    app.app.deviceStat['dome'] = False
    with mock.patch.object(app.app.mount.obsSite,
                           'startSlewing',
                           return_value=True):
        suc = app.slewSelectedTarget()
        assert suc


def test_slewSelectedTarget_3():
    app.app.mount.obsSite.AltTarget = Angle(degrees=10)
    app.app.mount.obsSite.AzTarget = Angle(degrees=10)
    app.app.deviceStat['dome'] = False
    with mock.patch.object(app.app.mount.obsSite,
                           'startSlewing',
                           return_value=False):
        suc = app.slewSelectedTarget()
        assert not suc


def test_slewTargetAltAz_1():
    app.app.mount.setting.horizonLimitHigh = 80
    app.app.mount.setting.horizonLimitLow = 10
    app.app.mount.obsSite.status = 0

    with mock.patch.object(app,
                           'slewSelectedTarget',
                           return_value=True):
        suc = app.slewTargetAltAz(100, 10)
        assert suc


def test_slewTargetAltAz_2():
    app.app.mount.setting.horizonLimitHigh = 80
    app.app.mount.setting.horizonLimitLow = 10
    app.app.mount.obsSite.status = 1

    with mock.patch.object(app,
                           'slewSelectedTarget',
                           return_value=False):
        suc = app.slewTargetAltAz(-10, 10)
        assert not suc


def test_moveAltAz_1():
    def sender():
        return 0

    app.sender = sender

    suc = app.moveAltAz()
    assert not suc


def test_moveAltAz_2():
    def sender():
        return app.ui.moveNorthEastAltAz

    app.sender = sender
    app.app.mount.obsSite.status = None
    app.app.mount.obsSite.Alt = 10
    app.app.mount.obsSite.Az = 10

    with mock.patch.object(app,
                           'slewTargetAltAz',
                           return_value=False):
        suc = app.moveAltAz()
        assert not suc


def test_moveAltAz_3():
    def sender():
        return app.ui.moveNorthEastAltAz

    app.sender = sender
    app.app.mount.obsSite.status = 0
    app.app.mount.obsSite.Alt = 10
    app.app.mount.obsSite.Az = 10

    with mock.patch.object(app,
                           'slewTargetAltAz',
                           return_value=False):
        suc = app.moveAltAz()
        assert not suc


def test_moveAltAz_4():
    def sender():
        return app.ui.moveNorthEastAltAz

    app.sender = sender
    app.app.mount.obsSite.status = 1
    app.app.mount.obsSite.Alt = 10
    app.app.mount.obsSite.Az = 10

    with mock.patch.object(app,
                           'slewTargetAltAz',
                           return_value=False):
        suc = app.moveAltAz()
        assert not suc


def test_moveAltAz_5():
    def sender():
        return app.ui.moveNorthEastAltAz

    app.sender = sender
    app.app.mount.obsSite.status = 1
    app.app.mount.obsSite.Alt = 10
    app.app.mount.obsSite.Az = 10

    with mock.patch.object(app,
                           'slewTargetAltAz',
                           return_value=True):
        suc = app.moveAltAz()
        assert suc
