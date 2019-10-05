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
import pytest
import unittest.mock as mock
# external packages
import PyQt5
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


def test_clearPowerGUI():
    suc = app.mainW.clearPowerGui()
    assert suc


def test_updatePowerGui():
    suc = app.mainW.updatePowerGui()
    assert suc


def test_setPowerNumber_1():
    app.power.device = None
    app.power.name = ''
    suc = app.mainW.setPowerNumber('test', '')
    assert not suc


def test_setPowerNumber_2():
    app.power.device = 1
    app.power.name = ''
    suc = app.mainW.setPowerNumber('test', '')
    assert not suc


def test_setPowerNumber_3():
    class Test:
        def getNumber(self, name):
            return {}
    app.power.device = Test()
    app.power.name = 'test'

    suc = app.mainW.setPowerNumber('test', '')
    assert suc


def test_setPowerNumber_4():
    class Test:
        def getNumber(self, name):
            return {'DEW_A': 123.5,
                    'DEW_B': 123.5,
                    }
    app.power.device = Test()
    app.power.name = 'test'

    suc = app.mainW.setPowerNumber('test', '')
    assert suc
    assert app.mainW.ui.dewA.text() == '124'
    assert app.mainW.ui.dewB.text() == '124'


def test_setPowerNumber_5():
    class Test:
        def getNumber(self, name):
            return {'DEW_A': 56.5,
                    'DEW_B': 41.5,
                    }
    app.power.device = Test()
    app.power.name = 'test'

    suc = app.mainW.setPowerNumber('test', '')
    assert suc
    assert app.mainW.ui.dewA.text() == ' 56'
    assert app.mainW.ui.dewB.text() == ' 42'


def test_setPowerSwitch_1():
    app.power.device = None
    app.power.name = ''
    suc = app.mainW.setPowerSwitch('test', '')
    assert not suc


def test_setPowerSwitch_2():
    app.power.device = 1
    app.power.name = ''
    suc = app.mainW.setPowerSwitch('test', '')
    assert not suc


def test_setPowerSwitch_3():
    class Test:
        def getSwitch(self, name):
            return {}
    app.power.device = Test()
    app.power.name = 'test'

    suc = app.mainW.setPowerSwitch('test', '')
    assert suc


def test_setPowerSwitch_4():
    class Test:
        def getSwitch(self, name):
            return {'ENABLED': True,
                    'AUTO_DEW_ENABLED': True,
                    }
    app.power.device = Test()
    app.power.name = 'test'
    app.mainW.ui.autoDew.setChecked(False)

    suc = app.mainW.setPowerSwitch('test', 'USB_PORT_CONTROL')
    assert suc
    assert not app.mainW.ui.autoDew.isChecked()


def test_setPowerSwitch_5():
    class Test:
        def getSwitch(self, name):
            return {'ENABLED': True,
                    'AUTO_DEW_ENABLED': True,
                    }
    app.power.device = Test()
    app.power.name = 'test'
    app.mainW.ui.autoDew.setChecked(False)

    suc = app.mainW.setPowerSwitch('test', 'AUTO_DEW')
    assert suc
    assert app.mainW.ui.autoDew.isChecked()


def test_setPowerText_1():
    app.power.device = None
    app.power.name = ''
    suc = app.mainW.setPowerSwitch('test', '')
    assert not suc


def test_setPowerText_2():
    app.power.device = 1
    app.power.name = ''
    suc = app.mainW.setPowerText('test', '')
    assert not suc


def test_setPowerText_3():
    class Test:
        def getText(self, name):
            return {}
    app.power.device = Test()
    app.power.name = 'test'

    suc = app.mainW.setPowerText('test', '')
    assert suc


def test_setPowerText_4():
    class Test:
        def getText(self, name):
            return {'POWER_LABEL_1': 'test1',
                    'POWER_LABEL_2': 'test2',
                    'POWER_LABEL_3': 'test3',
                    'POWER_LABEL_4': 'test4',
                    }
    app.power.device = Test()
    app.power.name = 'test'
    app.mainW.ui.powerLabel1.setText('')
    app.mainW.ui.powerLabel2.setText('')
    app.mainW.ui.powerLabel3.setText('')
    app.mainW.ui.powerLabel4.setText('')

    suc = app.mainW.setPowerText('test', '')
    assert suc
    assert app.mainW.ui.powerLabel1.text() == 'test1'
    assert app.mainW.ui.powerLabel2.text() == 'test2'
    assert app.mainW.ui.powerLabel3.text() == 'test3'
    assert app.mainW.ui.powerLabel4.text() == 'test4'


def test_sendDewA_1():
    app.power.device = None
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        suc = app.mainW.sendDewA()
        assert not suc


def test_sendDewA_2():
    class Test:
        def getNumber(self, name):
            return {}
    app.power.device = Test()
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        suc = app.mainW.sendDewA()
        assert suc


