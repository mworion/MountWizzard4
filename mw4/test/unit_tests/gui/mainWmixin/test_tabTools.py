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
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from astropy.io import fits
from mountcontrol.qtmount import Mount

# local import
from mw4.gui.mainWmixin.tabTools import Tools
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.widget import MWidget


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, app

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', expire=False, verbose=False,
                      pathToData='mw4/test/data')
        update1s = pyqtSignal()
        message = pyqtSignal(str, int)
        mwGlob = {'imageDir': 'mw4/test/image'}

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

    files = glob.glob('mw4/test/image/*.fit*')
    for f in files:
        os.remove(f)


def test_initConfig_1():
    app.app.config['mainW'] = {}
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_selectorGui():
    suc = app.setupSelectorGui()
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
    number = app.getNumberFiles(pathDir='mw4/test/testData', search='**/*.fit*')
    assert number == 2


def test_getNumberFiles_6():
    number = app.getNumberFiles(pathDir='mw4/test/testData', search='*.fit*')
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
    suc = app.renameFile('mw4/test/image/m51.fit')
    assert not suc


def test_renameFile_3():
    shutil.copy('mw4/test/testData/m51.fit', 'mw4/test/image/m51.fit')

    with mock.patch.object(os,
                           'rename'):
        suc = app.renameFile('mw4/test/image/m51.fit')
        assert suc


def test_renameRunGUI_1(qtbot):
    shutil.copy('mw4/test/testData/m51.fit', 'mw4/test/image/m51.fit')
    app.ui.renameDir.setText('')
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.renameRunGUI()
        assert not suc
    assert ['No valid input directory given', 2] == blocker.args


def test_renameRunGUI_2(qtbot):
    app.ui.renameDir.setText('mw4/test/image')
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.renameRunGUI()
        assert not suc
    assert ['No files to rename', 0] == blocker.args


def test_renameRunGUI_3(qtbot):
    app.ui.checkIncludeSubdirs.setChecked(True)
    app.ui.renameDir.setText('mw4/test/image')
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.renameRunGUI()
        assert not suc
    assert ['No files to rename', 0] == blocker.args


def test_renameRunGUI_4(qtbot):
    shutil.copy('mw4/test/testData/m51.fit', 'mw4/test/image/m51.fit')
    app.ui.renameDir.setText('mw4/test/image')
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


def test_moveNorth():
    with mock.patch.object(app.app.mount.obsSite,
                           'moveNorth',
                           return_value=True):
        suc = app.moveNorth()
        assert suc


def test_moveEast():
    with mock.patch.object(app.app.mount.obsSite,
                           'moveEast',
                           return_value=True):
        suc = app.moveEast()
        assert suc


def test_moveSouth():
    with mock.patch.object(app.app.mount.obsSite,
                           'moveSouth',
                           return_value=True):
        suc = app.moveSouth()
        assert suc


def test_moveWest():
    with mock.patch.object(app.app.mount.obsSite,
                           'moveWest',
                           return_value=True):
        suc = app.moveWest()
        assert suc


def test_moveNorthEast():
    with mock.patch.object(app.app.mount.obsSite,
                           'moveNorth',
                           return_value=True):
        with mock.patch.object(app.app.mount.obsSite,
                               'moveEast',
                               return_value=True):
            suc = app.moveNorthEast()
            assert suc


def test_moveSouthEast():
    with mock.patch.object(app.app.mount.obsSite,
                           'moveEast',
                           return_value=True):
        with mock.patch.object(app.app.mount.obsSite,
                               'moveEast',
                               return_value=True):
            suc = app.moveSouthEast()
            assert suc


def test_moveSouthWest():
    with mock.patch.object(app.app.mount.obsSite,
                           'moveSouth',
                           return_value=True):
        with mock.patch.object(app.app.mount.obsSite,
                               'moveWest',
                               return_value=True):
            suc = app.moveSouthWest()
            assert suc


def test_moveNorthWest():
    with mock.patch.object(app.app.mount.obsSite,
                           'moveWest',
                           return_value=True):
        with mock.patch.object(app.app.mount.obsSite,
                               'moveWest',
                               return_value=True):
            suc = app.moveNorthWest()
            assert suc


def test_stopMoveAll():
    with mock.patch.object(app.app.mount.obsSite,
                           'stopMoveAll',
                           return_value=True):
        suc = app.stopMoveAll()
        assert suc


def test_setSlewSpeed_1():
    def Sender():
        return ui.powerPort1

    app.sender = Sender

    suc = app.setSlewSpeed()
    assert suc


def test_setSlewSpeed_2():
    def Sender():
        return ui.slewSpeedMax
    app.sender = Sender

    def test():
        return

    app.slewSpeeds = {'max': app.ui.slewSpeedMax}
    app.slewSpeedFuncs = {'max': test}

    suc = app.setSlewSpeed()
    assert suc
