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
import pytest
from unittest import mock
import logging
# external packages
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount

# local import
from gui.mainWmixin.tabSettImaging import SettImaging
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget
from logic.camera.camera import Camera
from logic.focuser.focuser import Focuser
from logic.filter.filter import Filter
from logic.cover.cover import Cover
from logic.telescope.telescope import Telescope


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, Test1, app

    class Test1(QObject):
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        update1s = pyqtSignal()
        threadPool = QThreadPool()

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        message = pyqtSignal(str, int)
        camera = Camera(app=Test1())
        focuser = Focuser(app=Test1())
        filter = Filter(app=Test1())
        telescope = Telescope(app=Test1())
        cover = Cover(app=Test1())

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = SettImaging(app=Test(), ui=ui,
                      clickable=MWidget().clickable)
    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.guiSetText = MWidget().guiSetText
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    app.log = logging.getLogger(__name__)
    yield


def test_initConfig_1():
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_updateParameters_1():
    suc = app.updateParameters()
    assert suc


def test_updateParameters_2():
    app.app.camera.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = 1
    app.app.camera.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = 1
    app.app.camera.data['CCD_INFO.CCD_MAX_X'] = 1
    app.app.camera.data['CCD_INFO.CCD_MAX_Y'] = 1
    app.app.camera.data['CCD_COOLER.COOLER_ON'] = True
    app.app.camera.data['READOUT_QUALITY.QUALITY_LOW'] = True
    app.app.camera.data['FILTER_SLOT.FILTER_SLOT_VALUE'] = None

    app.ui.checkAutomaticTelescope.setChecked(True)
    with mock.patch.object(app,
                           'updateTelescopeParametersToGui'):
        suc = app.updateParameters()
        assert suc


def test_updateParameters_3():
    app.app.camera.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = 1
    app.app.camera.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = 1
    app.app.camera.data['CCD_INFO.CCD_MAX_X'] = 1
    app.app.camera.data['CCD_INFO.CCD_MAX_Y'] = 1
    app.app.camera.data['CCD_COOLER.COOLER_ON'] = True
    app.app.camera.data['READOUT_QUALITY.QUALITY_LOW'] = True
    app.app.camera.data['FILTER_SLOT.FILTER_SLOT_VALUE'] = 0
    app.ui.checkAutomaticTelescope.setChecked(False)
    app.ui.aperture.setValue(0)
    app.ui.focalLength.setValue(0)
    with mock.patch.object(app,
                           'updateTelescopeParametersToGui'):
        suc = app.updateParameters()
        assert suc


def test_updateTelescopeParametersToGui_1():
    app.app.telescope.data['TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH'] = 1
    app.app.telescope.data['TELESCOPE_INFO.TELESCOPE_APERTURE'] = 1

    suc = app.updateTelescopeParametersToGui()
    assert suc


def test_setCoolerTemp_1():
    with mock.patch.object(QMessageBox,
                           'critical'):
        suc = app.setCoolerTemp()
        assert not suc


def test_setCoolerTemp_2():
    app.app.camera.data['CAN_SET_CCD_TEMPERATURE'] = False
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = app.setCoolerTemp()
            assert not suc


def test_setCoolerTemp_3():
    app.app.camera.data['CAN_SET_CCD_TEMPERATURE'] = True
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            suc = app.setCoolerTemp()
            assert not suc


def test_setCoolerTemp_4():
    app.app.camera.data['CAN_SET_CCD_TEMPERATURE'] = True
    app.app.camera.data['CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE'] = 10
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            suc = app.setCoolerTemp()
            assert suc


def test_setCoolerTemp_5():
    app.app.camera.data['CAN_SET_CCD_TEMPERATURE'] = True
    app.app.camera.data['CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE'] = 10
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = app.setCoolerTemp()
            assert not suc


def test_setGain_1():
    with mock.patch.object(QMessageBox,
                           'critical'):
        suc = app.setGain()
        assert not suc


