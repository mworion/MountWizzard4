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
# Licence APL2.0
#
###########################################################
import logging
from queue import Queue
import time
from indipyclient.queclient import runqueclient
from mw4.base.indiClassAddOns import INDIGO_CONV, INDI_TYPES
from mw4.base.tpool import Worker
from PySide6.QtCore import QThreadPool, QMutex
from typing import Any


class IndiClass:
    log = logging.getLogger("MW4")
    MAX_SEARCH = 40

    def __init__(self, parent: Any) -> None:
        self.parent: Any = parent
        self.app: Any = parent.app
        self.msg: Any = parent.app.msg
        self.data: dict = parent.data
        self.signals: Any = parent.signals
        self.loadConfig: bool = parent.loadConfig
        self.updateRate: int = parent.updateRate
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
        self.receiveQ: Queue = Queue()
        self.sendQ: Queue = Queue()
        self.workerIndiQueueClient: Worker | None = None
        self.workerProcessRxQueue: Worker | None = None

        self.defaultConfig: dict[str, Any] = {
            "deviceName": "",
            "deviceList": [],
            "hostaddress": "localhost",
            "port": 7624,
            "loadConfig": False,
            "messages": False,
            "updateRate": 1000,
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

    def setStatusDeviceConnected(self, status: bool) -> None:
        if status and not self.deviceConnected:
            self.signals.deviceConnected.emit(self.deviceName)
        if not status and self.deviceConnected:
            self.signals.deviceDisconnected.emit(self.deviceName)
        self.deviceConnected = status

    def writeVectorsToData(self, vectors: dict) -> None:
        self.data.update(vectors)
        for vector, vectorItem in vectors.items():
            vectorName = vectorItem["name"]
            for member, memberItem in vectorItem["members"].items():
                value = memberItem.get("floatvalue", memberItem["value"])
                entry = f"{vectorName}.{member}"
                entry = INDIGO_CONV.get(entry, entry) if self.isINDIGO else entry
                self.data[entry] = value
                # print(entry, value)

    def processRxQueue(self) -> None:
        while self.commandRunning:
            if self.receiveQ.empty():
                time.sleep(0.05)
                continue
            item = self.receiveQ.get()
            print(item)
            if item.snapshot.get(self.deviceName) is None:
                continue
            if item.snapshot[self.deviceName].get("CONNECTION"):
                self.setStatusDeviceConnected(item.snapshot[self.deviceName]["CONNECTION"].get("CONNECT") == "On")
            if item.devicename != self.deviceName:
                continue
            vectors = item.snapshot[self.deviceName].dictdump().get("vectors")
            if vectors:
                self.writeVectorsToData(vectors)
    def cleanupStop(self):
        self.clientMutex.unlock()
        print("cleanup stop runqueueclient")
        self.commandRunning = False
        self.deviceName = ""
        self.deviceConnected = False


    def startCommunication(self) -> None:
        if not self.clientMutex.tryLock():
            return
        print("startCommunication")
        self.sendQ.queue.clear()
        self.receiveQ.queue.clear()
        self.data.clear()
        self.commandRunning = True
        self.workerIndiQueueClient = Worker(runqueclient, self.sendQ, self.receiveQ,
                                      indihost=self.hostaddress, indiport=self.port,
                                      blobfolder=str(self.app.mwGlob["tempDir"]))
        self.workerIndiQueueClient.signals.finished.connect(self.cleanupStop)
        self.threadPool.start(self.workerIndiQueueClient)
        self.workerProcessRxQueue = Worker(self.processRxQueue)
        self.threadPool.start(self.workerProcessRxQueue)

    def stopCommunication(self) -> None:
        print("stopCommunication")
        self.sendQ.put(None)

    def loadIndiConfig(self, deviceName: str) -> None:
        self.sendQ.put((deviceName, "CONFIG_PROCESS", {"CONFIG_PROCESS": True}))

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
                time.sleep(0.05)
                continue
            item = rxQ.get()
            if item is None:
                continue
            n = n - 1
            if item.eventtype == "Define" and item.devicename:
                driver = item.snapshot[item.devicename].get("DRIVER_INFO")
                if driver:
                    if INDI_TYPES[deviceType] & int(driver["DRIVER_INTERFACE"]):
                        discoverSet.add(item.devicename)
        txQ.put(None)
        self.discoverMutex.unlock()
        return list(discoverSet)
