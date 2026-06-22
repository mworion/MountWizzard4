############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################

import PySide6
import pytest
import requests
import time
from mw4.logic.powerswitch.kmRelay import KMRelay
from unittest import mock


@pytest.fixture()
def kmRelay() -> KMRelay:
    """Create a KMRelay instance with mocked app."""
    app = mock.MagicMock()
    with mock.patch.object(PySide6.QtCore.QTimer, "start"):
        relay = KMRelay(app)
    return relay


def test_getRelayWithDebugOutput(kmRelay: KMRelay) -> None:
    class MockResult:
        text = "test response"
        reason = "OK"
        status_code = 200
        elapsed = "0.1s"
        url = "http://localhost/status.xml"

    kmRelay.config.hostAddress = "localhost"
    kmRelay.config.user = "test"
    kmRelay.config.password = "test"
    with mock.patch.object(requests, "get", return_value=MockResult()):
        result = kmRelay.getRelay("/status.xml", debug=True)
        assert result is not None
        assert result.reason == "OK"


def test_startCommunicationWithoutHostAddress(kmRelay: KMRelay) -> None:
    kmRelay.config.hostAddress = ""
    kmRelay.startCommunication()
    assert kmRelay.deviceConnected is False


def test_startCommunicationWithHostAddress(kmRelay: KMRelay) -> None:
    kmRelay.config.hostAddress = "localhost"
    kmRelay.startCommunication()
    assert kmRelay.deviceConnected is False


def test_stopCommunication(kmRelay: KMRelay) -> None:
    kmRelay.deviceConnected = True
    kmRelay.stopCommunication()
    assert kmRelay.deviceConnected is False


def test_debugOutputWithValidResult(kmRelay: KMRelay) -> None:
    class MockResult:
        reason = "OK"
        status_code = 200
        elapsed = "0.1s"
        text = "test\r\nresponse"
        url = "http://localhost/status.xml"

    kmRelay.debugOutput(MockResult())


def test_debugOutputWithNone(kmRelay: KMRelay) -> None:
    kmRelay.debugOutput(None)


def test_getRelayWithNoneHostAddress(kmRelay: KMRelay) -> None:
    kmRelay.config.hostAddress = None
    result = kmRelay.getRelay("/status.xml", False)
    assert result == ""


def test_getRelayWithLockedMutex(kmRelay: KMRelay) -> None:
    kmRelay.config.hostAddress = "localhost"
    kmRelay.mutexPoll.lock()
    result = kmRelay.getRelay("/status.xml", False)
    assert result == ""
    kmRelay.mutexPoll.unlock()


def test_getRelayWithTimeoutException(kmRelay: KMRelay) -> None:
    kmRelay.config.hostAddress = "localhost"
    with mock.patch.object(requests, "get", side_effect=requests.exceptions.Timeout):
        result = kmRelay.getRelay("/status.xml", False)
        assert result == ""


def test_getRelayWithConnectionError(kmRelay: KMRelay) -> None:
    kmRelay.config.hostAddress = "localhost"
    with mock.patch.object(requests, "get", side_effect=requests.exceptions.ConnectionError):
        result = kmRelay.getRelay("/status.xml", False)
        assert result == ""


def test_getRelayWithGenericException(kmRelay: KMRelay) -> None:
    kmRelay.config.hostAddress = "localhost"
    with mock.patch.object(requests, "get", side_effect=Exception("Test error")):
        result = kmRelay.getRelay("/status.xml", False)
        assert result == ""


def test_checkConnectedNotConnectedWithNone(kmRelay: KMRelay) -> None:
    kmRelay.deviceConnected = False
    result = kmRelay.checkConnected(None)
    assert result is False
    assert kmRelay.deviceConnected is False


def test_checkConnectedNotConnectedWithOK(kmRelay: KMRelay) -> None:
    class MockResult:
        reason = "OK"

    kmRelay.deviceConnected = False
    result = kmRelay.checkConnected(MockResult())
    assert result is True
    assert kmRelay.deviceConnected is True