def test_setGain_2():
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            suc = app.setGain()
            assert not suc


def test_setGain_3():
    app.app.camera.data['CCD_GAIN.GAIN'] = 10
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            suc = app.setGain()
            assert suc


def test_setGain_4():
    app.app.camera.data['CCD_GAIN.GAIN'] = 10
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = app.setGain()
            assert not suc


def test_setOffset_1():
    with mock.patch.object(QMessageBox,
                           'critical'):
        suc = app.setOffset()
        assert not suc


def test_setOffset_2():
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            suc = app.setOffset()
            assert not suc


def test_setOffset_3():
    app.app.camera.data['CCD_OFFSET.OFFSET'] = 10
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            suc = app.setOffset()
            assert suc


def test_setOffset_4():
    app.app.camera.data['CCD_OFFSET.OFFSET'] = 10
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = app.setOffset()
            assert not suc


def test_setFilterNumber_1():
    with mock.patch.object(QMessageBox,
                           'critical'):
        suc = app.setFilterNumber()
        assert not suc


def test_setFilterNumber_2():
    app.app.filter.data['FILTER_SLOT.FILTER_SLOT_VALUE'] = 10
    app.app.filter.data['FILTER_NAME.FILTER_SLOT_NAME_0'] = 'test'
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = app.setFilterNumber()
            assert not suc


def test_setFilterNumber_3():
    app.app.filter.data['FILTER_SLOT.FILTER_SLOT_VALUE'] = 10
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            suc = app.setFilterNumber()
            assert suc


def test_setFilterName_1():
    with mock.patch.object(QMessageBox,
                           'critical'):
        suc = app.setFilterName()
        assert not suc


def test_setFilterName_2():
    app.app.filter.data['FILTER_SLOT.FILTER_SLOT_VALUE'] = 10
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getItem',
                               return_value=(10, False)):
            suc = app.setFilterName()
            assert not suc


def test_setFilterName_3():
    app.app.filter.data['FILTER_SLOT.FILTER_SLOT_VALUE'] = 1
    app.app.filter.data['FILTER_NAME.FILTER_SLOT_NAME_0'] = 'test1'
    app.app.filter.data['FILTER_NAME.FILTER_SLOT_NAME_1'] = 'test2'
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getItem',
                               return_value=('test1', True)):
            suc = app.setFilterName()
            assert suc


def test_setFilterName_4():
    app.app.filter.data['FILTER_SLOT.FILTER_SLOT_VALUE'] = 1
    app.app.filter.data['FILTER_NAME.FILTER_SLOT_NAME_1'] = 'test1'
    app.app.filter.data['FILTER_NAME.FILTER_SLOT_NAME_2'] = 'test2'
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getItem',
                               return_value=('test1', True)):
            suc = app.setFilterName()
            assert suc


def test_setDownloadModeFast():
    suc = app.setDownloadModeFast()
    assert suc


def test_setDownloadModeSlow():
    suc = app.setDownloadModeSlow()
    assert suc


def test_setCoolerOn_1():
    suc = app.setCoolerOn()
    assert suc


def test_setCoolerOff_1():
    suc = app.setCoolerOff()
    assert suc


def test_updateCoverStatGui_1():
    app.app.cover.data['CAP_PARK.PARK'] = True
    suc = app.updateCoverStatGui()
    assert suc


def test_updateCoverStatGui_2():
    app.app.cover.data['CAP_PARK.PARK'] = False
    suc = app.updateCoverStatGui()
    assert suc


def test_updateCoverStatGui_3():
    app.app.cover.data['CAP_PARK.PARK'] = None
    suc = app.updateCoverStatGui()
    assert suc


def test_updateCoverLightGui_1():
    app.app.cover.data['FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON'] = True
    suc = app.updateCoverLightGui()
    assert suc


