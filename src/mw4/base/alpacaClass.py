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
import alpaca.management as alpacaMgmt
import queue
import threading
import time
from alpaca.camera import Camera as AlpycaCamera
from alpaca.covercalibrator import CoverCalibrator as AlpycaCoverCalibrator
from alpaca.dome import Dome as AlpycaDome
from alpaca.exceptions import NotImplementedException as AlpycaNotImplError
from alpaca.filterwheel import FilterWheel as AlpycaFilterWheel
from alpaca.focuser import Focuser as AlpycaFocuser
from alpaca.observingconditions import ObservingConditions as AlpycaObsConditions
from alpaca.switch import Switch as AlpycaSwitch
from alpaca.telescope import Telescope as AlpycaTelescope
from dataclasses import dataclass, field
from mw4.base.driverDataClass import DriverData
from mw4.base.tpool import Worker
from PySide6.QtCore import QThreadPool
from typing import Any


@dataclass
class CommandItem:
    cmdType: str
    name: str
    kwargs: dict = field(default_factory=dict)
    value: Any = None


class AlpacaClass(DriverData):
    DEVICE_TYPE_MAP: dict[str, type] = {
        "camera": AlpycaCamera,
        "dome": AlpycaDome,
        "focuser": AlpycaFocuser,
        "filterwheel": AlpycaFilterWheel,
        "covercalibrator": AlpycaCoverCalibrator,
        "telescope": AlpycaTelescope,
        "observingconditions": AlpycaObsConditions,
        "switch": AlpycaSwitch,
    }

    def __init__(self, parent: Any) -> None:
        super().__init__(parent.data)
        self.app: Any = parent.app
        self.msg: Any = parent.app.msg
        self.data: dict = parent.data
        self.signals: Any = parent.signals
        self.threadPool: QThreadPool = parent.app.threadPool
        self.updateRate: int = 1000
        self.loadConfig: bool = False
        self._host: tuple[str, int] = ("localhost", 11111)
        self._port: int = 11111
        self._hostaddress: str = "localhost"
        self.protocol: str = "http"
        self.apiVersion: int = 1
        self._deviceName: str = ""
        self.deviceType: str = ""
        self.number: int = 0
        self.device: Any = None

        self.defaultConfig: dict[str, Any] = {
            "deviceName": "",
            "deviceList": [],
            "hostaddress": "localhost",
            "port": 11111,
            "apiVersion": 1,
            "user": "",
            "password": "",
            "updateRate": 1000,
        }

        self.deviceConnected: bool = False
        self.serverConnected: bool = False
        self.commandQueue: queue.Queue = queue.Queue()
        self.stopEvent: threading.Event = threading.Event()
        self.workerCommunicationLoop: Worker | None = None

    @property
    def host(self) -> tuple[str, int]:
        return self._host

    @host.setter
    def host(self, value: tuple[str, int]) -> None:
        self._host = value

    @property
    def hostaddress(self) -> str:
        return self._hostaddress

    @hostaddress.setter
    def hostaddress(self, value: str) -> None:
        self._hostaddress = value
        self._host = (self._hostaddress, self._port)

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(self, value: int | str) -> None:
        self._port = int(value)
        self._host = (self._hostaddress, self._port)

    @property
    def deviceName(self) -> str:
        return self._deviceName

    @deviceName.setter
    def deviceName(self, value: str) -> None:
        self._deviceName = value
        valueSplit = value.split(":")
        if len(valueSplit) != 3:
            return
        self.deviceType = valueSplit[1].strip()
        self.number = int(valueSplit[2].strip())

    def createAlpacaDevice(self) -> bool:
        deviceClass = self.DEVICE_TYPE_MAP.get(self.deviceType)
        if deviceClass is None:
            self.log.warning(f"Unknown device type: [{self.deviceType}]")
            return False

        address = f"{self._hostaddress}:{self._port}"
        try:
            self.device = deviceClass(address, self.number, self.protocol)
        except Exception as e:
            self.log.error(f"Create device exception: [{e}]")
            return False

        self.log.debug(f"Created [{self.deviceType}] device at [{address}]")
        return True

    def getDeviceProp(self, attr: str) -> Any:
        try:
            return getattr(self.device, attr)
        except AlpycaNotImplError:
            self.log.warning(
                f"[{self.deviceName}] [{attr}] not implemented"
            )
            return None
        except Exception as e:
            self.log.error(
                f"[{self.deviceName}] get [{attr}] exception: [{e}]"
            )
            return None

    def setDeviceProp(self, attr: str, value: Any) -> bool:
        try:
            setattr(self.device, attr, value)
            return True
        except AlpycaNotImplError:
            self.log.warning(
                f"[{self.deviceName}] [{attr}] not implemented"
            )
            return False
        except Exception as e:
            self.log.error(
                f"[{self.deviceName}] set [{attr}] exception: [{e}]"
            )
            return False

    def callDeviceMethod(self, method: str, **kwargs: Any) -> None:
        self.commandQueue.put(
            CommandItem(cmdType="call", name=method, kwargs=kwargs)
        )

    def callDeviceMethodSync(self, method: str, **kwargs: Any) -> Any:
        try:
            return getattr(self.device, method)(**kwargs)
        except AlpycaNotImplError:
            self.log.warning(
                f"[{self.deviceName}] [{method}] not implemented"
            )
            return None
        except Exception as e:
            self.log.error(
                f"[{self.deviceName}] call [{method}] exception: [{e}]"
            )
            return None

    def getAndStoreDeviceProp(self, attr: str, element: str) -> None:
        value = self.getDeviceProp(attr)
        self.storePropertyToData(value, element)

    def discoverAPIVersion(self) -> int:
        address = f"{self._hostaddress}:{self._port}"
        try:
            versions = alpacaMgmt.apiversions(address)
            if not versions:
                return 0
            return max(versions)
        except Exception as e:
            self.log.error(f"Discover API exception: [{e}]")
            return 0

    def discoverAlpacaDevices(self) -> list:
        address = f"{self._hostaddress}:{self._port}"
        try:
            return alpacaMgmt.configureddevices(address)
        except Exception as e:
            self.log.error(f"Search devices exception: [{e}]")
            return []

    def discoverDevices(self, deviceType: str) -> list:
        devices = self.discoverAlpacaDevices()
        if not devices:
            return []

        temp = [x for x in devices if x["DeviceType"].lower() == deviceType]
        discoverList = [
            f"{x['DeviceName']}:{deviceType}:{x['DeviceNumber']}"
            for x in temp
        ]
        return discoverList

    def connectDevice(self) -> bool:
        suc = False
        for retry in range(0, 10):
            self.setDeviceProp("Connected", True)
            suc = self.getDeviceProp("Connected")
            if suc:
                self.log.debug(
                    f"[{self.deviceName}] connected, [{retry}] retries"
                )
                break
            self.log.info(
                f"[{self.deviceName}] Connection retry: [{retry}]"
            )
            time.sleep(0.2)

        if not suc:
            self.msg.emit(2, "ALPACA", "Connect error", self.deviceName)
        return bool(suc)

    def getInitialConfig(self) -> None:
        self.data["DRIVER_INFO.DRIVER_NAME"] = self.getDeviceProp("Name")
        self.data["DRIVER_INFO.DRIVER_VERSION"] = (
            self.getDeviceProp("DriverVersion")
        )
        self.data["DRIVER_INFO.DRIVER_EXEC"] = self.getDeviceProp(
            "DriverInfo"
        )

    def pollData(self) -> None:
        pass

    def processCommandQueue(self) -> None:
        while not self.commandQueue.empty():
            try:
                cmd = self.commandQueue.get_nowait()
            except queue.Empty:
                break

            if cmd.cmdType == "call":
                try:
                    getattr(self.device, cmd.name)(**cmd.kwargs)
                except AlpycaNotImplError:
                    self.log.warning(
                        f"[{self.deviceName}] [{cmd.name}] not implemented"
                    )
                except Exception as e:
                    self.log.error(
                        f"[{self.deviceName}] call [{cmd.name}]"
                        f" exception: [{e}]"
                    )
            elif cmd.cmdType == "set":
                self.setDeviceProp(cmd.name, cmd.value)
            else:
                self.log.warning(
                    f"[{self.deviceName}] unknown cmdType: [{cmd.cmdType}]"
                )

    def runnerCommunicationLoop(self) -> None:
        while not self.stopEvent.is_set():
            if not self.deviceConnected:
                suc = self.connectDevice()
                if suc:
                    self.serverConnected = True
                    self.deviceConnected = True
                    self.signals.serverConnected.emit()
                    self.signals.deviceConnected.emit(self.deviceName)
                    self.msg.emit(
                        0, "ALPACA", "Device found", self.deviceName
                    )
                    self.getInitialConfig()
                self.stopEvent.wait(timeout=self.updateRate / 1000)
                continue

            suc = self.getDeviceProp("Connected")
            if not suc:
                self.deviceConnected = False
                self.signals.deviceDisconnected.emit(self.deviceName)
                self.msg.emit(
                    0, "ALPACA", "Device remove", self.deviceName
                )
                self.stopEvent.wait(timeout=self.updateRate / 1000)
                continue

            try:
                self.pollData()
            except Exception as e:
                self.log.error(
                    f"[{self.deviceName}] pollData exception: [{e}]"
                )
            self.processCommandQueue()
            self.stopEvent.wait(timeout=self.updateRate / 1000)

    def startCommunication(self) -> None:
        self.data.clear()
        if not self.createAlpacaDevice():
            self.msg.emit(
                2, "ALPACA", "Device type error", self.deviceName
            )
            return
        self.stopEvent.clear()
        self.workerCommunicationLoop = Worker(self.runnerCommunicationLoop)
        self.threadPool.start(self.workerCommunicationLoop)

    def stopCommunication(self) -> None:
        self.stopEvent.set()
        self.setDeviceProp("Connected", False)
        self.deviceConnected = False
        self.serverConnected = False
        self.signals.deviceDisconnected.emit(self.deviceName)
        self.signals.serverDisconnected.emit({self.deviceName: 0})
        self.msg.emit(0, "ALPACA", "Device  remove", self.deviceName)