def test_checkConnectedConnectedWithOK(kmRelay: KMRelay) -> None:
    class MockResult:
        reason = "OK"

    kmRelay.deviceConnected = True
    result = kmRelay.checkConnected(MockResult())
    assert result is True
    assert kmRelay.deviceConnected is True


def test_checkConnectedConnectedWithoutOK(kmRelay: KMRelay) -> None:
    class MockResult:
        reason = "NotFound"

    kmRelay.deviceConnected = True
    result = kmRelay.checkConnected(MockResult())
    assert result is False
    assert kmRelay.deviceConnected is False


def test_cyclePollingNotConnected(kmRelay: KMRelay) -> None:
    with (
        mock.patch.object(kmRelay, "getRelay", return_value=None),
        mock.patch.object(kmRelay, "checkConnected", return_value=False),
    ):
        kmRelay.cyclePolling()


def test_cyclePollingConnected(kmRelay: KMRelay) -> None:
    class MockResult:
        text = "<relay0>0</relay0>\n<relay1>1</relay1>"
        reason = "OK"

    with (
        mock.patch.object(kmRelay, "getRelay", return_value=MockResult()),
        mock.patch.object(kmRelay, "checkConnected", return_value=True),
    ):
        kmRelay.cyclePolling()


def test_cyclePollingParseXml(kmRelay: KMRelay) -> None:
    class MockResult:
        text = "<response>\n<relay1>0</relay1>\n<relay2>1</relay2>\n</response>"
        reason = "OK"

    with (
        mock.patch.object(kmRelay, "getRelay", return_value=MockResult()),
        mock.patch.object(kmRelay, "checkConnected", return_value=True),
    ):
        kmRelay.cyclePolling()
        assert kmRelay.status[0] == 0
        assert kmRelay.status[1] == 1


def test_statusAllZero(kmRelay: KMRelay) -> None:
    returnValue = """<response>
                     <relay1>0</relay1>
                     <relay2>0</relay2>
                     <relay3>0</relay3>
                     <relay4>0</relay4>
                     <relay5>0</relay5>
                     <relay6>0</relay6>
                     <relay7>0</relay7>
                     <relay8>0</relay8>
                     </response>"""

    class MockResult:
        text = returnValue
        reason = "OK"
        status_code = 200

    with mock.patch.object(kmRelay, "getRelay", return_value=MockResult()):
        for i in range(0, 8):
            kmRelay.set(i, False)
        kmRelay.cyclePolling()
        assert kmRelay.status == [0, 0, 0, 0, 0, 0, 0, 0]


def test_statusAllOne(kmRelay: KMRelay) -> None:
    returnValue = """<response>
                     <relay1>1</relay1>
                     <relay2>1</relay2>
                     <relay3>1</relay3>
                     <relay4>1</relay4>
                     <relay5>1</relay5>
                     <relay6>1</relay6>
                     <relay7>1</relay7>
                     <relay8>1</relay8>
                     </response>"""

    class MockResult:
        text = returnValue
        reason = "OK"
        status_code = 200

    with mock.patch.object(kmRelay, "getRelay", return_value=MockResult()):
        for i in range(0, 8):
            kmRelay.set(i, True)
        kmRelay.cyclePolling()
        assert kmRelay.status == [1, 1, 1, 1, 1, 1, 1, 1]


def test_statusAfterSwitch(kmRelay: KMRelay) -> None:
    returnValue = """<response>
                     <relay1>1</relay1>
                     <relay2>1</relay2>
                     <relay3>1</relay3>
                     <relay4>1</relay4>
                     <relay5>1</relay5>
                     <relay6>1</relay6>
                     <relay7>1</relay7>
                     <relay8>1</relay8>
                     </response>"""

    class MockResult:
        text = returnValue
        reason = "OK"
        status_code = 200

    with mock.patch.object(kmRelay, "getRelay", return_value=MockResult()):
        for i in range(0, 8):
            kmRelay.switch(i)
        kmRelay.cyclePolling()
        assert kmRelay.status == [1, 1, 1, 1, 1, 1, 1, 1]