def test_updateCoverLightGui_2():
    app.app.cover.data['FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON'] = False
    suc = app.updateCoverLightGui()
    assert suc


def test_updateCoverLightGui_3():
    app.app.cover.data['FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON'] = None
    suc = app.updateCoverLightGui()
    assert suc


def test_setCoverPark_1():
    with mock.patch.object(app.app.cover,
                           'closeCover',
                           return_value=False):
        suc = app.setCoverPark()
        assert not suc


def test_setCoverPark_2():
    with mock.patch.object(app.app.cover,
                           'closeCover',
                           return_value=True):
        suc = app.setCoverPark()
        assert suc


def test_setCoverUnpark_1():
    with mock.patch.object(app.app.cover,
                           'openCover',
                           return_value=False):
        suc = app.setCoverUnpark()
        assert not suc


def test_setCoverUnpark_2():
    with mock.patch.object(app.app.cover,
                           'openCover',
                           return_value=True):
        suc = app.setCoverUnpark()
        assert suc


def test_setCoverHalt_1():
    with mock.patch.object(app.app.cover,
                           'haltCover',
                           return_value=False):
        suc = app.setCoverHalt()
        assert not suc


def test_setCoverHalt_2():
    with mock.patch.object(app.app.cover,
                           'haltCover',
                           return_value=True):
        suc = app.setCoverHalt()
        assert suc


def test_moveFocuserIn_1():
    with mock.patch.object(app.app.focuser,
                           'move',
                           return_value=False):
        suc = app.moveFocuserIn()
        assert not suc


def test_moveFocuserIn_2():
    with mock.patch.object(app.app.focuser,
                           'move',
                           return_value=True):
        suc = app.moveFocuserIn()
        assert suc


def test_moveFocuserOut_1():
    with mock.patch.object(app.app.focuser,
                           'move',
                           return_value=False):
        suc = app.moveFocuserOut()
        assert not suc


def test_moveFocuserOut_2():
    with mock.patch.object(app.app.focuser,
                           'move',
                           return_value=True):
        suc = app.moveFocuserOut()
        assert suc


def test_haltFocuser_1():
    with mock.patch.object(app.app.focuser,
                           'halt',
                           return_value=False):
        suc = app.haltFocuser()
        assert not suc


def test_haltFocuser_2():
    with mock.patch.object(app.app.focuser,
                           'halt',
                           return_value=True):
        suc = app.haltFocuser()
        assert suc


def test_switchLightOn_1():
    with mock.patch.object(app.app.cover,
                           'lightOn',
                           return_value=False):
        suc = app.switchLightOn()
        assert not suc


def test_switchLightOn_2():
    with mock.patch.object(app.app.cover,
                           'lightOn',
                           return_value=True):
        suc = app.switchLightOn()
        assert suc


def test_switchLightOff_1():
    with mock.patch.object(app.app.cover,
                           'lightOff',
                           return_value=False):
        suc = app.switchLightOff()
        assert not suc


def test_switchLightOff_2():
    with mock.patch.object(app.app.cover,
                           'lightOff',
                           return_value=True):
        suc = app.switchLightOff()
        assert suc


def test_setLightIntensity_1():
    with mock.patch.object(QMessageBox,
                           'critical'):
        suc = app.setLightIntensity()
        assert not suc


def test_setLightIntensity_2():
    app.app.cover.data['FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE'] = 10
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = app.setLightIntensity()
            assert not suc


def test_setLightIntensity_3():
    app.app.cover.data['FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE'] = 10
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(app.app.cover,
                                   'lightIntensity',
                                   return_value=False):
                suc = app.setLightIntensity()
                assert not suc


def test_setLightIntensity_4():
    app.app.cover.data['FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE'] = 10
    with mock.patch.object(QMessageBox,
                           'critical'):
        with mock.patch.object(QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(app.app.cover,
                                   'lightIntensity',
                                   return_value=True):
                suc = app.setLightIntensity()
                assert suc
