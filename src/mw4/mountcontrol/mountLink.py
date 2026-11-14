# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
import queue
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from mw4.mountcontrol import timing
from PySide6.QtCore import QObject, Signal, SignalInstance
from PySide6.QtNetwork import QAbstractSocket, QTcpSocket


class ReplyParser:
    """
    ReplyParser splits the byte stream of a persistent connection into the
    replies of single transactions. Bytes which belong to the next transaction
    stay in the buffer. A reply spec is (chunks, minBytes): chunks > 0 waits for
    that many '#' terminators, otherwise minBytes fixed-length bytes are taken.
    """

    def __init__(self) -> None:
        self.buffer = bytearray()

    def reset(self) -> None:
        self.buffer.clear()

    def feed(self, data: bytes) -> None:
        self.buffer.extend(data)

    def take(self, chunks: int, minBytes: int) -> list[str] | None:
        if chunks > 0:
            if self.buffer.count(b"#") < chunks:
                return None
            end = -1
            for _ in range(chunks):
                end = self.buffer.index(b"#", end + 1)
            raw = bytes(self.buffer[: end + 1])
            del self.buffer[: end + 1]
        else:
            if len(self.buffer) < minBytes:
                return None
            raw = bytes(self.buffer[:minBytes])
            del self.buffer[:minBytes]
        text = raw.replace(b"\xdf", b"*").decode("ASCII", errors="replace")
        return text.rstrip("#").split("#")


