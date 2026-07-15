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
import unittest.mock as mock
from mw4.mountcontrol.connection import Connection
from PySide6.QtCore import QByteArray


def makeClient(
    connected: bool = True,
    written: bool = True,
    readyRead: bool = True,
    data: bytes = b"",
) -> mock.MagicMock:
    """Create a mocked QTcpSocket with configurable blocking-call results."""
    client = mock.MagicMock()
    client.waitForConnected.return_value = connected
    client.waitForBytesWritten.return_value = written
    client.waitForReadyRead.return_value = readyRead
    client.readAll.return_value = QByteArray(data)
    return client


def makeParent(host=None, loggingTrace: bool = False) -> object:
    class Config:
        pass

    class Parent:
        pass

    p = Parent()
    p.loggingTrace = loggingTrace
    p.mountIsUp = True

    config = Config()
    if isinstance(host, tuple) and len(host) == 2:
        config.hostAddress = host[0]
        config.port = host[1]
    elif host is not None and not isinstance(host, tuple):
        config.hostAddress = host
        config.port = None
    else:
        config.hostAddress = None
        config.port = None

    p.config = config
    return p


class TestAnalyseCommand:
    """Tests for the analyseCommand method."""

    def test_responses_withoutCommand(self):
        conn = Connection(makeParent())
        chunksToReceive, getData, minBytes = conn.analyseCommand("")
        assert not getData
        assert minBytes == 0
        assert chunksToReceive == 0

    def test_responses_withoutCommand_1(self):
        conn = Connection(makeParent())
        chunksToReceive, getData, minBytes = conn.analyseCommand(":Q#")
        assert not getData
        assert minBytes == 0
        assert chunksToReceive == 0

    def test_responses_withoutCommand_2(self):
        conn = Connection(makeParent())
        chunksToReceive, getData, minBytes = conn.analyseCommand(":QaXa#")
        assert getData
        assert minBytes == 0
        assert chunksToReceive == 1

    def test_responses_withoutCommand_3(self):
        conn = Connection(makeParent())
        chunksToReceive, getData, minBytes = conn.analyseCommand(":Q#:QaXa#")
        assert getData
        assert minBytes == 0
        assert chunksToReceive == 1

    def test_responses_typeA(self):
        conn = Connection(makeParent())
        command = ":AP#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert not getData
        assert minBytes == 0
        assert chunksToReceive == 0

    def test_responses_typeB(self):
        conn = Connection(makeParent())
        command = ":FLIP#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert getData
        assert minBytes == 1
        assert chunksToReceive == 0

    def test_responses_typeC(self):
        conn = Connection(makeParent())
        command = ":GTMP1#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert getData
        assert minBytes == 0
        assert chunksToReceive == 1

    def test_responses_typeAB(self):
        conn = Connection(makeParent())
        command = ":AP#:FLIP#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert getData
        assert minBytes == 1
        assert chunksToReceive == 0

    def test_responses_typeAC(self):
        conn = Connection(makeParent())
        command = ":AP#:GTMP1#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert getData
        assert minBytes == 0
        assert chunksToReceive == 1

    def test_responses_typeBC(self):
        conn = Connection(makeParent())
        command = ":FLIP#:GTMP1#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert getData
        assert minBytes == 1
        assert chunksToReceive == 1

    def test_responses_typeABC(self):
        conn = Connection(makeParent())
        command = ":AP#:FLIP#:GTMP1#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert getData
        assert minBytes == 1
        assert chunksToReceive == 1

    def test_responses_typeABCABC(self):
        conn = Connection(makeParent())
        command = ":AP#:FLIP#:GTMP1#:AP#:FLIP#:GTMP1#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert getData
        assert minBytes == 2
        assert chunksToReceive == 2

    def test_responses_typeABBCCABC(self):
        conn = Connection(makeParent())
        command = ":AP#:FLIP#:FLIP#:GTMP1#:GTMP1#:AP#:FLIP#:GTMP1#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert getData
        assert minBytes == 3
        assert chunksToReceive == 3

    def test_responses_real(self):
        conn = Connection(makeParent())
        command = ":GTsid#:Ga#:Gz#:Gr#:Gd#:QaXa#:QaXb#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert getData
        assert minBytes == 1
        assert chunksToReceive == 6

    def test_responses_real_2(self):
        conn = Connection(makeParent())
        command = ":Suaf1#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert not getData
        assert minBytes == 0
        assert chunksToReceive == 0

    def test_responses_real_3(self):
        conn = Connection(makeParent())
        command = ":RC3#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert not getData
        assert minBytes == 0
        assert chunksToReceive == 0

    def test_responses_real_4(self):
        conn = Connection(makeParent())
        command = ":RG2#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert not getData
        assert minBytes == 0
        assert chunksToReceive == 0

    def test_responses_real_5(self):
        conn = Connection(makeParent())
        command = ":RG#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert not getData
        assert minBytes == 0
        assert chunksToReceive == 0

    def test_responses_real_6(self):
        conn = Connection(makeParent())
        command = ":RC#"
        chunksToReceive, getData, minBytes = conn.analyseCommand(command)
        assert not getData
        assert minBytes == 0
        assert chunksToReceive == 0

    def test_analyseCommand_loggingTrace(self):
        conn = Connection(makeParent(host=("localhost", 3492), loggingTrace=True))
        chunksToReceive, getData, minBytes = conn.analyseCommand(":AP#")
        assert not getData
        assert minBytes == 0
        assert chunksToReceive == 0


