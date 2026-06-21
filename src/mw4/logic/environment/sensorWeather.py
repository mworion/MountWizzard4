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
import logging
import platform
from mw4.base.signalsDevices import Signals
from mw4.logic.environment.sensorWeatherAlpaca import SensorWeatherAlpaca
from mw4.logic.environment.sensorWeatherBoltwood import SensorWeatherBoltwood
from mw4.logic.environment.sensorWeatherIndi import SensorWeatherIndi
from mw4.logic.environment.sensorWeatherOnline import SensorWeatherOnline
from collections.abc import Any

if platform.system() == "Windows":
    from mw4.logic.environment.sensorWeatherAscom import SensorWeatherAscom


class SensorWeather:
    log = logging.getLogger("MW4")
    DEVICE_TYPE: str = "observingconditions"

    def __init__(self, app: Any) -> None:
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data: dict[str, Any] = {}
        self.framework: str = ""
        self.run: dict[str, Any] = {
            "indi": SensorWeatherIndi(self),
            "alpaca": SensorWeatherAlpaca(self),
            "boltwood": SensorWeatherBoltwood(self),
            "online": SensorWeatherOnline(self),
        }
        if platform.system() == "Windows":
            self.run["ascom"] = SensorWeatherAscom(self)

    def startCommunication(self) -> None:
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        self.run[self.framework].stopCommunication()
