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
# Python  v3.7.5
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

# external packages
import PyQt5.QtWidgets
import PyQt5.QtTest
import PyQt5.QtCore
from PyQt5.QtGui import QCloseEvent
from indibase.indiBase import Device

# local import
from mw4.gui.devicePopupW import DevicePopup
from mw4.base.indiClass import IndiClass
from mw4.gui.widget import MWidget


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app, data, geometry, framework
    data = {
        'telescope':
            {
                'indiNameList': ['test1', 'test2']
                }
            }
    geometry = [100, 100, 100, 100]
    framework = {'indi': 'test'}

    yield


def test_storeConfig_1(qtbot):
    app = DevicePopup(geometry=geometry,
                      data=data,
                      framework=framework,
                      driver='telescope',
                      deviceType='telescope')

    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    qtbot.addWidget(app)

    suc = app.storeConfig()
    assert suc


def test_closeEvent_1(qtbot):
    app = DevicePopup(geometry=geometry,
                      data=data,
                      framework=framework,
                      driver='telescope',
                      deviceType='telescope')
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    qtbot.addWidget(app)
    app.closeEvent(QCloseEvent())


def test_copyAllIndiSettings_1(qtbot):
    app = DevicePopup(geometry=geometry,
                      data=data,
                      framework=framework,
                      driver='telescope',
                      deviceType='telescope')
    qtbot.addWidget(app)

    suc = app.copyAllIndiSettings()
    assert suc


def test_copyAllAlpacaSettings_1(qtbot):
    app = DevicePopup(geometry=geometry,
                      data=data,
                      framework=framework,
                      driver='telescope',
                      deviceType='telescope')
    qtbot.addWidget(app)

    suc = app.copyAllAlpacaSettings()
    assert suc


def test_AddDevicesWithType_1(qtbot):
    app = DevicePopup(geometry=geometry,
                      data=data,
                      framework=framework,
                      driver='telescope',
                      deviceType='telescope')
    qtbot.addWidget(app)

    device = Device()
    app.indiClass = IndiClass()
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': None}):
        suc = app.addDevicesWithType('telescope', 'test')
        assert not suc


def test_AddDevicesWithType_2(qtbot):
    app = DevicePopup(geometry=geometry,
                      data=data,
                      framework=framework,
                      driver='telescope',
                      deviceType='telescope')
    qtbot.addWidget(app)

    device = Device()
    app.indiClass = IndiClass()
    app.indiClass.client.devices['telescope'] = device
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': None}):
        suc = app.addDevicesWithType('telescope', 'test')
        assert not suc


def test_AddDevicesWithType_3(qtbot):
    app = DevicePopup(geometry=geometry,
                      data=data,
                      framework=framework,
                      driver='telescope',
                      deviceType='telescope')
    qtbot.addWidget(app)

    device = Device()
    app.indiClass = IndiClass()
    app.indiClass.client.devices['telescope'] = device
    app.indiSearchType = None
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': 0}):
        suc = app.addDevicesWithType('telescope', 'test')
        assert not suc


def test_AddDevicesWithType_4(qtbot):
    app = DevicePopup(geometry=geometry,
                      data=data,
                      framework=framework,
                      driver='telescope',
                      deviceType='telescope')
    qtbot.addWidget(app)

    device = Device()
    app.indiClass = IndiClass()
    app.indiClass.client.devices['telescope'] = device
    app.indiSearchType = 1
    app.indiSearchNameList = list()
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': 1}):
        suc = app.addDevicesWithType('telescope', 'test')
        assert suc


def test_searchDevices_1(qtbot):
    app = DevicePopup(geometry=geometry,
                      data=data,
                      framework=framework,
                      driver='telescope',
                      deviceType='telescope')
    qtbot.addWidget(app)

    suc = app.searchDevices()
    assert suc


def test_searchDevices_2(qtbot):
    app = DevicePopup(geometry=geometry,
                      data=data,
                      framework=framework,
                      driver='telescope',
                      deviceType='telescope')
    qtbot.addWidget(app)

    app.driver = 'test'
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'information',
                           return_value=True):
        suc = app.searchDevices()
        assert suc