def test_statusAfterPulse(kmRelay: KMRelay) -> None:
    returnValue = """<response>
                     <relay1>0</relay1>
                     <relay2>0</relay2>
                     <relay3>0</relay3>
                     <relay4>0</relay4>
                     <relay5>0</relay5>
                     <relay6>0</relay6>
                     <relay7>0</relay7>
                     <relay8>0</relay8>
                     </response>"""

    class MockResult:
        text = returnValue
        reason = "OK"
        status_code = 200

    with (
        mock.patch.object(kmRelay, "getRelay", return_value=MockResult()),
        mock.patch.object(time, "sleep"),
    ):
        for i in range(0, 8):
            kmRelay.pulse(i)
        kmRelay.cyclePolling()
        assert kmRelay.status == [0, 0, 0, 0, 0, 0, 0, 0]


def test_getByteOn(kmRelay: KMRelay) -> None:
    kmRelay.status = [False] * 8
    value = kmRelay.getByte(relayNumber=7, state=True)
    assert value == 0x80


def test_getByteOff(kmRelay: KMRelay) -> None:
    kmRelay.status = [True] * 8
    value = kmRelay.getByte(relayNumber=7, state=False)
    assert value == 0x7F


def test_getByteMixed(kmRelay: KMRelay) -> None:
    kmRelay.status = [True, False, True, False, True, False, True, False]
    value = kmRelay.getByte(relayNumber=0, state=False)
    assert value == 0x54


def test_pulseWithNoneResponse(kmRelay: KMRelay) -> None:
    with (
        mock.patch.object(kmRelay, "getRelay", return_value=None),
        mock.patch.object(time, "sleep"),
    ):
        kmRelay.pulse(7)


def test_pulseWithBadResponse(kmRelay: KMRelay) -> None:
    class MockResult:
        reason = "Failed"
        status_code = 500

    with (
        mock.patch.object(kmRelay, "getRelay", return_value=MockResult()),
        mock.patch.object(time, "sleep"),
    ):
        kmRelay.pulse(7)


def test_pulseWithGoodResponse(kmRelay: KMRelay) -> None:
    class MockResult:
        reason = "OK"
        status_code = 200

    with (
        mock.patch.object(kmRelay, "getRelay", return_value=MockResult()),
        mock.patch.object(time, "sleep"),
    ):
        kmRelay.pulse(7)


def test_switchWithNoneResponse(kmRelay: KMRelay) -> None:
    with mock.patch.object(kmRelay, "getRelay", return_value=None):
        kmRelay.switch(7)


def test_switchWithBadResponse(kmRelay: KMRelay) -> None:
    class MockResult:
        reason = "Failed"
        status_code = 500

    with mock.patch.object(kmRelay, "getRelay", return_value=MockResult()):
        kmRelay.switch(7)


def test_switchWithGoodResponse(kmRelay: KMRelay) -> None:
    class MockResult:
        reason = "OK"
        status_code = 200

    with mock.patch.object(kmRelay, "getRelay", return_value=MockResult()):
        kmRelay.switch(7)


def test_setWithNoneResponse(kmRelay: KMRelay) -> None:
    with mock.patch.object(kmRelay, "getRelay", return_value=None):
        kmRelay.set(7, True)


def test_setWithBadResponse(kmRelay: KMRelay) -> None:
    class MockResult:
        reason = "Failed"
        status_code = 500

    with mock.patch.object(kmRelay, "getRelay", return_value=MockResult()):
        kmRelay.set(7, True)


def test_setWithGoodResponse(kmRelay: KMRelay) -> None:
    class MockResult:
        reason = "OK"
        status_code = 200

    with mock.patch.object(kmRelay, "getRelay", return_value=MockResult()):
        kmRelay.set(7, False)


def test_initialization(kmRelay: KMRelay) -> None:
    assert kmRelay.framework == ""
    assert kmRelay.data == {}
    assert kmRelay.status == [0] * 8
    assert kmRelay.deviceConnected is False


def test_signals(kmRelay: KMRelay) -> None:
    assert hasattr(kmRelay.signals, "statusReady")
    assert hasattr(kmRelay.signals, "deviceConnected")
    assert hasattr(kmRelay.signals, "deviceDisconnected")