class TestCloseClientHard:
    """Tests for the closeClientHard method."""

    def test_closeClientHard_1(self):
        conn = Connection(makeParent())
        conn.closeClientHard("")

    def test_closeClientHard_2(self):
        conn = Connection(makeParent(host="test"))
        client = makeClient()
        client.abort.side_effect = Exception
        conn.closeClientHard(client)

    def test_closeClientHard_3(self):
        conn = Connection(makeParent(host="test"))
        client = makeClient()
        conn.closeClientHard(client)
        client.abort.assert_called_once()
        client.close.assert_called_once()


class TestBuildClient:
    """Tests for the buildClient method."""

    def test_buildClient_noHost(self):
        conn = Connection(makeParent(host=None))
        client = conn.buildClient()
        assert client is None

    def test_buildClient_hostNotTuple(self):
        conn = Connection(makeParent(host="localhost"))
        client = conn.buildClient()
        assert client is None

    def test_buildClient_mountNotUp(self):
        parent = makeParent(host=("localhost", 3492))
        parent.mountIsUp = False
        conn = Connection(parent)
        client = conn.buildClient()
        assert client is None

    def test_buildClient_emptyHost(self):
        conn = Connection(makeParent(host=None))
        conn.host = None
        client = conn.buildClient()
        assert client is None

    def test_buildClient_hostNotTuple_direct(self):
        conn = Connection(makeParent(host=None))
        conn.host = "not_a_tuple"
        client = conn.buildClient()
        assert client is None


