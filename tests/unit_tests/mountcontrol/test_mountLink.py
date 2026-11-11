# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
import socket
import threading
import time
from mw4.mountcontrol import timing
from mw4.mountcontrol.mountLink import (
    BULK,
    CYCLIC,
    INTERACTIVE,
    LinkWorker,
    MountLink,
    ReplyParser,
    getWorker,
    workers,
)
from unittest import mock


class FakeMount:
    def __init__(self, replies: dict[bytes, bytes]) -> None:
        self.replies = replies
        self.received = bytearray()
        self.accepted = 0
        self.server = socket.socket()
        self.server.bind(("127.0.0.1", 0))
        self.server.listen(5)
        self.port = self.server.getsockname()[1]
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self) -> None:
        while self.running:
            try:
                conn, _ = self.server.accept()
            except OSError:
                return
            self.accepted += 1
            conn.settimeout(0.05)
            while self.running:
                try:
                    data = conn.recv(4096)
                except TimeoutError:
                    continue
                except OSError:
                    break
                if not data:
                    break
                self.received.extend(data)
                keys = [k for k in self.replies if data.endswith(k)]
                if keys:
                    conn.sendall(self.replies[max(keys, key=len)])
            conn.close()

    def stop(self) -> None:
        self.running = False
        self.server.close()


def test_parserChunks():
    p = ReplyParser()
    p.feed(b"a#b")
    assert p.take(2, 0) is None
    p.feed(b"#c#")
    assert p.take(2, 0) == ["a", "b"]
    assert p.take(1, 0) == ["c"]


def test_parserMinBytes():
    p = ReplyParser()
    p.feed(b"1")
    assert p.take(0, 2) is None
    p.feed(b"0\xdf")
    assert p.take(0, 2) == ["10"]
    assert p.take(0, 1) == ["*"]
    p.feed(b"x")
    p.reset()
    assert p.take(0, 1) is None


def test_transact_flow():
    mount = FakeMount({b":Ginfo#": b"a#", b":Ginfo#:Ginfo#": b"1#2#"})
    link = MountLink("127.0.0.1", mount.port)
    try:
        assert link.transact(":Ginfo#") == (True, ["a"])
        assert link.transact(":Ginfo#") == (True, ["a"])
        assert link.transact(":Ginfo#:Ginfo#") == (True, ["1", "2"])
        assert link.transact(":Q#") == (True, [])
        assert link.transact(":Bad#") == (False, [])
        assert mount.accepted == 1
        assert mount.received.startswith(b":U2#")
        assert mount.received.count(b":U2#") == 1
        assert link.isConnected()
    finally:
        link.close()
        link.close()
        mount.stop()


def test_transact_timeoutNoRetry(caplog):
    mount = FakeMount({})
    link = MountLink("127.0.0.1", mount.port)
    try:
        with caplog.at_level(logging.DEBUG, logger="MW4"):
            assert link.transact(":Ginfo#", deadline=0.2) == (False, [])
        assert "receive timeout" in caplog.text
        assert mount.received.count(b":Ginfo#") == 1
        assert not link.isConnected()
        assert link.transact(":Ginfo#", deadline=0.2) == (False, [])
        assert mount.accepted == 1
        time.sleep(timing.RECONNECT_BACKOFF_S + 0.1)
        mount.replies[b":Ginfo#"] = b"a#"
        assert link.transact(":Ginfo#") == (True, ["a"])
        assert mount.accepted == 2
    finally:
        link.close()
        mount.stop()


def test_connectTimeout():
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    link = MountLink("127.0.0.1", port)
    with mock.patch("mw4.mountcontrol.mountLink.QTcpSocket.waitForConnected", return_value=False):
        assert link.transact(":Ginfo#") == (False, [])
    assert not link.isConnected()


