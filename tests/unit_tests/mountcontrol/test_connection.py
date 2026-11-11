# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.mountcontrol.connection import Connection
from mw4.mountcontrol.mountLink import workers
from tests.unit_tests.mountcontrol.test_mountLink import FakeMount


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
        suc, _msg, _num = conn.communicate(":test#")
        assert not suc

    def test_communicate_invalid_command_2(self):
        conn = Connection(makeParent())
        suc, _msg, _num = conn.communicate(":AP#:test#")
        assert not suc


class TestCommandP:
    """Tests for COMMAND_P frozenset."""

    def test_command_P_is_frozenset(self):
        conn = Connection(makeParent())
        assert isinstance(conn.COMMAND_P, frozenset)
        assert frozenset({":RC", ":Rc", ":RG", ":Suaf"}) == conn.COMMAND_P


@pytest.fixture
def mount():
    m = FakeMount(
        {
            b":GVN#": b"2.20#",
            b":GVN#:GVN#": b"2.20#2.20#",
            b":Q#": b"",
            b":GVD#": b"Mar 1 2020#",
            b":AP#": b"",
        }
    )
    yield m
    for w in list(workers.values()):
        w.stop()
    workers.clear()
    m.stop()


class TestFacade:
    def test_communicate_ok(self, mount):
        conn = Connection(makeParent(("127.0.0.1", mount.port)))
        suc, response, chunks = conn.communicate(":GVN#")
        assert suc
        assert response == ["2.20"]
        assert chunks == 1

    def test_communicate_responseCheck(self, mount):
        conn = Connection(makeParent(("127.0.0.1", mount.port)))
        assert conn.communicate(":GVN#", "2.20")[0]
        assert not conn.communicate(":GVN#", "x")[0]

    def test_communicate_noReply(self, mount):
        conn = Connection(makeParent(("127.0.0.1", mount.port)))
        assert conn.communicate(":Q#") == (True, [], 0)

    def test_communicate_invalid(self, mount):
        conn = Connection(makeParent(("127.0.0.1", mount.port)))
        assert conn.communicate(":XXX#") == (False, [], 0)
        assert conn.communicateBulk(":XXX#") == (False, [], 0)

    def test_communicate_mountDown(self, mount):
        parent = makeParent(("127.0.0.1", mount.port))
        parent.mountIsUp = False
        conn = Connection(parent)
        assert not conn.communicate(":GVN#")[0]
        assert conn.communicateRaw(":GVN#") == (False, False, "Socket error")
        assert not conn.communicateBulk(":GVN#")[0]

    @pytest.mark.parametrize("host", [None, "abc", ("a",), (None, 1), ("a", None)])
    def test_communicate_badHost(self, host):
        conn = Connection(makeParent(host))
        assert not conn.communicate(":GVN#")[0]

    @pytest.mark.parametrize("host", [None, "abc", ("a",), (None, 1), ("a", None)])
    def test_linkReady_malformedHost(self, host):
        conn = Connection(makeParent(("127.0.0.1", 1)))
        conn.host = host
        assert not conn.linkReady()

    def test_communicate_failure(self):
        conn = Connection(makeParent(("127.0.0.1", 1)))
        assert not conn.communicate(":GVN#", deadline=0.2)[0]

    def test_communicateRaw(self, mount):
        conn = Connection(makeParent(("127.0.0.1", mount.port)))
        assert conn.communicateRaw(":GVN#") == (True, True, "2.20#")

    def test_communicateBulk(self, mount):
        conn = Connection(makeParent(("127.0.0.1", mount.port)))
        suc, response, _ = conn.communicateBulk(":GVN#:GVN#")
        assert suc
        assert response == ["2.20", "2.20"]

    def test_communicateBulk_fail(self):
        conn = Connection(makeParent(("127.0.0.1", 1)))
        assert not conn.communicateBulk(":GVN#")[0]