class TestCommunicate:
    """Tests for the communicate method."""

    def test_ok(self):
        with mock.patch("mw4.mountcontrol.connection.QTcpSocket") as m_socket:
            m_socket.return_value = makeClient(data=b"10micron GM1000HPS#")
            conn = Connection(makeParent(host=("localhost", 3492)))
            suc, response, chunks = conn.communicate(":GVN#")
            m_socket.return_value.connectToHost.assert_called_with("localhost", 3492)
            m_socket.return_value.write.assert_called_with(b":GVN#")
        assert suc
        assert response[0] == "10micron GM1000HPS"

    def test_notok_response_check(self):
        with mock.patch("mw4.mountcontrol.connection.QTcpSocket") as m_socket:
            m_socket.return_value = makeClient(data=b"10micron GM1000HPS#")
            conn = Connection(makeParent(host=("localhost", 3492)))
            suc, response, chunks = conn.communicate(":GVN#", "0")
            m_socket.return_value.connectToHost.assert_called_with("localhost", 3492)
            m_socket.return_value.write.assert_called_with(b":GVN#")
        assert not suc
        assert response[0] == "10micron GM1000HPS"

    def test_no_host_defined(self):
        conn = Connection(makeParent(host=None))
        suc, response, chunks = conn.communicate(":GVN#")
        assert not suc
        assert response == []

    def test_no_port_defined(self):
        conn = Connection(makeParent(host="localhost"))
        suc, response, chunks = conn.communicate(":GVN#")
        assert not suc
        assert response == []

    def test_no_response(self):
        with mock.patch("mw4.mountcontrol.connection.QTcpSocket") as m_socket:
            m_socket.return_value = makeClient(data=b"10micron GM1000HPS#")
            conn = Connection(makeParent(host=("localhost", 3492)))
            suc, response, chunks = conn.communicate("")
        assert suc
        assert response == []

    def test_no_chunk(self):
        with mock.patch("mw4.mountcontrol.connection.QTcpSocket") as m_socket:
            m_socket.return_value = makeClient(data=b"")
            conn = Connection(makeParent(host=("localhost", 3492)))
            suc, response, chunks = conn.communicate("")
        assert suc
        assert response == []

    def test_connect_timeout(self):
        with mock.patch("mw4.mountcontrol.connection.QTcpSocket") as m_socket:
            m_socket.return_value = makeClient(connected=False)
            conn = Connection(makeParent(host=("localhost", 3492)))
            suc, response, chunks = conn.communicate(":GVN#")
        assert not suc

    def test_sendall_timeout(self):
        with mock.patch("mw4.mountcontrol.connection.QTcpSocket") as m_socket:
            m_socket.return_value = makeClient(written=False)
            conn = Connection(makeParent(host=("localhost", 3492)))
            suc, response, chunks = conn.communicate(":GVN#")
        assert not suc

    def test_recv_timeout(self):
        with mock.patch("mw4.mountcontrol.connection.QTcpSocket") as m_socket:
            m_socket.return_value = makeClient(readyRead=False)
            conn = Connection(makeParent(host=("localhost", 3492)))
            suc, response, chunks = conn.communicate(":GVN#")
        assert not suc

    def test_connect_socket_error(self):
        with mock.patch("mw4.mountcontrol.connection.QTcpSocket") as m_socket:
            client = makeClient()
            client.connectToHost.side_effect = Exception
            m_socket.return_value = client
            conn = Connection(makeParent(host=("localhost", 3492)))
            suc, response, chunks = conn.communicate(":GVN#")
        assert not suc

    def test_sendall_exception(self):
        with mock.patch("mw4.mountcontrol.connection.QTcpSocket") as m_socket:
            client = makeClient()
            client.write.side_effect = Exception("Test")
            m_socket.return_value = client
            conn = Connection(makeParent(host=("localhost", 3492)))
            suc, response, chunks = conn.communicate(":GVN#")
        assert not suc

    def test_recv_exception(self):
        with mock.patch("mw4.mountcontrol.connection.QTcpSocket") as m_socket:
            client = makeClient(data=b"10micron GM1000HPS#")
            client.readAll.side_effect = Exception("Test")
            m_socket.return_value = client
            conn = Connection(makeParent(host=("localhost", 3492)))
            suc, response, chunks = conn.communicate(":GVN#")
        assert not suc

    def test_connect_exception(self):
        with mock.patch("mw4.mountcontrol.connection.QTcpSocket") as m_socket:
            client = makeClient()
            client.connectToHost.side_effect = Exception("Test")
            m_socket.return_value = client
            conn = Connection(makeParent(host=("localhost", 3492)))
            suc, response, chunks = conn.communicate(":GVN#")
        assert not suc


class TestCommandValidation:
    """Tests for command validation methods."""

    def test_commands_valid_A(self):
        conn = Connection(makeParent())
        for command in conn.COMMAND_A:
            assert command in conn.COMMANDS

    def test_commands_valid_B(self):
        conn = Connection(makeParent())
        for command in conn.COMMAND_B:
            assert command in conn.COMMANDS

    def test_valid_commandSet_1(self):
        conn = Connection(makeParent())
        suc = conn.validCommandSet(":AP#")
        assert suc

    def test_valid_commandSet_2(self):
        conn = Connection(makeParent())
        suc = conn.validCommandSet(":AP#:AP#:AP#")
        assert suc

    def test_valid_commandSet_3(self):
        conn = Connection(makeParent())
        suc = conn.validCommandSet(":AP#:AP#:AP#")
        assert suc

    def test_invalid_commandSet_1(self):
        conn = Connection(makeParent())
        suc = conn.validCommandSet(":test#")
        assert not suc

    def test_invalid_commandSet_2(self):
        conn = Connection(makeParent())
        suc = conn.validCommandSet(":AP#:test#")
        assert not suc

    def test_invalid_command_1(self):
        conn = Connection(makeParent())
        suc = conn.validCommand(":AP#")
        assert suc

    def test_invalid_command_2(self):
        conn = Connection(makeParent())
        suc = conn.validCommand(":test#")
        assert not suc

    def test_communicate_invalid_command_1(self):
        conn = Connection(makeParent())
        suc, msg, num = conn.communicate(":test#")
        assert not suc

    def test_communicate_invalid_command_2(self):
        conn = Connection(makeParent())
        suc, msg, num = conn.communicate(":AP#:test#")
        assert not suc