def test_sendTimeout():
    mount = FakeMount({})
    link = MountLink("127.0.0.1", mount.port)
    try:
        assert link.connect()
        with mock.patch.object(link.client, "waitForBytesWritten", return_value=False):
            assert link.transact(":Ginfo#") == (False, [])
        assert link.client is None
    finally:
        mount.stop()


def test_u2SendTimeout():
    mount = FakeMount({})
    link = MountLink("127.0.0.1", mount.port)
    try:
        with mock.patch(
            "mw4.mountcontrol.mountLink.QTcpSocket.waitForBytesWritten", return_value=False
        ):
            assert not link.connect()
    finally:
        mount.stop()


def test_closeError(caplog):
    link = MountLink("127.0.0.1", 1)
    link.client = mock.Mock()
    link.client.abort.side_effect = OSError("x")
    link.close()
    assert "Link close error" in caplog.text


def test_transactRaw():
    mount = FakeMount({b":GVN#": b"2.20\xdf#"})
    link = MountLink("127.0.0.1", mount.port)
    try:
        assert link.transactRaw(":GVN#") == (True, True, "2.20*#")
        assert link.transactRaw(":XX#", deadline=0.2) == (True, False, "Timeout")
        link.close()
        link.notBefore = 0.0
        with mock.patch.object(link, "connect", return_value=False):
            assert link.transactRaw(":GVN#") == (False, False, "Socket error")
        assert link.connect()
        with mock.patch.object(link.client, "waitForBytesWritten", return_value=False):
            assert link.transactRaw(":GVN#") == (False, False, "Send error")
    finally:
        link.close()
        mount.stop()


def test_transactBulk():
    mount = FakeMount({b":GVN#:GVN#": b"1#2#", b":GVN#": b"3#"})
    link = MountLink("127.0.0.1", mount.port)
    progress = mock.Mock()
    try:
        assert link.transactBulk(":GVN#:GVN#:GVN#", 2, 1.0, progress) == (
            True,
            ["1", "2", "3"],
        )
        assert progress.emit.call_args_list == [mock.call(2, 3), mock.call(3, 3)]
        assert link.transactBulk(":GVN#", 2, 1.0) == (True, ["3"])
        assert link.transactBulk("", 2, 1.0) == (False, [])
        assert link.transactBulk(":GVN#:GVN#", 2, 0.2)[0] is True
        assert link.transactBulk(":XX#", 2, 0.2) == (False, [])
        mount.replies.clear()
        assert link.transactBulk(":GVN#:GVN#", 1, 0.2) == (False, [])
    finally:
        link.close()
        mount.stop()


def test_transactBulk_merge():
    mount = FakeMount({b":CM#": b"1", b":FLIP#": b"2"})
    link = MountLink("127.0.0.1", mount.port)
    try:
        suc, response = link.transactBulk(":CM#:FLIP#", 1, 1.0)
        assert suc
        assert response == ["12"]
    finally:
        link.close()
        mount.stop()


def test_worker():
    mount = FakeMount({b":GVN#": b"3#", b":GVN#:GVN#": b"1#2#", b":GVN#\xdf": b""})
    worker = getWorker("127.0.0.1", mount.port)
    try:
        assert getWorker("127.0.0.1", mount.port) is worker
        assert worker.submit("std", ":GVN#", 1.0, CYCLIC) == (True, ["3"], 0)
        assert worker.submit("raw", ":GVN#", 1.0, INTERACTIVE) == (True, True, "3#")
        assert worker.submit("bulk", ":GVN#:GVN#", 1.0, BULK) == (True, ["1", "2"], 0)
        assert LinkWorker.waitLimit("bulk", ":GVN#" * 61, 1.0) > 6
        with mock.patch.object(worker, "waitLimit", return_value=0.0):
            assert worker.submit("std", ":GVN#", 1.0, CYCLIC) == (False, [], 0)
            assert worker.submit("raw", ":GVN#", 1.0, CYCLIC) == (False, False, "Timeout")
    finally:
        worker.stop()
        workers.clear()
        mount.stop()
