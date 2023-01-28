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
# written in python3, (c) 2019-2023 by mworion
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
from logic.powerswitch.kmRelay import KMRelay
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        func = KMRelay()
        yield func


def test_startCommunication_1(function):
    function.host = None
    with mock.patch.object(function.timerTask,
                           'start'):
        suc = function.startCommunication()
        assert not suc


def test_startCommunications_2(function):
    function.hostaddress = 'localhost'
    with mock.patch.object(function.timerTask,
                           'start'):
        suc = function.startCommunication()
        assert suc


def test_stopTimers_1(function):
    with mock.patch.object(function.timerTask,
                           'stop',):
        suc = function.stopCommunication()
        assert suc


def test_debugOutput_1(function):
    suc = function.debugOutput()
    assert not suc


def test_debugOutput_2(function):
    class Test:
        reason = 'reason'
        status_code = 200
        elapsed = 1
        text = 'test'
        url = 'test'

    suc = function.debugOutput(Test())
    assert suc


def test_getRelay_1(function):
    function.hostaddress = None
    suc = function.getRelay()
    assert suc is None


def test_getRelay_2(function):
    function.hostaddress = 'localhost'
    function.mutexPoll.lock()
    suc = function.getRelay()
    assert suc is None
    function.mutexPoll.unlock()


def test_getRelay_3(function):
    function.hostaddress = 'localhost'
    with mock.patch.object(requests,
                           'get',
                           return_value=None,
                           side_effect=requests.exceptions.Timeout):
        suc = function.getRelay()
        assert suc is None


def test_getRelay_4(function):
    function.hostaddress = 'localhost'
    with mock.patch.object(requests,
                           'get',
                           return_value=None,
                           side_effect=requests.exceptions.ConnectionError):
        suc = function.getRelay()
        assert suc is None


def test_getRelay_5(function):
    function.hostaddress = 'localhost'
    with mock.patch.object(requests,
                           'get',
                           return_value=None,
                           side_effect=Exception()):
        suc = function.getRelay(debug=True)
        assert suc is None


def test_checkConnected_1(function):
    class Test:
        reason = 'NotOk'

    function.deviceConnected = True
    suc = function.checkConnected(None)
    assert not suc
    assert not function.deviceConnected


def test_checkConnected_2(function):
    class Test:
        reason = 'OK'

    function.deviceConnected = False
    suc = function.checkConnected(Test())
    assert suc
    assert function.deviceConnected


def test_checkConnected_3(function):
    class Test:
        reason = 'NotOk'

    function.deviceConnected = False
    suc = function.checkConnected(None)
    assert not suc
    assert not function.deviceConnected


def test_checkConnected_4(function):
    class Test:
        reason = 'OK'

    function.deviceConnected = True
    suc = function.checkConnected(Test())
    assert suc
    assert function.deviceConnected


def test_cyclePolling_1(function):
    function.user = 'test'
    function.password = 'test'
    function.hostaddress = 'localhost'
    with mock.patch.object(function,
                           'getRelay'):
        with mock.patch.object(function,
                               'checkConnected',
                               return_value=False):
            suc = function.cyclePolling()
            assert not suc


def test_cyclePolling_2(function):
    class Test:
        reason = 'NotOk'
        text = 'test'

    function.user = 'test'
    function.password = 'test'
    function.hostaddress = 'localhost'
    with mock.patch.object(function,
                           'getRelay',
                           return_value=Test()):
        with mock.patch.object(function,
                               'checkConnected',
                               return_value=True):
            suc = function.cyclePolling()
            assert suc


def test_cyclePolling_3(function):
    class Test:
        reason = 'OK'
        text = 'test'

    function.user = 'test'
    function.password = 'test'
    function.hostaddress = 'localhost'
    with mock.patch.object(function,
                           'getRelay',
                           return_value=Test()):
        with mock.patch.object(function,
                               'checkConnected',
                               return_value=True):
            suc = function.cyclePolling()
            assert suc


def test_status1(function):
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

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):

        for i in range(0, 8):
            function.set(i, 0)

        function.cyclePolling()
        assert [0, 0, 0, 0, 0, 0, 0, 0] == function.status


def test_status2(function):
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

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):

        for i in range(0, 8):
            function.set(i, 1)

        function.cyclePolling()
        assert [1, 1, 1, 1, 1, 1, 1, 1] == function.status


def test_status3(function):
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

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):

        for i in range(0, 8):
            function.switch(i)

        function.cyclePolling()
        assert [1, 1, 1, 1, 1, 1, 1, 1] == function.status


def test_status4(function):
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

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):
        with mock.patch.object(time,
                               'sleep'):
            for i in range(0, 8):
                function.pulse(i)

            function.cyclePolling()
            assert [0, 0, 0, 0, 0, 0, 0, 0] == function.status


def test_getRelay_1(function):
    function.mutexPoll.lock()
    suc = function.getRelay()
    function.mutexPoll.unlock()
    assert not suc


def test_getRelay_2(function):
    function.hostaddress = None
    suc = function.getRelay()
    assert not suc


def test_getByte_1(function):
    relay = 7
    state = True
    function.status = [False] * 8

    value = function.getByte(relayNumber=relay, state=state)
    assert value == 0x80


def test_getByte_2(function):
    relay = 7
    state = False
    function.status = [True] * 8

    value = function.getByte(relayNumber=relay, state=state)
    assert value == 0x7F


def test_pulse_1(function):
    ret = None

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):
        with mock.patch.object(time,
                               'sleep'):
            suc = function.pulse(7)
            assert not suc


def test_pulse_2(function):
    class Test:
        pass
    ret = Test()
    ret.reason = 'False'
    ret.status_code = 200

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):
        with mock.patch.object(time,
                               'sleep'):
            suc = function.pulse(7)
            assert not suc


def test_pulse_3(function):
    class Test:
        pass
    ret = Test()
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):
        with mock.patch.object(time,
                               'sleep'):
            suc = function.pulse(7)
            assert suc


def test_switch_1(function):
    ret = None

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):
        suc = function.switch(7)
        assert not suc


def test_switch_2(function):
    class Test:
        pass
    ret = Test()
    ret.reason = 'False'
    ret.status_code = 200

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):
        suc = function.switch(7)
        assert not suc


def test_switch_3(function):
    class Test:
        pass
    ret = Test()
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):
        suc = function.switch(7)
        assert suc


def test_set_1(function):
    ret = None

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):
        suc = function.set(7, True)
        assert not suc


def test_set_2(function):
    class Test:
        pass
    ret = Test()
    ret.reason = 'False'
    ret.status_code = 200

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):
        suc = function.set(7, True)
        assert not suc


def test_set_3(function):
    class Test:
        pass
    ret = Test()
    ret.reason = 'OK'
    ret.status_code = 200

    with mock.patch.object(function,
                           'getRelay',
                           return_value=ret):
        suc = function.set(7, False)
        assert suc
