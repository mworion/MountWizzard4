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
from mw4.base.tpool import Worker
from PySide6.QtCore import QThreadPool, QMutex
from typing import Any


class IndiClassNew:
    INDI_TYPES: dict[str, int] = {
        "telescope": (1 << 0),
        "camera": (1 << 1),
        "guider": (1 << 2),
        "focuser": (1 << 3),
        "filterwheel": (1 << 4),
        "dome": (1 << 5),
        "observingconditions": (1 << 7) | (1 << 15),
        "skymeter": (1 << 15) | (1 << 19),
        "covercalibrator": (1 << 9) | (1 << 10),
        "switch": (1 << 7) | (1 << 3) | (1 << 15) | (1 << 18),
    }
    log = logging.getLogger("MW4")
    RETRY_DELAY: int = 1500
    NUMBER_RETRY: int = 5

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

        self.deviceName: str = ""
        self.deviceType: int = 0
        self.deviceConnected: bool = False
        self._hostaddress: str | None = None
        self._host: tuple[str, int] | None = None
        self._port: int | None = None
        self.discoverList: list[str] = []
        self.isINDIGO: bool = False
        self.messages: bool = False
        self.commandRunning: bool = False
        self.rxQueue: Queue = Queue()
        self.txQueue: Queue = Queue()
        self.workerIndiQueue: Worker | None = None
        self.workerIndiCommand: Worker | None = None

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
        return "127.0.0.1", 7624
        return self._host

    @host.setter
    def host(self, value: tuple[str, int] | None) -> None:
        self._host = value
        self.client.host = value

    @property
    def hostaddress(self) -> str | None:
        return "127.0.0.1"
        return self._hostaddress

    @hostaddress.setter
    def hostaddress(self, value: str | None) -> None:
        self._hostaddress = value

    @property
    def port(self) -> int | None:
        return 7624
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

    def manageResults(self) -> None:
        while self.commandRunning:
            if self.rxQueue.empty():
                time.sleep(0.1)
                continue
            rxItem = self.rxQueue.get()
            # print("Data: ", rxItem.eventtype, rxItem.devicename, rxItem.vectorname)
            if rxItem.snapshot.get(self.deviceName) is None:
                continue
            if rxItem.snapshot[self.deviceName].get("CONNECTION"):
                self.setStatusDeviceConnected(rxItem.snapshot[self.deviceName]["CONNECTION"].get("CONNECT") == "On")
            if rxItem.devicename != self.deviceName:
                continue
            rxVector = rxItem.snapshot[self.deviceName].dictdump().get("vectors")
            if rxVector:
                for vector, vectorItem in rxVector.items():
                    vectorName = vectorItem["name"]
                    vectorType = vectorItem["vectortype"]
                    for member, memberItem in vectorItem["members"].items():
                        if vectorType == "NumberVector":
                            value = float(memberItem["value"])
                        else:
                            value = memberItem["value"]
                        entry = f"{vectorName}.{member}"
                        self.data[entry] = value
                        print(f"{vectorName}.{member}", value)

    def cleanupStop(self):
        self.clientMutex.unlock()
        self.commandRunning = False
        print("stopped thread")

    def startCommunication(self) -> None:
        print("start")
        if not self.clientMutex.tryLock():
            return
        self.commandRunning = True
        self.deviceName = "CCD Simulator"
        self.deviceType = self.INDI_TYPES["camera"]
        self.data.clear()
        self.workerIndiQueue = Worker(runqueclient, self.txQueue, self.rxQueue, indihost=self.hostaddress, indiport=self.port)
        self.workerIndiQueue.signals.finished.connect(self.cleanupStop)
        self.threadPool.start(self.workerIndiQueue)
        self.workerIndiCommand = Worker(self.manageResults)
        self.threadPool.start(self.workerIndiCommand)


    def stopCommunication(self) -> None:
        print("stopped command")
        self.txQueue.put(None)
        self.deviceName = ""
        self.deviceConnected = False
        self.commandRunning = False

    def connectDevice(self, deviceName: str, propertyName: str) -> None:
        if propertyName != "CONNECTION":
            return

        if deviceName == self.deviceName:
            self.client.connectDevice(deviceName=deviceName)

    def loadIndiConfig(self, deviceName: str) -> None:
        loadObject = self.device.getSwitch("CONFIG_PROCESS")
        loadObject["CONFIG_LOAD"] = True
        suc = self.client.sendNewSwitch(
            deviceName=deviceName, propertyName="CONFIG_PROCESS", elements=loadObject
        )
        t = f"Config load [{deviceName}] success: [{suc}], value: [True]"
        self.log.info(t)

    def discoverDevices(self, deviceType: str) -> list[str]:
        self.discoverList = []
        return self.discoverList
