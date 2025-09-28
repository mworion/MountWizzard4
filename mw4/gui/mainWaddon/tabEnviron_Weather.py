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
from functools import partial

# external packages
import numpy as np
from PySide6.QtCore import QObject

# local import
from gui.utilities.toolsQtWidget import changeStyleDynamic, guiSetText


class EnvironWeather(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.refractionSource = ""
        self.filteredTemperature = np.full(60, -99)
        self.filteredPressure = np.full(60, 0)
        self.seeingEnabled = False

        self.refractionSources = {
            "sensor1Weather": {
                "group": self.ui.sensor1Group,
                "data": self.app.sensor1Weather.data,
                "signals": self.app.sensor1Weather.signals,
                "uiPost": "1",
            },
            "sensor2Weather": {
                "group": self.ui.sensor2Group,
                "data": self.app.sensor2Weather.data,
                "signals": self.app.sensor2Weather.signals,
                "uiPost": "2",
            },
            "sensor3Weather": {
                "group": self.ui.sensor3Group,
                "data": self.app.sensor3Weather.data,
                "signals": self.app.sensor3Weather.signals,
                "uiPost": "3",
            },
            "onlineWeather": {
                "group": self.ui.onlineGroup,
                "data": self.app.onlineWeather.data,
                "signals": self.app.onlineWeather.signals,
                "uiPost": "Online",
            },
            "directWeather": {
                "group": self.ui.directGroup,
                "data": self.app.directWeather.data,
                "signals": self.app.directWeather.signals,
                "uiPost": "Direct",
            },
        }

        for source in self.refractionSources:
            self.refractionSources[source]["signals"].deviceDisconnected.connect(
                partial(self.clearSourceGui, source)
            )
            self.refractionSources[source]["group"].clicked.connect(
                partial(self.selectRefractionSource, source)
            )

        self.envFields = {
            "temperature": {
                "valueKey": "WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
                "format": "4.1f",
            },
            "pressure": {
                "valueKey": "WEATHER_PARAMETERS.WEATHER_PRESSURE",
                "format": "4.0f",
            },
            "humidity": {
                "valueKey": "WEATHER_PARAMETERS.WEATHER_HUMIDITY",
                "format": "3.0f",
            },
            "dewPoint": {
                "valueKey": "WEATHER_PARAMETERS.WEATHER_DEWPOINT",
                "format": "4.1f",
            },
            "cloudCover": {
                "valueKey": "WEATHER_PARAMETERS.CloudCover",
                "format": "3.0f",
            },
            "rainVol": {
                "valueKey": "WEATHER_PARAMETERS.RainVol",
                "format": "5.2f",
            },
            "SQR": {
                "valueKey": "SKY_QUALITY.SKY_BRIGHTNESS",
                "format": "4.1f",
            },
        }

        # weather functions
        self.app.mount.signals.settingDone.connect(self.updateSourceGui)
        self.app.mount.signals.settingDone.connect(self.updateRefractionUpdateType)
        self.ui.refracManual.clicked.connect(self.setRefractionUpdateType)
        self.ui.refracCont.clicked.connect(self.setRefractionUpdateType)
        self.ui.refracNoTrack.clicked.connect(self.setRefractionUpdateType)

        # cyclic functions
        self.app.update1s.connect(self.smartEnvironGui)
        self.app.update1s.connect(self.updateSourceGui)
        self.app.update1s.connect(self.updateFilterRefractionParameters)
        self.app.update1s.connect(self.updateRefractionParameters)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.ui.refracManual.setChecked(config.get("refracManual", False))
        self.ui.refracCont.setChecked(config.get("refracCont", False))
        self.ui.refracNoTrack.setChecked(config.get("refracNoTrack", False))
        self.refractionSource = config.get("refractionSource", "")
        self.setRefractionSourceGui()

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["refracManual"] = self.ui.refracManual.isChecked()
        config["refracCont"] = self.ui.refracCont.isChecked()
        config["refracNoTrack"] = self.ui.refracNoTrack.isChecked()
        config["refractionSource"] = self.refractionSource

    def smartEnvironGui(self) -> None:
        """ """
        for source in self.refractionSources:
            stat = self.app.deviceStat.get(source, None)
            group = self.refractionSources[source]["group"]
            if stat is None:
                group.setFixedWidth(0)
                group.setEnabled(False)
            elif stat:
                group.setMinimumSize(75, 0)
                group.setEnabled(True)
            else:
                group.setMinimumSize(75, 0)
                group.setEnabled(False)

    def updateRefractionUpdateType(self) -> None:
        """ """
        if self.refractionSource != "directWeather":
            return

        setting = self.app.mount.setting
        if setting.weatherStatus == 0:
            self.ui.refracManual.setChecked(True)
        elif setting.weatherStatus == 1:
            self.ui.refracNoTrack.setChecked(True)
        elif setting.weatherStatus == 2:
            self.ui.refracCont.setChecked(True)

    def setRefractionUpdateType(self) -> None:
        """ """
        if not self.ui.showTabEnviron.isChecked():
            return
        if self.refractionSource != "directWeather":
            self.app.mount.setting.setDirectWeatherUpdateType(0)
            return

        if self.app.mount.setting.weatherStatus == 0:
            self.ui.refracCont.setChecked(True)

        # otherwise, we have to switch it on or off
        if self.ui.refracManual.isChecked():
            self.app.mount.setting.setDirectWeatherUpdateType(0)
        elif self.ui.refracNoTrack.isChecked():
            self.app.mount.setting.setDirectWeatherUpdateType(1)
        else:
            self.app.mount.setting.setDirectWeatherUpdateType(2)

    def setRefractionSourceGui(self) -> None:
        """ """
        for source in self.refractionSources:
            if self.refractionSource == source:
                changeStyleDynamic(self.refractionSources[source]["group"], "refraction", True)
                self.refractionSources[source]["group"].setChecked(True)
            else:
                changeStyleDynamic(
                    self.refractionSources[source]["group"], "refraction", False
                )
                self.refractionSources[source]["group"].setChecked(False)

    def selectRefractionSource(self, source: str) -> None:
        """ """
        if self.refractionSources[source]["group"].isChecked():
            self.refractionSource = source
        else:
            self.refractionSource = ""

        self.setRefractionSourceGui()
        self.setRefractionUpdateType()

    def updateFilterRefractionParameters(self) -> None:
        """ """
        if self.refractionSource not in [
            "sensor1Weather",
            "sensor2Weather",
            "sensor3Weather",
            "onlineWeather",
        ]:
            return

        key = "WEATHER_PARAMETERS.WEATHER_TEMPERATURE"
        temp = self.refractionSources[self.refractionSource]["data"].get(key, -99)
        key = "WEATHER_PARAMETERS.WEATHER_PRESSURE"
        press = self.refractionSources[self.refractionSource]["data"].get(key, 0)

        if all(i == -99 for i in self.filteredTemperature):
            self.filteredTemperature = np.full(60, temp)

        if all(i == 0 for i in self.filteredPressure):
            self.filteredPressure = np.full(60, press)

        if temp is not None:
            self.filteredTemperature = np.roll(self.filteredTemperature, 1)
            self.filteredTemperature[0] = temp

        if press is not None:
            self.filteredPressure = np.roll(self.filteredPressure, 1)
            self.filteredPressure[0] = press

    def movingAverageRefractionParameters(self) -> tuple:
        """ """
        temp = np.mean(self.filteredTemperature)
        press = np.mean(self.filteredPressure)
        return temp, press

    def updateRefractionParameters(self) -> None:
        """ """
        if self.refractionSource == "directWeather":
            return
        if not self.app.deviceStat["mount"]:
            return

        temp, press = self.movingAverageRefractionParameters()
        if self.ui.refracManual.isChecked():
            return
        if self.ui.refracNoTrack.isChecked():
            if self.app.mount.obsSite.status == 0:
                return

        self.mainW.log.debug(f"Setting refrac temp:[{temp}], press:[{press}]")
        if not self.app.mount.setting.setRefractionParam(temperature=temp, pressure=press):
            self.msg.emit(2, "System", "Environment", "No refraction update")

    def updateSourceGui(self) -> None:
        """ """
        for source in self.refractionSources:
            data = self.refractionSources[source]["data"]
            uiPost = self.refractionSources[source]["uiPost"]
            for field in self.envFields:
                ui = eval("self.ui." + field + uiPost)
                value = data.get(self.envFields[field]["valueKey"])
                guiSetText(ui, self.envFields[field]["format"], value)

    def clearSourceGui(self, source: str, sender) -> None:
        """ """
        self.refractionSources[source]["data"].clear()
        self.ui.meteoblueIcon.setVisible(False)
        self.ui.meteoblueSeeing.setVisible(False)
        self.updateSourceGui()
