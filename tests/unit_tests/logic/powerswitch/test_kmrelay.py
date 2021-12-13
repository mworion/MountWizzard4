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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import time
import pytest

# external packages
import PyQt5
import requests

# local import
from base.loggerMW import setupLogging
setupLogging()
from logic.powerswitch.kmRelay import KMRelay


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = KMRelay()
        yield


def test_startCommunication_1():
    app.host = None
    with mock.patch.object(app.timerTask,
                           'start'):
        suc = app.startCommunication()
        assert not suc


def test_startCommunications_2():
    app.hostaddress = 'localhost'
    with mock.patch.object(app.timerTask,
                           'start'):
        suc = app.startCommunication()
        assert suc


def test_stopTimers_1():
    with mock.patch.object(app.timerTask,
                           'stop',):
        suc = app.stopCommunication()
        assert suc


def test_debugOutput_1():
    suc = app.debugOutput()
    assert not suc


def test_debugOutput_2():
    class Test:
        reason = 'reason'
        status_code = 200
        elapsed = 1
        text = 'test'
        url = 'test'

    suc = app.debugOutput(Test())
    assert suc


def test_getRelay_1():
    app.hostaddress = None
    suc = app.getRelay()
    assert suc is None


def test_getRelay_2():
    app.hostaddress = 'localhost'
    app.mutexPoll.lock()
    suc = app.getRelay()
    assert suc is None
    app.mutexPoll.unlock()


def test_getRelay_3():
    app.hostaddress = 'localhost'
    with mock.patch.object(requests,
                           'get',
                           return_value=None,
                           side_effect=requests.exceptions.Timeout):
        suc = app.getRelay()
        assert suc is None


def test_getRelay_4():
    app.hostaddress = 'localhost'
    with mock.patch.object(requests,
                           'get',
                           return_value=None,
                           side_effect=requests.exceptions.ConnectionError):
        suc = app.getRelay()
        assert suc is None


def test_getRelay_5():
    app.hostaddress = 'localhost'
    with mock.patch.object(requests,
                           'get',
                           return_value=None,
                           side_effect=Exception()):
        suc = app.getRelay(debug=True)
        assert suc is None


def test_checkConnected_1():
    class Test:
        reason = 'NotOk'

    app.deviceConnected = True
    suc = app.checkConnected(None)
    assert not suc
    assert not app.deviceConnected


def test_checkConnected_2():
    class Test:
        reason = 'OK'

    app.deviceConnected = False
    suc = app.checkConnected(Test())
    assert suc
    assert app.deviceConnected


def test_checkConnected_3():
    class Test:
        reason = 'NotOk'

    app.deviceConnected = False
    suc = app.checkConnected(None)
    assert not suc
    assert not app.deviceConnected


def test_checkConnected_4():
    class Test:
        reason = 'OK'

    app.deviceConnected = True
    suc = app.checkConnected(Test())
    assert suc
    assert app.deviceConnected


def test_cyclePolling_1():
    app.user = 'test'
    app.password = 'test'
    app.hostaddress = 'localhost'
    with mock.patch.object(app,
                           'getRelay'):
        with mock.patch.object(app,
                               'checkConnected',
                               return_value=False):
            suc = app.cyclePolling()
            assert not suc


def test_cyclePolling_2():
    class Test:
        reason = 'NotOk'
        text = 'test'

    app.user = 'test'
    app.password = 'test'
    app.hostaddress = 'localhost'
    with mock.patch.object(app,
                           'getRelay',
                           return_value=Test()):
        with mock.patch.object(app,
                               'checkConnected',
                               return_value=True):
            suc = app.cyclePolling()
            assert suc


def test_cyclePolling_3():
    class Test:
        reason = 'OK'
        text = 'test'

    app.user = 'test'
    app.password = 'test'
    app.hostaddress = 'localhost'
    with mock.patch.object(app,
                           'getRelay',
                           return_value=Test()):
        with mock.patch.object(app,
                               'checkConnected',
                               return_value=True):
            suc = app.cyclePolling()
            assert suc


def test_status1(qtbot):
    returnValue = """<response>
                     <relay0>0</relay0>
                     <relay1>0</relay1>
                     <relay2>0</relay2>
                     <relay3>0</relay3>
                     <relay4>0</relay4>
                     <relay5>0</relay5>
                     <relay6>0</relay6>
                     <relay7>0</relay7>
                     <relay8>0</relay8>
                     </response>"""

    class Test:
        pass
    ret = Test()
    ret.text = returnValue
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):

        for i in range(0, 8):
            app.set(i, 0)

        with qtbot.waitSignal(app.signals.statusReady):
            app.cyclePolling()
        assert [0, 0, 0, 0, 0, 0, 0, 0] == app.status


