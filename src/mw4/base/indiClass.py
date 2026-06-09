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
import asyncio
import logging
import queue
from dataclasses import dataclass, field
from indipyclient.queclient import EventItem, QueClient, runqueclient
from mw4.base.indiClassAddOns import INDI_TYPES, INDIGO_CONV
from mw4.base.tpool import Worker
from PySide6.QtCore import QMutex, QThreadPool
from queue import Queue
from typing import Any


@dataclass
class DeviceConfigIndi:
    deviceName: str = field(default="")
    hostAddress: str = field(default="127.0.0.1")
    port: int = field(default=7624)
    protocol: str = field(default="http")
    loadConfig: bool = field(default=False)
    showMessage: bool = field(default=False)


class IndiClass:
    log = logging.getLogger("MW4")
    MAX_SEARCH: int = 20

    def __init__(self, parent: Any) -> None:
        self.parent: Any = parent
        self.app: Any = parent.app
        self.msg: Any = parent.app.msg
        self.data: dict = parent.data
        self.signals: Any = parent.signals
        self.config = DeviceConfigIndi()
        self.threadPool: QThreadPool = parent.app.threadPool
        self.clientMutex: QMutex = QMutex()
        self.discoverMutex: QMutex = QMutex()
        self.deviceConnected: bool = False
        self.discoverList: list[str] = []
        self.isINDIGO: bool = False
        self.commandRunning: bool = False
        self.loggingTrace: bool = False
        self.rxQ: Queue = Queue()
        self.txQ: Queue = Queue()
        self.queueClient: QueClient | None = None
        self.workerIndiQueueClient: Worker | None = None
        self.workerProcessRxQueue: Worker | None = None

    def updateMessage(self, item: EventItem) -> None:
        if not self.config.showMessage:
            return
        message = item.snapshot[self.config.deviceName].dictdump().get("messages")
        if not message:
            return
        self.msg.emit(
            0, "INDI", "Device message", f"{self.config.deviceName:15s} {message[0][1]}"
        )

    def setStatusDeviceConnected(self, item: EventItem) -> None:
        status = item.snapshot[self.config.deviceName]["CONNECTION"].get("CONNECT") == "On"
        if status and not self.deviceConnected:
            self.signals.deviceConnected.emit(self.config.deviceName)
        if not status and self.deviceConnected:
            self.signals.deviceDisconnected.emit(self.config.deviceName)
        self.deviceConnected = status

    def writeVectorsToData(self, item: EventItem, vectors: dict) -> None:
        for vector, vectorItem in vectors.items():
            vectorName = vectorItem["name"]
            for member, memberItem in vectorItem["members"].items():
                value = memberItem.get("floatvalue", memberItem["value"])
                value = True if value == "On" else value
                value = False if value == "Off" else value
                entry = f"{vectorName}.{member}"
                entry = INDIGO_CONV.get(entry, entry) if self.isINDIGO else entry
                self.data[entry] = value

    def processRxQueue(self) -> None:
        while self.commandRunning:
            try:
                item = self.rxQ.get(timeout=0.01)
            except queue.Empty:
                continue
            if item.snapshot.get(self.config.deviceName) is None:
                continue
            if item.devicename != self.config.deviceName:
                continue
            if item.snapshot[self.config.deviceName].get("CONNECTION"):
                self.setStatusDeviceConnected(item)
            if item.eventtype == "Message":
                self.updateMessage(item)
            vectors = item.snapshot[self.config.deviceName].dictdump().get("vectors")
            if vectors:
                self.writeVectorsToData(item, vectors)

    def cleanupStop(self) -> None:
        self.queueClient = None
        self.clientMutex.unlock()

    def runQueueClient(self) -> None:
        self.queueClient = QueClient(
            self.txQ,
            self.rxQ,
            indihost=self.config.hostAddress,
            indiport=self.config.port,
            blobfolder=str(self.app.mwGlob["tempDir"]),
        )
        self.queueClient.debug_verbosity(3 if self.loggingTrace else 0)
        asyncio.run(self.queueClient.asyncrun())

    def startCommunication(self) -> None:
        if not self.clientMutex.tryLock():
            return
        self.txQ.queue.clear()
        self.rxQ.queue.clear()
        self.data.clear()
        self.commandRunning = True
        self.workerIndiQueueClient = Worker(self.runQueueClient)
        self.workerIndiQueueClient.signals.finished.connect(self.cleanupStop)
        self.threadPool.start(self.workerIndiQueueClient)
        self.workerProcessRxQueue = Worker(self.processRxQueue)
        self.threadPool.start(self.workerProcessRxQueue)

    def stopCommunication(self) -> None:
        self.txQ.put(None)
        self.commandRunning = False
        self.config.deviceName = ""
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit(self.config.deviceName)

    def loadIndiConfig(self, deviceName: str) -> None:
        self.txQ.put((deviceName, "CONFIG_PROCESS", {"CONFIG_PROCESS": True}))

    def discoverDevices(self, deviceType: str, hostaddress: str, port: int) -> list[str]:
        if not self.discoverMutex.tryLock():
            return []
        n = self.MAX_SEARCH
        txQ = Queue()
        rxQ = Queue()
        discoverSet = set()
        worker = Worker(runqueclient, txQ, rxQ, indihost=hostaddress, indiport=port)
        self.threadPool.start(worker)
        while n > 0:
            try:
                item = rxQ.get(timeout=0.1)
            except queue.Empty:
                n -= 1
                continue
            if item is None:
                continue
            if item.devicename:
                driver = item.snapshot[item.devicename].get("DRIVER_INFO")
                if driver and (INDI_TYPES[deviceType] & int(driver["DRIVER_INTERFACE"])):
                    discoverSet.add(item.devicename)
            rxQ.task_done()
        txQ.put(None)
        self.discoverMutex.unlock()
        return list(discoverSet)
