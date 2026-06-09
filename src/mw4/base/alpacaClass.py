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
import alpaca.management as alpacaMgmt
from alpaca.camera import Camera as AlpycaCamera
from alpaca.covercalibrator import CoverCalibrator as AlpycaCoverCalibrator
from alpaca.dome import Dome as AlpycaDome
from alpaca.filterwheel import FilterWheel as AlpycaFilterWheel
from alpaca.focuser import Focuser as AlpycaFocuser
from alpaca.observingconditions import ObservingConditions as AlpycaObsConditions
from alpaca.switch import Switch as AlpycaSwitch
from alpaca.telescope import Telescope as AlpycaTelescope
from dataclasses import dataclass, field
from mw4.base.alpacaAscomCommon import AlpacaAscomCommon
from mw4.base.tpool import Worker
from typing import Any


@dataclass
class DeviceConfigAlpaca:
    deviceName: str = field(default="")
    hostAddress: str = field(default="127.0.0.1")
    port: int = field(default=11111)
    protocol: str = field(default="http")
    loadConfig: bool = field(default=False)
    apiVersion: int = field(default=1)
    number: int = field(default=0)


class AlpacaClass(AlpacaAscomCommon):
    PROTOCOL_NAME: str = "ALPACA"
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
        super().__init__(parent)
        self.config = DeviceConfigAlpaca()
        self.workerCommunicationLoop: Worker | None = None

    def startCommunication(self) -> None:
        self.deviceConnected = False
        self.serverConnected = False
        self.data.clear()
        self.propertyExceptions.clear()
        self.stopEvent.clear()
        self.workerCommunicationLoop = Worker(self.runnerCommunicationLoop)
        self.threadPool.start(self.workerCommunicationLoop)

    def createAlpacaDevice(self, deviceType: str) -> bool:
        deviceClass = self.DEVICE_TYPE_MAP.get(deviceType)
        if deviceClass is None:
            self.log.warning(f"Unknown device type: [{deviceType}]")
            return False

        address = f"{self.config.hostAddress}:{self.config.port}"
        try:
            self.device = deviceClass(address, self.config.number, self.config.protocol)
        except Exception as e:
            self.log.error(f"Create device exception: [{e}]")
            return False

        self.log.debug(f"Created device at [{address}]")
        return True

    def discoverAPIVersion(self) -> int:
        address = f"{self.config.hostAddress}:{self.config.port}"
        try:
            versions = alpacaMgmt.apiversions(address)
            if not versions:
                return 0
            return max(versions)
        except Exception as e:
            self.log.error(f"Discover API exception: [{e}]")
            return 0

    def discoverAlpacaDevices(self, hostaddress: str, port: int) -> list:
        address = f"{hostaddress}:{port}"
        try:
            return alpacaMgmt.configureddevices(address)
        except Exception as e:
            self.log.error(f"Search devices exception: [{e}]")
            return []

    def discoverDevices(self, deviceType: str, hostaddress: str, port: int) -> list:
        devices = self.discoverAlpacaDevices(hostaddress, port)
        if not devices:
            return []

        temp = [x for x in devices if x["DeviceType"].lower() == deviceType]
        discoverList = [f"{x['DeviceName']}:{deviceType}:{x['DeviceNumber']}" for x in temp]
        self.log.debug(f"Discovered [{deviceType}] devices at [{discoverList}]")
        return discoverList