class MountLink(QObject):
    """
    MountLink keeps one persistent TCP connection to the mount. ':U2#' is sent
    once per (re)connect. A transaction has a whole deadline. Any timeout or
    error closes the link, marks it for reconnect after a backoff and reports
    failure. Nothing is ever retried or resent.
    """

    log = logging.getLogger("MW4")

    def __init__(self, host: str, port: int, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.host = host
        self.port = port
        self.client: QTcpSocket | None = None
        self.parser = ReplyParser()
        from mw4.mountcontrol.connection import Connection

        self.helper = Connection.__new__(Connection)
        self.helper.id = "link"
        self.helper.host = (host, port)
        self.helper.loggingTrace = False
        self.notBefore = 0.0
        self.reconnects = 0

    def isConnected(self) -> bool:
        return (
            self.client is not None
            and self.client.state() == QAbstractSocket.SocketState.ConnectedState
        )

    def close(self) -> None:
        client, self.client = self.client, None
        self.parser.reset()
        if client is None:
            return
        try:
            client.abort()
            client.close()
        except (OSError, RuntimeError) as e:
            self.log.warning("Link close error: [%s]", e)

    def fail(self, reason: str) -> tuple[bool, list[str]]:
        self.log.debug("Link failure: %s", reason)
        self.close()
        self.notBefore = time.monotonic() + timing.RECONNECT_BACKOFF_S
        return False, []

    def openLink(self) -> bool:
        if self.isConnected():
            return True
        if time.monotonic() < self.notBefore:
            self.log.debug("Link connect skipped: backoff active")
            return False
        self.close()
        client = QTcpSocket()
        client.setSocketOption(QAbstractSocket.SocketOption.LowDelayOption, 1)
        client.connectToHost(self.host, self.port)
        if not client.waitForConnected(int(timing.CONNECT_TIMEOUT_S * 1000)):
            client.abort()
            self.fail("connect timeout")
            return False
        self.client = client
        self.reconnects += 1
        client.write(b":U2#")
        if not client.waitForBytesWritten(int(timing.CONNECT_TIMEOUT_S * 1000)):
            self.fail("timeout sending :U2#")
            return False
        self.log.debug("Link connected, reconnects: %d", self.reconnects)
        return True

    def transact(
        self, commandString: str, deadline: float = timing.BATCH_DEADLINE_S
    ) -> tuple[bool, list[str]]:
        if not self.helper.validCommandSet(commandString):
            return False, []
        chunks, getData, minBytes = self.helper.analyseCommand(commandString)
        if not self.openLink() or self.client is None:
            return False, []
        start = time.monotonic()
        self.client.write(commandString.encode())
        if not self.client.waitForBytesWritten(int(deadline * 1000)):
            return self.fail("send timeout")
        if not getData:
            return True, []
        while True:
            reply = self.parser.take(chunks, minBytes)
            if reply is not None:
                break
            remaining = deadline - (time.monotonic() - start)
            if remaining <= 0 or not self.client.waitForReadyRead(int(remaining * 1000)):
                return self.fail("receive timeout")
            self.parser.feed(self.client.readAll().data())
        duration = time.monotonic() - start
        if self.helper.loggingTrace:
            self.log.debug(
                "[Trace] Transaction %d commands, %.3f s", commandString.count("#"), duration
            )
        return True, reply

    def transactRaw(
        self, commandString: str, deadline: float = timing.COMMAND_DEADLINE_S
    ) -> tuple[bool, bool, str]:
        if not self.openLink() or self.client is None:
            return False, False, "Socket error"
        self.parser.reset()
        self.client.write(commandString.encode())
        if not self.client.waitForBytesWritten(int(deadline * 1000)):
            self.fail("send timeout raw")
            return False, False, "Send error"
        if not self.client.waitForReadyRead(int(deadline * 1000)):
            self.fail("receive timeout raw")
            return True, False, "Timeout"
        raw = bytes(self.client.readAll().data()).replace(b"\xdf", b"*")
        return True, True, raw.decode("ASCII", errors="replace")

    def transactBulk(
        self,
        commandString: str,
        chunkSize: int,
        deadline: float,
        progress: SignalInstance | None = None,
        between: Callable[[], None] | None = None,
    ) -> tuple[bool, list[str]]:
        """
        A bulk transaction sends the commands in chunks. It stops at the first
        failing chunk and never resends. progress(done, total) is emitted after
        each successful chunk. between is called between two chunks and may
        use the link for short jobs.
        """
        commands = commandString.split("#")[:-1]
        total = len(commands)
        if total == 0 or not self.helper.validCommandSet(commandString):
            return False, []
        chunks, _, minBytes = self.helper.analyseCommand(commandString)
        merge = chunks == 0 and minBytes > 0
        response: list[str] = []
        for start in range(0, total, chunkSize):
            chunk = commands[start : start + chunkSize]
            suc, reply = self.transact("#".join(chunk) + "#", deadline)
            if not suc:
                return False, []
            if merge and reply and response:
                response[0] += reply[0]
            else:
                response.extend(reply)
            done = start + len(chunk)
            self.log.debug("Bulk chunk %d/%d", done, total)
            if progress is not None:
                progress.emit(done, total)
            if between is not None and done < total:
                between()
        return True, response


INTERACTIVE = 0
BULK = 1
CYCLIC = 2


@dataclass(order=True)
class LinkJob:
    priority: int
    seq: int
    kind: str = field(compare=False)
    command: str = field(compare=False)
    deadline: float = field(compare=False)
    event: threading.Event = field(compare=False, default_factory=threading.Event)
    result: tuple = field(compare=False, default=(False, [], 0))
    progress: SignalInstance | None = field(compare=False, default=None)


LATENCY_SAMPLES = 500


class LinkWorker(QObject):
    """
    LinkWorker owns the MountLink in a dedicated thread and serves a priority
    queue: interactive before bulk before cyclic. Callers block until their job
    is done or its deadline has passed.
    """

    progress = Signal(int, int)
    log = logging.getLogger("MW4")

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.jobs: queue.PriorityQueue[LinkJob] = queue.PriorityQueue()
        self.counter = 0
        self.lock = threading.Lock()
        self.pending: set[str] = set()
        self.cache: dict[str, tuple[float, list[str]]] = {}
        self.stale = True
        self.coalesced = 0
        self.failures = 0
        self.latency: dict[int, deque[float]] = {
            INTERACTIVE: deque(maxlen=LATENCY_SAMPLES),
            BULK: deque(maxlen=LATENCY_SAMPLES),
            CYCLIC: deque(maxlen=LATENCY_SAMPLES),
        }
        self.link: MountLink | None = None
        self.running = True
        self.workerThread = threading.Thread(target=self.runnerLink, daemon=True)
        self.workerThread.start()

    def stop(self) -> None:
        self.running = False
        self.workerThread.join(1)

    def runnerLink(self) -> None:
        self.link = MountLink(self.host, self.port)
        link = self.link
        while self.running:
            try:
                job = self.jobs.get(timeout=0.1)
            except queue.Empty:
                continue
            self.runJob(job, link)
        link.close()

    def runJob(self, job: LinkJob, link: MountLink) -> None:
        started = time.monotonic()
        if job.kind == "raw":
            job.result = link.transactRaw(job.command, job.deadline)
        elif job.kind == "bulk":
            suc, response = link.transactBulk(
                job.command,
                timing.BULK_CHUNK_SIZE,
                job.deadline,
                job.progress or self.progress,
                (lambda: self.serveFast(link)) if timing.BULK_INTERLEAVE_FAST else None,
            )
            job.result = (suc, response, 0)
        else:
            suc, response = link.transact(job.command, job.deadline)
            job.result = (suc, response, 0)
        self.latency[job.priority].append(time.monotonic() - started)
        self.finishJob(job)
        job.event.set()

    def serveFast(self, link: MountLink) -> None:
        """
        Runs queued fast poll jobs between two bulk chunks. All other jobs
        stay in the queue.
        """
        keep: list[LinkJob] = []
        while True:
            try:
                job = self.jobs.get_nowait()
            except queue.Empty:
                break
            if job.kind == "std" and job.command in timing.FAST_POLL_COMMANDS:
                self.runJob(job, link)
            else:
                keep.append(job)
        for job in keep:
            self.jobs.put(job)

    def finishJob(self, job: LinkJob) -> None:
        with self.lock:
            self.pending.discard(job.command)
        if job.result[0] is not True:
            self.failures += 1
            self.stale = True
        elif job.priority == CYCLIC:
            self.cache[job.command] = (time.monotonic(), job.result[1])
            self.stale = False

    def stats(self, priority: int) -> dict[str, float]:
        """
        Returns count and p50/p95/p99 of the transaction durations in seconds
        for one priority class, taken from the latest samples.
        """
        samples = sorted(self.latency[priority])
        if not samples:
            return {"count": 0, "p50": 0.0, "p95": 0.0, "p99": 0.0}
        last = len(samples) - 1
        result = {"count": len(samples)}
        for name, quantile in (("p50", 0.50), ("p95", 0.95), ("p99", 0.99)):
            result[name] = samples[round(quantile * last)]
        return result

    def logStats(self) -> None:
        for name, priority in (("cyclic", CYCLIC), ("bulk", BULK), ("interactive", INTERACTIVE)):
            self.log.debug(
                "Link stats %s: %s, queue %d, coalesced %d, failures %d",
                name,
                self.stats(priority),
                self.jobs.qsize(),
                self.coalesced,
                self.failures,
            )

    def cached(self, command: str, maxAge: float) -> list[str] | None:
        """
        Returns the latest reply of a cyclic command if it is fresh enough and
        no failure happened since, otherwise None.
        """
        entry = self.cache.get(command)
        if entry is None or self.stale:
            return None
        if time.monotonic() - entry[0] > maxAge:
            return None
        return entry[1]

    def submit(
        self,
        kind: str,
        command: str,
        deadline: float,
        priority: int,
        progress: SignalInstance | None = None,
    ) -> tuple:
        with self.lock:
            if priority == CYCLIC and command in self.pending:
                self.coalesced += 1
                self.log.debug("Cyclic poll coalesced: %s", command[:40])
                return (False, [], 0) if kind != "raw" else (False, False, "Timeout")
            self.pending.add(command)
            self.counter += 1
            job = LinkJob(priority, self.counter, kind, command, deadline, progress=progress)
        self.jobs.put(job)
        if not job.event.wait(self.waitLimit(kind, command, deadline)):
            self.log.debug("Link job wait expired: %s", command[:40])
            return (False, [], 0) if kind != "raw" else (False, False, "Timeout")
        return job.result

    @staticmethod
    def waitLimit(kind: str, command: str, deadline: float) -> float:
        chunks = 1
        if kind == "bulk":
            chunks = command.count("#") // timing.BULK_CHUNK_SIZE + 1
        return deadline * chunks * 2 + timing.CONNECT_TIMEOUT_S


workers: dict[tuple[str, int], LinkWorker] = {}
workersLock = threading.Lock()


def getWorker(host: str, port: int) -> LinkWorker:
    with workersLock:
        worker = workers.get((host, port))
        if worker is None:
            worker = LinkWorker(host, port)
            workers[(host, port)] = worker
        return worker