class TestReceiveData:
    """Tests for the receiveData method."""

    def test_receiveData_1(self):
        client = makeClient()
        client.readAll.side_effect = Exception
        conn = Connection(makeParent())
        val = conn.receiveData(client=client, numberOfChunks=0, minBytes=0)
        assert val == (False, [])

    def test_receiveData_2(self):
        client = makeClient(data=b"")
        conn = Connection(makeParent())
        val = conn.receiveData(client=client, numberOfChunks=0, minBytes=0)
        assert val == (True, [""])

    def test_receiveData_3(self):
        client = makeClient(data=b"12345")
        conn = Connection(makeParent())
        val = conn.receiveData(client=client, numberOfChunks=0, minBytes=5)
        assert val == (True, ["12345"])

    def test_receiveData_multipleChunks(self):
        client = makeClient(data=b"a#b#")
        conn = Connection(makeParent())
        val = conn.receiveData(client=client, numberOfChunks=2, minBytes=0)
        assert val == (True, ["a", "b"])

    def test_receiveData_timeout_loggingTrace(self):
        conn = Connection(makeParent(loggingTrace=True))
        client = makeClient(readyRead=False)
        val = conn.receiveData(client=client, numberOfChunks=1, minBytes=0)
        assert val == (False, [])

    def test_receiveData_success_loggingTrace(self):
        conn = Connection(makeParent(loggingTrace=True))
        client = makeClient(data=b"result#")
        val = conn.receiveData(client=client, numberOfChunks=1, minBytes=0)
        assert val == (True, ["result"])


class TestCommunicateRaw:
    """Tests for the communicateRaw method."""

    def test_communicateRaw_0(self):
        conn = Connection(makeParent())
        with (
            mock.patch.object(conn, "buildClient", return_value=None),
            mock.patch.object(conn, "sendData", return_value=False),
        ):
            suc = conn.communicateRaw("test")
            assert not suc[0]
            assert not suc[1]
            assert suc[2] == "Socket error"

    def test_communicateRaw_1(self):
        client = makeClient(readyRead=False)
        conn = Connection(makeParent())
        with (
            mock.patch.object(conn, "buildClient", return_value=client),
            mock.patch.object(conn, "sendData", return_value=False),
        ):
            suc = conn.communicateRaw("test")
            assert not suc[0]
            assert not suc[1]
            assert suc[2] == "Timeout"
        client.abort.assert_called_once()
        client.close.assert_called_once()

    def test_communicateRaw_2(self):
        client = makeClient()
        client.readAll.side_effect = Exception
        conn = Connection(makeParent())
        with (
            mock.patch.object(conn, "buildClient", return_value=client),
            mock.patch.object(conn, "sendData", return_value=True),
        ):
            suc = conn.communicateRaw("test")
            assert suc[0]
            assert not suc[1]
            assert suc[2] == "Exception"

    def test_communicateRaw_3(self):
        client = makeClient(data=b"test")
        conn = Connection(makeParent())
        with (
            mock.patch.object(conn, "buildClient", return_value=client),
            mock.patch.object(conn, "sendData", return_value=True),
        ):
            suc = conn.communicateRaw("test")
            assert suc[0]
            assert suc[1]
            assert suc[2] == "test"
        client.abort.assert_called_once()
        client.close.assert_called_once()

    def test_communicateRaw_timeout_loggingTrace(self):
        client = makeClient(readyRead=False)
        conn = Connection(makeParent(loggingTrace=True))
        with (
            mock.patch.object(conn, "buildClient", return_value=client),
            mock.patch.object(conn, "sendData", return_value=True),
        ):
            suc = conn.communicateRaw("test")
        assert not suc[1]
        assert suc[2] == "Timeout"

    def test_communicateRaw_success_loggingTrace(self):
        client = makeClient(data=b"response")
        conn = Connection(makeParent(loggingTrace=True))
        with (
            mock.patch.object(conn, "buildClient", return_value=client),
            mock.patch.object(conn, "sendData", return_value=True),
        ):
            suc = conn.communicateRaw("test")
        assert suc[1]
        assert suc[2] == "response"


class TestSendData:
    """Tests for the sendData method and logging."""

    def test_sendData_loggingTrace(self):
        conn = Connection(makeParent(host=("localhost", 3492), loggingTrace=True))
        client = makeClient()
        suc = conn.sendData(client, ":AP#")
        assert suc

    def test_sendData_timeout_loggingTrace(self):
        conn = Connection(makeParent(host=("localhost", 3492), loggingTrace=True))
        client = makeClient(written=False)
        suc = conn.sendData(client, ":AP#")
        assert not suc

    def test_sendData_exception(self):
        conn = Connection(makeParent(host=("localhost", 3492)))
        client = makeClient()
        client.write.side_effect = Exception("Test")
        suc = conn.sendData(client, ":AP#")
        assert not suc


class TestCommandP:
    """Tests for COMMAND_P frozenset."""

    def test_command_P_is_frozenset(self):
        conn = Connection(makeParent())
        assert isinstance(conn.COMMAND_P, frozenset)
        assert frozenset({":RC", ":Rc", ":RG", ":Suaf"}) == conn.COMMAND_P
