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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import os
# external packages
from astropy.io import fits
# local import
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_initConfig_1():
    app.config['mainW'] = {}
    suc = app.mainW.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['mainW']
    suc = app.mainW.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_setupIcons():
    suc = app.mainW.setupIcons()
    assert suc


def test_selectorGui():
    suc = app.mainW.setupSelectorGui()
    assert suc
    for _, ui in app.mainW.selectorsDropDowns.items():
        assert ui.count() == 7


def test_getNumberFiles_1():
    number = app.mainW.getNumberFiles()
    assert number == 0


def test_getNumberFiles_2():
    number = app.mainW.getNumberFiles(pathDir='/Users')
    assert number == 0


def test_getNumberFiles_3():
    number = app.mainW.getNumberFiles(pathDir='/Users/mw/PycharmProjects', search='**/*.fit*')
    assert number > 0


def test_getNumberFiles_4():
    number = app.mainW.getNumberFiles(pathDir='/xxx', search='**/*.fit*')
    assert number == 0


def test_getNumberFiles_5():
    number = app.mainW.getNumberFiles(pathDir=app.mwGlob['imageDir'], search='**/*.fit*')
    assert number == 3


def test_getNumberFiles_6():
    number = app.mainW.getNumberFiles(pathDir=app.mwGlob['imageDir'], search='*.fit*')
    assert number == 3


def test_convertHeaderEntry_1():
    chunk = app.mainW.convertHeaderEntry(entry='', fitsKey='')
    assert not chunk


def test_convertHeaderEntry_2():
    chunk = app.mainW.convertHeaderEntry(entry='2019-05-26T17:02:18.843', fitsKey='')
    assert not chunk


def test_convertHeaderEntry_3():
    chunk = app.mainW.convertHeaderEntry(entry='2019-05-26T17:02:18.843', fitsKey='DATE-OBS')
    assert chunk == '2019-05-26-17-02-18'


def test_convertHeaderEntry_4():
    chunk = app.mainW.convertHeaderEntry(entry='2019-05-26T17:02:18', fitsKey='DATE-OBS')
    assert chunk == '2019-05-26-17-02-18'


def test_convertHeaderEntry_5():
    chunk = app.mainW.convertHeaderEntry(fitsKey='DATE-OBS')
    assert not chunk


def test_convertHeaderEntry_6():
    chunk = app.mainW.convertHeaderEntry(fitsKey='XXX')
    assert not chunk


def test_processSelectors_1():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('DATE-OBS', '2019-05-26T17:02:18.843')
    name = app.mainW.processSelectors(fitsHeader=header)
    assert not name


def test_processSelectors_2():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('DATE-OBS', '2019-05-26T17:02:18.843')
    name = app.mainW.processSelectors(fitsHeader=header, selection='Frame')
    assert not name


def test_processSelectors_3():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('DATE-OBS', '2019-05-26T17:02:18.843')
    name = app.mainW.processSelectors(fitsHeader=header, selection='Datetime')
    assert name == '2019-05-26-17-02-18'


def test_processSelectors_4():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('DATE-OBS', '2019-05-26T17:02:18.843')
    name = app.mainW.processSelectors(selection='Datetime')
    assert not name


def test_renameFile_1():
    suc = app.mainW.renameFile()
    assert not suc


def test_renameFile_2():
    with mock.patch.object(os,
                           'rename'):
        suc = app.mainW.renameFile(app.mwGlob['imageDir'] + '/m51.fit')
        assert suc


def test_renameRunGUI_1(qtbot):
    app.mainW.ui.renameDir.setText('')
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.renameRunGUI()
        assert not suc
    assert ['No valid input directory given', 2] == blocker.args


def test_renameRunGUI_2(qtbot):
    app.mainW.ui.renameDir.setText(app.mwGlob['tempDir'])
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.renameRunGUI()
        assert not suc
    assert ['No files to rename', 0] == blocker.args


def test_renameRunGUI_3(qtbot):
    app.mainW.ui.renameDir.setText(app.mwGlob['imageDir'])
    with mock.patch.object(app.mainW,
                           'renameFile',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.renameRunGUI()
            assert suc
        assert ['3 images were renamed', 0] == blocker.args


def test_slewParkPos_1(qtbot):
    class Test:
        @staticmethod
        def text():
            return '1'
    buttons = range(0, 8)
    alt = [Test(), Test(), Test(), Test(), Test(), Test(), Test(), Test()]
    az = [Test(), Test(), Test(), Test(), Test(), Test(), Test(), Test()]
    app.mainW.posButtons = buttons
    app.mainW.posAlt = alt
    app.mainW.posAz = az

    with mock.patch.object(app.mount.obsSite,
                           'slewAltAz',
                           return_value=True):
        for button in buttons:
            with mock.patch.object(app.mainW,
                                   'sender',
                                   return_value=button):
                suc = app.mainW.slewToParkPos()
                assert suc


def test_slewParkPos_2(qtbot):
    buttons = str(range(0, 8))
    app.mainW.posButtons = buttons
    with mock.patch.object(app.mount.obsSite,
                           'slewAltAz',
                           return_value=False):
        for button in buttons:
            with mock.patch.object(app.mainW,
                                   'sender',
                                   return_value=button):
                suc = app.mainW.slewToParkPos()
                assert not suc


def test_slewParkPos_3(qtbot):
    buttons = range(0, 8)
    app.mainW.posButtons = buttons
    with mock.patch.object(app.mount.obsSite,
                           'slewAltAz',
                           return_value=False):
        with mock.patch.object(app.mainW,
                               'sender',
                               return_value=None):
            suc = app.mainW.slewToParkPos()
            assert not suc


def test_slewParkPos_4(qtbot):
    class Test:
        @staticmethod
        def text():
            return '1'
    buttons = range(0, 8)
    alt = [Test(), Test(), Test(), Test(), Test(), Test(), Test(), Test()]
    az = [Test(), Test(), Test(), Test(), Test(), Test(), Test(), Test()]
    app.mainW.posButtons = buttons
    app.mainW.posAlt = alt
    app.mainW.posAz = az

    with qtbot.waitSignal(app.message) as blocker:
        with mock.patch.object(app.mount.obsSite,
                               'slewAltAz',
                               return_value=True):
            for button in buttons:
                with mock.patch.object(app.mainW,
                                       'sender',
                                       return_value=button):
                    suc = app.mainW.slewToParkPos()
                    assert suc
            assert ['Slew to [Park Pos 0]', 0] == blocker.args


def test_slewParkPos_5(qtbot):
    class Test:
        @staticmethod
        def text():
            return '1'
    buttons = range(0, 8)
    alt = [Test(), Test(), Test(), Test(), Test(), Test(), Test(), Test()]
    az = [Test(), Test(), Test(), Test(), Test(), Test(), Test(), Test()]
    app.mainW.posButtons = buttons
    app.mainW.posAlt = alt
    app.mainW.posAz = az

    with qtbot.waitSignal(app.message) as blocker:
        with mock.patch.object(app.mount.obsSite,
                               'slewAltAz',
                               return_value=False):
            for button in buttons:
                with mock.patch.object(app.mainW,
                                       'sender',
                                       return_value=button):
                    suc = app.mainW.slewToParkPos()
                    assert not suc
            assert ['Cannot slew to [Park Pos 0]', 2] == blocker.args
