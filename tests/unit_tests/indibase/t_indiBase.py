############################################################
# -*- coding: utf-8 -*-
#
# INDIBASE
#
# GUI with PyQT5 for python
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
# external packages
import PyQt5
from PyQt5.QtTest import QTest
# local import
from indibase import indiBase
from indibase import indiXML

app = PyQt5.QtWidgets.QApplication([])
test = indiBase.Client()
testServer = 'localhost'

#
#
# testing main
#
#


def test_setServer1():
    test.setServer()
    assert ('', 7624) == test.host


def test_setServer2():
    test.setServer('heise.de')
    assert ('heise.de', 7624) == test.host


def test_setServer3():
    test.setServer('heise.de', 7624)
    assert ('heise.de', 7624) == test.host


def test_getHost_ok1():
    test.setServer('heise.de', 7624)
    assert test.getHost()


def test_getHost_ok2():
    test.setServer('localhost')
    assert 'localhost' == test.getHost()


def test_getHost_not_ok1():
    test = indiBase.Client()
    assert '' == test.getHost()


def test_getPort_ok1():
    test.setServer('heise.de', 7624)
    assert test.getPort()


def test_getPort_ok2():
    test.setServer('localhost')
    assert 7624 == test.getPort()


def test_getPort_ok3():
    test.setServer('localhost', 3000)
    assert 3000 == test.getPort()


def test_getPort_not_ok1():
    test = indiBase.Client()
    assert 0 == test.getPort()


def test_watchDevice1():
    call_ref = indiXML.clientGetProperties(indi_attr={'version': '1.7',
                                                      'device': 'test'})
    ret_val = True
    with mock.patch.object(test,
                           '_sendCmd',
                           return_value=ret_val):
        test.watchDevice('test')
        call_val = test._sendCmd.call_args_list[0][0][0]
        assert call_ref.toXML() == call_val.toXML()


def test_watchDevice2():
    call_ref = indiXML.clientGetProperties(indi_attr={'version': '1.7',
                                                      'device': ''})
    ret_val = True
    with mock.patch.object(test,
                           '_sendCmd',
                           return_value=ret_val):
        test.watchDevice()
        call_val = test._sendCmd.call_args_list[0][0][0]
        assert call_ref.toXML() == call_val.toXML()


def test_connectServer1(qtbot):
    test.setServer('')
    with qtbot.assertNotEmitted(test.signals.serverConnected):
        suc = test.connectServer()
        assert not suc
    test.disconnectServer()


def test_connectServer2(qtbot):
    test.setServer(testServer)
    with qtbot.waitSignal(test.signals.serverConnected) as blocker:
        suc = test.connectServer()
        assert suc
    assert [] == blocker.args
    test.disconnectServer()


def test_connectServer3(qtbot):
    test.setServer(testServer)
    test.connected = True
    with qtbot.waitSignal(test.signals.serverConnected) as blocker:
        suc = test.connectServer()
        assert suc
    assert [] == blocker.args
    test.disconnectServer()


def test_connectServer_not_ok1(qtbot):
    test.setServer('')
    suc = test.connectServer()
    assert not suc


def test_disconnectServer1(qtbot):
    test.setServer('')
    with qtbot.assertNotEmitted(test.signals.serverDisconnected):
        suc = test.disconnectServer()
        assert suc


def test_disconnectServer2(qtbot):
    test.setServer('localhost')
    test.connectServer()
    with qtbot.waitSignal(test.signals.serverDisconnected) as blocker:
        suc = test.disconnectServer()
        assert suc
    assert [] == blocker.args


def test_disconnectServer3(qtbot):
    test.setServer('localhost')
    with qtbot.assertNotEmitted(test.signals.serverDisconnected):
        suc = test.disconnectServer()
        assert suc


def test_disconnectServer4(qtbot):
    test.setServer('localhost')
    test.connectServer()
    test.watchDevice('CCD Simulator')
    QTest.qWait(500)
    test.connectDevice('CCD Simulator')
    with qtbot.waitSignal(test.signals.serverDisconnected):
        with qtbot.waitSignal(test.signals.removeDevice) as b:
            test.socket.close()
    assert ['CCD Simulator'] == b.args
    assert 0 == len(test.devices)


def test_isServerConnected1():
    test.setServer('localhost')
    test.connectServer()
    val = test.isServerConnected()
    assert val


def test_isServerConnected2():
    test.setServer('localhost')
    test.disconnectServer()
    val = test.isServerConnected()
    assert not val


def test_connectDevice1():
    test.setServer('localhost')
    test.connectServer()
    suc = test.connectDevice('')
    assert not suc
    test.disconnectServer()


def test_connectDevice2():
    test.setServer('localhost')
    suc = test.connectServer()
    assert suc
    suc = test.watchDevice('CCD Simulator')
    assert suc
    QTest.qWait(500)
    suc = test.connectDevice('CCD Simulator')
    assert suc
    test.disconnectServer()


def test_connectDevice3():
    test.setServer('localhost')
    suc = test.connectDevice('CCD Simulator')
    assert not suc


def test_disconnectDevice1():
    test.setServer('localhost')
    suc = test.connectServer()
    assert suc
    suc = test.watchDevice('CCD Simulator')
    assert suc
    QTest.qWait(500)
    suc = test.connectDevice('CCD Simulator')
    assert suc
    suc = test.disconnectDevice('CCD Simulator')
    assert suc
    test.disconnectServer()


def test_disconnectDevice2():
    test.setServer('localhost')
    suc = test.connectServer()
    assert suc
    suc = test.watchDevice('CCD Simulator')
    assert suc
    QTest.qWait(500)
    suc = test.connectDevice('CCD Simulator')
    assert suc
    suc = test.disconnectDevice('')
    assert not suc
    test.disconnectServer()


