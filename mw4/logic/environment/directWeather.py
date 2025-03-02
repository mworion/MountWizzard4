############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages

# local imports
from base.signalsDevices import Signals
from mountcontrol.setting import Setting


class DirectWeather:
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, app=None):
        self.app = app
        self.signals = Signals()

        # minimum set for driver package built in
        self.framework = ""
        self.run = {"directWeather": self}
        self.deviceName = ""
        self.data = {}
        self.defaultConfig = {
            "framework": "",
            "frameworks": {"directWeather": {"deviceName": "On Mount"}},
        }
        self.running = False
        self.enabled = False
        self.app.mount.signals.settingDone.connect(self.updateData)

    def startCommunication(self) -> None:
        """ """
        self.enabled = True
        self.app.deviceStat["directWeather"] = False

    def stopCommunication(self) -> None:
        """ """
        self.enabled = False
        self.running = False
        self.app.deviceStat["directWeather"] = None
        self.data.clear()
        self.signals.deviceDisconnected.emit("DirectWeather")

    def updateData(self, sett: Setting) -> None:
        """ """
        if not self.enabled:
            return False

        value1 = sett.weatherTemperature
        value2 = sett.weatherPressure
        value3 = sett.weatherDewPoint
        value4 = sett.weatherHumidity
        value5 = sett.weatherAge
        isValid = None not in [value1, value2, value3, value4, value5]

        if not isValid and self.running:
            self.signals.deviceDisconnected.emit("DirectWeather")
            self.running = False
        elif isValid and not self.running:
            self.signals.deviceConnected.emit("DirectWeather")
            self.running = True

        self.app.deviceStat["directWeather"] = isValid
        self.data["WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = value1
        self.data["WEATHER_PARAMETERS.WEATHER_PRESSURE"] = value2
        self.data["WEATHER_PARAMETERS.WEATHER_DEWPOINT"] = value3
        self.data["WEATHER_PARAMETERS.WEATHER_HUMIDITY"] = value4
        self.data["WEATHER_PARAMETERS.WEATHER_AGE"] = value5