def test_status2(qtbot):
    returnValue = """<response>
                     <relay0>1</relay0>
                     <relay1>1</relay1>
                     <relay2>1</relay2>
                     <relay3>1</relay3>
                     <relay4>1</relay4>
                     <relay5>1</relay5>
                     <relay6>1</relay6>
                     <relay7>1</relay7>
                     <relay8>1</relay8>
                     </response>"""

    class Test:
        pass
    ret = Test()
    ret.text = returnValue
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):

        for i in range(0, 8):
            app.set(i, 1)

        with qtbot.waitSignal(app.signals.statusReady):
            app.cyclePolling()
        assert [1, 1, 1, 1, 1, 1, 1, 1] == app.status


def test_status3(qtbot):
    returnValue = """<response>
                     <relay0>1</relay0>
                     <relay1>1</relay1>
                     <relay2>1</relay2>
                     <relay3>1</relay3>
                     <relay4>1</relay4>
                     <relay5>1</relay5>
                     <relay6>1</relay6>
                     <relay7>1</relay7>
                     <relay8>1</relay8>
                     </response>"""

    class Test:
        pass
    ret = Test()
    ret.text = returnValue
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):

        for i in range(0, 8):
            app.switch(i)

        with qtbot.waitSignal(app.signals.statusReady):
            app.cyclePolling()
        assert [1, 1, 1, 1, 1, 1, 1, 1] == app.status


def test_status4(qtbot):
    returnValue = """<response>
                     <relay0>0</relay0>
                     <relay1>0</relay1>
                     <relay2>0</relay2>
                     <relay3>0</relay3>
                     <relay4>0</relay4>
                     <relay5>0</relay5>
                     <relay6>0</relay6>
                     <relay7>0</relay7>
                     <relay8>0</relay8>
                     </response>"""

    class Test:
        pass
    ret = Test()
    ret.text = returnValue
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):
        with mock.patch.object(time,
                               'sleep'):
            for i in range(0, 8):
                app.pulse(i)

            with qtbot.waitSignal(app.signals.statusReady):
                app.cyclePolling()
            assert [0, 0, 0, 0, 0, 0, 0, 0] == app.status


def test_getRelay_1(qtbot):
    app.mutexPoll.lock()
    suc = app.getRelay()
    app.mutexPoll.unlock()
    assert not suc


def test_getRelay_2(qtbot):
    app.hostaddress = None
    suc = app.getRelay()
    assert not suc


def test_getByte_1():
    relay = 7
    state = True
    app.status = [False] * 8

    value = app.getByte(relayNumber=relay, state=state)
    assert value == 0x80


def test_getByte_2():
    relay = 7
    state = False
    app.status = [True] * 8

    value = app.getByte(relayNumber=relay, state=state)
    assert value == 0x7F


def test_pulse_1(qtbot):
    ret = None

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):
        with mock.patch.object(time,
                               'sleep'):
            suc = app.pulse(7)
            assert not suc


def test_pulse_2(qtbot):
    class Test:
        pass
    ret = Test()
    ret.reason = 'False'
    ret.status_code = 200

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):
        with mock.patch.object(time,
                               'sleep'):
            suc = app.pulse(7)
            assert not suc


def test_pulse_3(qtbot):
    class Test:
        pass
    ret = Test()
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):
        with mock.patch.object(time,
                               'sleep'):
            suc = app.pulse(7)
            assert suc


def test_switch_1(qtbot):
    ret = None

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):
        suc = app.switch(7)
        assert not suc


def test_switch_2(qtbot):
    class Test:
        pass
    ret = Test()
    ret.reason = 'False'
    ret.status_code = 200

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):
        suc = app.switch(7)
        assert not suc


def test_switch_3(qtbot):
    class Test:
        pass
    ret = Test()
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):
        suc = app.switch(7)
        assert suc


def test_set_1(qtbot):
    ret = None

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):
        suc = app.set(7, True)
        assert not suc


def test_set_2(qtbot):
    class Test:
        pass
    ret = Test()
    ret.reason = 'False'
    ret.status_code = 200

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):
        suc = app.set(7, True)
        assert not suc


def test_set_3(qtbot):
    class Test:
        pass
    ret = Test()
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(app,
                           'getRelay',
                           return_value=ret):
        suc = app.set(7, False)
        assert suc
