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
from mw4.base.driverDataClass import DriverData
from mw4.base.tpool import Worker
from PySide6.QtCore import QThreadPool, QTimer
from typing import Any


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
        self.propertyExceptions: list[str] = []
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
        self.worker: Worker | None = None
        self.workerGetConfig: Worker | None = None
        self.workerStatus: Worker | None = None
        self.workerData: Worker | None = None
        self.workerConnect: Worker | None = None

        self.cycleDevice: QTimer = QTimer()
        self.cycleDevice.setSingleShot(False)
        self.cycleDevice.timeout.connect(self.pollStatus)
        self.cycleData: QTimer = QTimer()
        self.cycleData.setSingleShot(False)
        self.cycleData.timeout.connect(self.pollData)

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
        if self.device is None or attr in self.propertyExceptions:
            return None

        try:
            return getattr(self.device, attr)
        except AlpycaNotImplError:
            self.log.warning(f"[{self.deviceName}] [{attr}] not implemented")
            self.propertyExceptions.append(attr)
            return None
        except Exception as e:
            self.log.error(f"[{self.deviceName}] get [{attr}] exception: [{e}]")
            return None

    def setDeviceProp(self, attr: str, value: Any) -> bool:
        if self.device is None or attr in self.propertyExceptions:
            return False

        try:
            setattr(self.device, attr, value)
            return True
        except AlpycaNotImplError:
            self.log.warning(f"[{self.deviceName}] [{attr}] not implemented")
            self.propertyExceptions.append(attr)
            return False
        except Exception as e:
            self.log.error(f"[{self.deviceName}] set [{attr}] exception: [{e}]")
            return False

    def callDeviceMethod(self, method: str, **kwargs: Any) -> Any:
        if not self.deviceConnected:
            return None
        if self.device is None or method in self.propertyExceptions:
            return None

        try:
            return getattr(self.device, method)(**kwargs)
        except AlpycaNotImplError:
            self.log.warning(f"[{self.deviceName}] [{method}] not implemented")
            self.propertyExceptions.append(method)
            return None
        except Exception as e:
            self.log.error(f"[{self.deviceName}] call [{method}] exception: [{e}]")
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

    def workerConnectDevice(self) -> None:
        self.propertyExceptions = []
        self.deviceConnected = False
        self.serverConnected = False

        if not self.createAlpacaDevice():
            self.msg.emit(2, "ALPACA", "Device type error", f"{self.deviceName}")
            return

        suc = False
        for retry in range(0, 10):
            self.setDeviceProp("Connected", True)
            suc = self.getDeviceProp("Connected")

            if suc:
                t = f"[{self.deviceName}] connected, [{retry}] retries"
                self.log.debug(t)
                break
            else:
                t = f" [{self.deviceName}] Connection retry: [{retry}]"
                self.log.info(t)
                time.sleep(0.2)

        if not suc:
            self.msg.emit(2, "ALPACA", "Connect error", f"{self.deviceName}")
            return

        if not self.serverConnected:
            self.serverConnected = True
            self.signals.serverConnected.emit()

        if not self.deviceConnected:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f"{self.deviceName}")
            self.msg.emit(0, "ALPACA", "Device found", f"{self.deviceName}")
            self.startAlpacaTimer()
            self.getInitialConfig()

    def startAlpacaTimer(self) -> None:
        self.cycleData.start(self.updateRate)
        self.cycleDevice.start(self.updateRate)

    def stopAlpacaTimer(self) -> None:
        self.cycleData.stop()
        self.cycleDevice.stop()

    def workerGetInitialConfig(self) -> None:
        self.data["DRIVER_INFO.DRIVER_NAME"] = self.getDeviceProp("Name")
        self.data["DRIVER_INFO.DRIVER_VERSION"] = self.getDeviceProp("DriverVersion")
        self.data["DRIVER_INFO.DRIVER_EXEC"] = self.getDeviceProp("DriverInfo")

    def workerPollStatus(self) -> None:
        suc = self.getDeviceProp("Connected")
        if self.deviceConnected and not suc:
            self.deviceConnected = False
            self.signals.deviceDisconnected.emit(f"{self.deviceName}")
            self.msg.emit(0, "ALPACA", "Device remove", f"{self.deviceName}")

        elif not self.deviceConnected and suc:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f"{self.deviceName}")
            self.msg.emit(0, "ALPACA", "Device found", f"{self.deviceName}")

    def processPolledData(self) -> None:
        pass

    def workerPollData(self) -> None:
        pass

    def pollData(self) -> None:
        if not self.deviceConnected:
            return
        self.workerData = Worker(self.workerPollData)
        self.workerData.signals.result.connect(self.processPolledData)
        self.threadPool.start(self.workerData)

    def pollStatus(self) -> None:
        if not self.deviceConnected:
            return
        self.workerStatus = Worker(self.workerPollStatus)
        self.threadPool.start(self.workerStatus)

    def getInitialConfig(self) -> None:
        if not self.deviceConnected:
            return
        self.workerGetConfig = Worker(self.workerGetInitialConfig)
        self.threadPool.start(self.workerGetConfig)

    def startCommunication(self) -> None:
        self.data.clear()
        self.workerConnect = Worker(self.workerConnectDevice)
        self.threadPool.start(self.workerConnect)

    def stopCommunication(self) -> None:
        self.stopAlpacaTimer()
        self.setDeviceProp("Connected", False)
        self.deviceConnected = False
        self.serverConnected = False
        self.propertyExceptions = []
        self.signals.deviceDisconnected.emit(f"{self.deviceName}")
        self.signals.serverDisconnected.emit({f"{self.deviceName}": 0})
        self.msg.emit(0, "ALPACA", "Device  remove", f"{self.deviceName}")

    def discoverDevices(self, deviceType: str) -> list:
        devices = self.discoverAlpacaDevices()
        if not devices:
            return []

        temp = [x for x in devices if x["DeviceType"].lower() == deviceType]
        discoverList = [f"{x['DeviceName']}:{deviceType}:{x['DeviceNumber']}" for x in temp]
        return discoverList
