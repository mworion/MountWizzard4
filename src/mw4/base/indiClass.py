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
import time
from indipyclient.queclient import EventItem, QueClient, runqueclient
from mw4.base.indiClassAddOns import INDI_TYPES, INDIGO_CONV
from mw4.base.threadUtils import mainThreadSleep
from mw4.base.tpool import Worker
from PySide6.QtCore import QMutex, QThreadPool
from queue import Queue
from typing import Any


class IndiClass:
    log = logging.getLogger("MW4")
    MAX_SEARCH: int = 20

    def __init__(self, parent: Any) -> None:
        self.parent: Any = parent
        self.app: Any = parent.app
        self.msg: Any = parent.app.msg
        self.data: dict = parent.data
        self.signals: Any = parent.signals
        self.loadConfig: bool = parent.loadConfig
        self.threadPool: QThreadPool = parent.app.threadPool
        self.clientMutex: QMutex = QMutex()
        self.discoverMutex: QMutex = QMutex()

        self.deviceName: str = ""
        self.deviceConnected: bool = False
        self._hostaddress: str | None = None
        self._host: tuple[str, int] | None = None
        self._port: int | None = None
        self.discoverList: list[str] = []
        self.isINDIGO: bool = False
        self.messages: bool = False
        self.commandRunning: bool = False
        self.loggingTrace: bool = False
        self.rxQ: Queue = Queue()
        self.txQ: Queue = Queue()
        self.queueClient: QueClient | None = None
        self.workerIndiQueueClient: Worker | None = None
        self.workerProcessRxQueue: Worker | None = None

        self.defaultConfig: dict[str, Any] = {
            "deviceName": "",
            "deviceList": [],
            "hostaddress": "localhost",
            "port": 7624,
            "loadConfig": False,
            "messages": False,
        }

    @property
    def host(self) -> tuple[str, int] | None:
        return self._host

    @host.setter
    def host(self, value: tuple[str, int] | None) -> None:
        self._host = value

    @property
    def hostaddress(self) -> str | None:
        return self._hostaddress

    @hostaddress.setter
    def hostaddress(self, value: str | None) -> None:
        self._hostaddress = value

    @property
    def port(self) -> int | None:
        return self._port

    @port.setter
    def port(self, value: int | str) -> None:
        self._port = int(value)

    def updateMessage(self, item: EventItem) -> None:
        if not self.messages:
            return
        message = item.snapshot[self.deviceName].dictdump().get("messages")
        if not message:
            return
        self.msg.emit(0, "INDI", "Device message", f"{self.deviceName:15s} {message[0][1]}")

    def setStatusDeviceConnected(self, item: EventItem) -> None:
        status = item.snapshot[self.deviceName]["CONNECTION"].get("CONNECT") == "On"
        if status and not self.deviceConnected:
            self.signals.deviceConnected.emit(self.deviceName)
        if not status and self.deviceConnected:
            self.signals.deviceDisconnected.emit(self.deviceName)
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
            if self.rxQ.empty():
                time.sleep(0.1)
                continue
            item = self.rxQ.get()
            if item.snapshot.get(self.deviceName) is None:
                continue
            if item.devicename != self.deviceName:
                continue
            if item.snapshot[self.deviceName].get("CONNECTION"):
                self.setStatusDeviceConnected(item)
            if item.eventtype == "Message":
                self.updateMessage(item)
            vectors = item.snapshot[self.deviceName].dictdump().get("vectors")
            if vectors:
                self.writeVectorsToData(item, vectors)

    def cleanupStop(self) -> None:
        self.clientMutex.unlock()

    def setTrace(self, enable: bool = False) -> None:
        self.loggingTrace = enable
        indiTrace = 2 if enable else 0
        if self.queueClient:
            self.queueClient.debug_verbosity(indiTrace)

    def runQueueClient(self) -> None:
        self.queueClient = QueClient(
            self.txQ,
            self.rxQ,
            indihost=self.hostaddress,
            indiport=self.port,
            blobfolder=str(self.app.mwGlob["tempDir"]),
        )
        self.setTrace(self.loggingTrace)
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
        self.deviceName = ""
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit(self.deviceName)

    def loadIndiConfig(self, deviceName: str) -> None:
        self.txQ.put((deviceName, "CONFIG_PROCESS", {"CONFIG_PROCESS": True}))

    def discoverDevices(self, deviceType: str) -> list[str]:
        if not self.discoverMutex.tryLock():
            return []
        n = self.MAX_SEARCH
        txQ = Queue()
        rxQ = Queue()
        discoverSet = set()
        worker = Worker(runqueclient, txQ, rxQ, indihost=self.hostaddress, indiport=self.port)
        self.threadPool.start(worker)
        while n > 0:
            if rxQ.empty():
                mainThreadSleep(100)
                n = n - 1
                continue
            item = rxQ.get()
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