def test_sendDewB_1():
    app.power.device = None
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        suc = app.mainW.sendDewB()
        assert not suc


def test_sendDewB_2():
    class Test:
        def getNumber(self, name):
            return {}
    app.power.device = Test()
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        suc = app.mainW.sendDewB()
        assert suc


def test_sendPowerPort1_1():
    app.power.device = None
    suc = app.mainW.sendPowerPort1()
    assert not suc


def test_sendPowerPort1_2():
    class Test:
        def getSwitch(self, name):
            return {}
    app.power.device = Test()
    suc = app.mainW.sendPowerPort1()
    assert not suc


def test_sendPowerPort1_3():
    class Test:
        def getSwitch(self, name):
            return {'POWER_CONTROL_1': ''}
    app.power.device = Test()
    suc = app.mainW.sendPowerPort1()
    assert suc


def test_sendPowerPort2_1():
    app.power.device = None
    suc = app.mainW.sendPowerPort2()
    assert not suc


def test_sendPowerPort2_2():
    class Test:
        def getSwitch(self, name):
            return {}
    app.power.device = Test()
    suc = app.mainW.sendPowerPort2()
    assert not suc


def test_sendPowerPort2_3():
    class Test:
        def getSwitch(self, name):
            return {'POWER_CONTROL_2': ''}
    app.power.device = Test()
    suc = app.mainW.sendPowerPort2()
    assert suc


def test_sendPowerPort3_1():
    app.power.device = None
    suc = app.mainW.sendPowerPort3()
    assert not suc


def test_sendPowerPort3_2():
    class Test:
        def getSwitch(self, name):
            return {}
    app.power.device = Test()
    suc = app.mainW.sendPowerPort3()
    assert not suc


def test_sendPowerPort3_3():
    class Test:
        def getSwitch(self, name):
            return {'POWER_CONTROL_3': ''}
    app.power.device = Test()
    suc = app.mainW.sendPowerPort3()
    assert suc


def test_sendPowerPort4_1():
    app.power.device = None
    suc = app.mainW.sendPowerPort4()
    assert not suc


def test_sendPowerPort4_2():
    class Test:
        def getSwitch(self, name):
            return {}
    app.power.device = Test()
    suc = app.mainW.sendPowerPort4()
    assert not suc


def test_sendPowerPort4_3():
    class Test:
        def getSwitch(self, name):
            return {'POWER_CONTROL_4': ''}
    app.power.device = Test()
    suc = app.mainW.sendPowerPort4()
    assert suc


def test_sendPowerBootPort1_1():
    app.power.device = None
    suc = app.mainW.sendPowerBootPort1()
    assert not suc


def test_sendPowerBootPort1_2():
    class Test:
        def getSwitch(self, name):
            return {}
    app.power.device = Test()
    suc = app.mainW.sendPowerBootPort1()
    assert suc


def test_sendPowerBootPort2_1():
    app.power.device = None
    suc = app.mainW.sendPowerBootPort2()
    assert not suc


def test_sendPowerBootPort2_2():
    class Test:
        def getSwitch(self, name):
            return {}
    app.power.device = Test()
    suc = app.mainW.sendPowerBootPort2()
    assert suc


def test_sendPowerBootPort3_1():
    app.power.device = None
    suc = app.mainW.sendPowerBootPort3()
    assert not suc


def test_sendPowerBootPort3_2():
    class Test:
        def getSwitch(self, name):
            return {}
    app.power.device = Test()
    suc = app.mainW.sendPowerBootPort3()
    assert suc


def test_sendPowerBootPort4_1():
    app.power.device = None
    suc = app.mainW.sendPowerBootPort4()
    assert not suc


def test_sendPowerBootPort4_2():
    class Test:
        def getSwitch(self, name):
            return {}
    app.power.device = Test()
    suc = app.mainW.sendPowerBootPort4()
    assert suc


def test_sendHubUSB_1():
    app.power.device = None
    suc = app.mainW.sendHubUSB()
    assert not suc


def test_sendHubUSB_2():
    class Test:
        def getSwitch(self, name):
            return {}

        def sendNewSwitch(self, a, b, c):
            pass

    app.power.device = Test()
    suc = app.mainW.sendHubUSB()
    assert not suc


def test_sendHubUSB_3():
    class Test:
        def getSwitch(self, name):
            return {'ENABLED': True,
                    'DISABLED': False}

        def sendNewSwitch(self, a, b, c):
            pass

    app.power.device = Test()
    suc = app.mainW.sendHubUSB()
    assert suc


def test_sendAutoDew_1():
    app.power.device = None
    suc = app.mainW.sendAutoDew()
    assert not suc


def test_sendAutoDew_2():
    class Test:
        def getSwitch(self, name):
            return {}

        def sendNewSwitch(self, a, b, c):
            pass

    app.power.device = Test()
    app.mainW.ui.autoDew.setChecked(True)
    suc = app.mainW.sendAutoDew()
    assert suc