def test_disconnectDevice3():
    test.setServer('localhost')
    suc = test.connectServer()
    assert suc
    suc = test.watchDevice('CCD Simulator')
    assert suc
    QTest.qWait(500)
    suc = test.connectDevice('CCD Simulator')
    assert suc
    suc = test.disconnectDevice('Test')
    assert not suc
    test.disconnectServer()


def test_disconnectDevice4():
    suc = test.disconnectDevice('CCD Simulator')
    assert not suc


def test_getDevice1():
    dev = test.getDevice('')
    assert not dev


def test_getDevice2():
    test.setServer('localhost')
    test.connectServer()
    test.watchDevice('CCD Simulator')
    QTest.qWait(500)
    dev = test.getDevice('CCD Simulator')
    assert dev
    test.disconnectServer()


def test_getDevices1():
    test.setServer('localhost')
    test.connectServer()
    test.watchDevice('CCD Simulator')
    QTest.qWait(500)
    val = test.getDevices(test.CCD_INTERFACE)
    assert val
    assert 'CCD Simulator' in val
    test.disconnectServer()


def test_getDevices2():
    test.setServer('localhost')
    test.connectServer()
    test.watchDevice('CCD Simulator')
    QTest.qWait(500)
    val = test.getDevices(test.TELESCOPE_INTERFACE)
    assert val
    assert 'Telescope Simulator' not in val
    test.disconnectServer()


def test_getDevices3():
    test.setServer('localhost')
    val = test.getDevices(test.CCD_INTERFACE)
    assert not val
    test.disconnectServer()


def test_getDevices4():
    test.setServer('localhost')
    test.connectServer()
    test.watchDevice('CCD Simulator')
    QTest.qWait(500)
    val = test.getDevices()
    assert val
    assert 'CCD Simulator' in val
    test.disconnectServer()


def test_setBlobMode1():
    test.setServer('localhost')
    test.connectServer()
    call_ref = indiXML.enableBLOB('Never',
                                  indi_attr={'name': 'blob',
                                             'device': 'CCD Simulator'})
    test.watchDevice('CCD Simulator')
    QTest.qWait(500)
    ret_val = True
    with mock.patch.object(test,
                           '_sendCmd',
                           return_value=ret_val):
        suc = test.setBlobMode('Never',
                               'CCD Simulator',
                               'blob')
        assert suc
        call_val = test._sendCmd.call_args_list[0][0][0]
        assert call_ref.toXML() == call_val.toXML()
    test.disconnectServer()


def test_setBlobMode2():
    test.setServer('localhost')
    test.connectServer()
    call_ref = indiXML.enableBLOB('Never',
                                  indi_attr={'name': 'blob',
                                             'device': 'CCD Simulator'})
    test.watchDevice('CCD Simulator')
    QTest.qWait(500)
    ret_val = True
    with mock.patch.object(test,
                           '_sendCmd',
                           return_value=ret_val):
        suc = test.setBlobMode(deviceName='CCD Simulator',
                               propertyName='blob')
        assert suc
        call_val = test._sendCmd.call_args_list[0][0][0]
        assert call_ref.toXML() == call_val.toXML()
    test.disconnectServer()


def test_setBlobMode3():
    test.setServer('localhost')
    test.connectServer()
    test.watchDevice('CCD Simulator')
    QTest.qWait(500)
    ret_val = True
    with mock.patch.object(test,
                           '_sendCmd',
                           return_value=ret_val):
        suc = test.setBlobMode(deviceName='',
                               propertyName='blob')
        assert not suc
    test.disconnectServer()


def test_sendNewText1():
    test.setServer('localhost')
    test.connectServer()
    suc = test.watchDevice('CCD Simulator')
    assert suc
    QTest.qWait(500)
    suc = test.connectDevice('CCD Simulator')
    assert suc
    ret_val = True
    with mock.patch.object(test,
                           '_sendCmd',
                           return_value=ret_val):
        suc = test.sendNewText(deviceName='CCD Simulator',
                               propertyName='anna',
                               elements='blob',
                               text='TEST')
        assert not suc
    test.disconnectServer()


def test_sendNewText2():
    test.setServer('localhost')
    test.connectServer()
    call_ref = indiXML.newTextVector([indiXML.oneText('TEST',
                                                      indi_attr={'name': 'blob'})
                                      ],
                                     indi_attr={'name': 'CONNECTION',
                                                'device': 'CCD Simulator'})
    suc = test.watchDevice('CCD Simulator')
    assert suc
    QTest.qWait(500)
    suc = test.connectDevice('CCD Simulator')
    assert suc
    ret_val = True
    with mock.patch.object(test,
                           '_sendCmd',
                           return_value=ret_val):
        suc = test.sendNewText(deviceName='CCD Simulator',
                               propertyName='CONNECTION',
                               elements='blob',
                               text='TEST')
        assert suc
        call_val = test._sendCmd.call_args_list[0][0][0]
        assert call_ref.toXML() == call_val.toXML()
    test.disconnectServer()


def test_setNumber():
    test.setServer('localhost')
    test.connectServer()
    test.watchDevice('CCD Simulator')
    QTest.qWait(500)
    device = test.getDevice('CCD Simulator')
    numb = device.getNumber('CCD_FRAME')
    numb['X'] = 0
    numb['Y'] = 0
    numb['WIDTH'] = 3388
    numb['HEIGHT'] = 2712
    test.sendNewNumber(deviceName='CCD Simulator',
                       propertyName='CCD_FRAME',
                       elements=numb,
                       )
