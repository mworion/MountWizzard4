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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from functools import partial

# external packages
import numpy as np

# local import
from gui.utilities.toolsQtWidget import MWidget


class EnvironWeather(MWidget):
    """
    """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.refractionSource = ''
        self.filteredTemperature = np.full(60, 0)
        self.filteredPressure = np.full(60, 950)
        self.seeingEnabled = False

        self.refractionSources = {
            'sensor1Weather': {'group': self.ui.sensor1Group,
                               'data': self.app.sensor1Weather.data,
                               'signals': self.app.sensor1Weather.signals,
                               'uiPost': '1',
                               },
            'sensor2Weather': {'group': self.ui.sensor2Group,
                               'data': self.app.sensor2Weather.data,
                               'signals': self.app.sensor2Weather.signals,
                               'uiPost': '2',
                               },
            'sensor3Weather': {'group': self.ui.sensor3Group,
                               'data': self.app.sensor3Weather.data,
                               'signals': self.app.sensor3Weather.signals,
                               'uiPost': '3',
                               },
            'onlineWeather': {'group': self.ui.onlineGroup,
                              'data': self.app.onlineWeather.data,
                              'signals': self.app.onlineWeather.signals,
                              'uiPost': 'Online',
                              },
            'directWeather': {'group': self.ui.directGroup,
                              'data': self.app.directWeather.data,
                              'signals': self.app.directWeather.signals,
                              'uiPost': 'Direct',
                              },
        }

        for source in self.refractionSources:
            self.refractionSources[source]['signals'].deviceDisconnected.connect(
                partial(self.clearSourceGui, source))
            self.refractionSources[source]['group'].clicked.connect(
                partial(self.selectRefractionSource, source))

        self.envFields = {
            'temperature': {
                'valueKey': 'WEATHER_PARAMETERS.WEATHER_TEMPERATURE',
                'format': '4.1f',
            },
            'pressure': {
                'valueKey': 'WEATHER_PARAMETERS.WEATHER_PRESSURE',
                'format': '4.0f',
            },
            'humidity': {
                'valueKey': 'WEATHER_PARAMETERS.WEATHER_HUMIDITY',
                'format': '3.0f',
            },
            'dewPoint': {
                'valueKey': 'WEATHER_PARAMETERS.WEATHER_DEWPOINT',
                'format': '4.1f',
            },
            'cloudCover': {
                'valueKey': 'WEATHER_PARAMETERS.CloudCover',
                'format': '3.0f',
            },
            'rainVol': {
                'valueKey': 'WEATHER_PARAMETERS.RainVol',
                'format': '5.2f',
            },
            'SQR': {
                'valueKey': 'SKY_QUALITY.SKY_BRIGHTNESS',
                'format': '4.1f',
            }
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

    def initConfig(self):
        """
        """
        config = self.app.config['mainW']
        self.ui.refracManual.setChecked(config.get('refracManual', False))
        self.ui.refracCont.setChecked(config.get('refracCont', False))
        self.ui.refracNoTrack.setChecked(config.get('refracNoTrack', False))
        self.refractionSource = config.get('refractionSource', '')
        self.setRefractionSourceGui()

    def storeConfig(self):
        """
        """
        config = self.app.config['mainW']
        config['refracManual'] = self.ui.refracManual.isChecked()
        config['refracCont'] = self.ui.refracCont.isChecked()
        config['refracNoTrack'] = self.ui.refracNoTrack.isChecked()
        config['refractionSource'] = self.refractionSource

    def smartEnvironGui(self):
        """
        smartEnvironGui enables and disables gui actions depending on the actual
        state of the different environment devices. it is run every 1 second
        synchronously, because it can't be simpler done with dynamic approach.
        all different situations in a running environment is done locally.

        """
        for source in self.refractionSources:
            stat = self.app.deviceStat.get(source, None)
            group = self.refractionSources[source]['group']
            if stat is None:
                group.setFixedWidth(0)
                group.setEnabled(False)
            elif stat:
                group.setMinimumSize(75, 0)
                group.setEnabled(True)
            else:
                group.setMinimumSize(75, 0)
                group.setEnabled(False)

    def updateRefractionUpdateType(self):
        """
        """
        if self.refractionSource != 'directWeather':
            return False

        setting = self.app.mount.setting
        if setting.weatherStatus == 0:
            self.ui.refracManual.setChecked(True)
        elif setting.weatherStatus == 1:
            self.ui.refracNoTrack.setChecked(True)
        elif setting.weatherStatus == 2:
            self.ui.refracCont.setChecked(True)
        else:
            return False
        return True

    def setRefractionUpdateType(self):
        """
        """
        if not self.ui.showTabEnviron.isChecked():
            return False
        if self.refractionSource != 'directWeather':
            suc = self.app.mount.setting.setDirectWeatherUpdateType(0)
            return suc

        if self.app.mount.setting.weatherStatus == 0:
            self.ui.refracCont.setChecked(True)

        # otherwise, we have to switch it on or off
        if self.ui.refracManual.isChecked():
            suc = self.app.mount.setting.setDirectWeatherUpdateType(0)
        elif self.ui.refracNoTrack.isChecked():
            suc = self.app.mount.setting.setDirectWeatherUpdateType(1)
        else:
            suc = self.app.mount.setting.setDirectWeatherUpdateType(2)
        return suc

    def setRefractionSourceGui(self):
        """
        """
        for source in self.refractionSources:
            if self.refractionSource == source:
                self.changeStyleDynamic(
                    self.refractionSources[source]['group'], 'refraction', True)
                self.refractionSources[source]['group'].setChecked(True)
            else:
                self.changeStyleDynamic(
                    self.refractionSources[source]['group'], 'refraction', False)
                self.refractionSources[source]['group'].setChecked(False)

    def selectRefractionSource(self, source):
        """
        """
        if self.refractionSources[source]['group'].isChecked():
            self.refractionSource = source
        else:
            self.refractionSource = ''

        self.setRefractionSourceGui()
        self.setRefractionUpdateType()

    def updateFilterRefractionParameters(self) -> bool:
        """
        """
        if self.refractionSource not in ['sensor1Weather', 'sensor2Weather',
                                         'sensor3Weather', 'onlineWeather']:
            return False

        key = 'WEATHER_PARAMETERS.WEATHER_TEMPERATURE'
        temp = self.refractionSources[self.refractionSource]['data'].get(key, 0)
        key = 'WEATHER_PARAMETERS.WEATHER_PRESSURE'
        press = self.refractionSources[self.refractionSource]['data'].get(key, 950)

        if temp is not None:
            self.filteredTemperature = np.roll(self.filteredTemperature, 1)
            self.filteredTemperature[0] = temp

        if press is not None:
            self.filteredPressure = np.roll(self.filteredPressure, 1)
            self.filteredPressure[0] = press
        return True

    def movingAverageRefractionParameters(self) -> tuple:
        """
        """
        temp = np.mean(self.filteredTemperature)
        press = np.mean(self.filteredPressure)
        return temp, press

    def updateRefractionParameters(self) -> bool:
        """
        """
        if self.refractionSource == 'directWeather':
            return False
        if not self.app.deviceStat['mount']:
            return False

        temp, press = self.movingAverageRefractionParameters()
        if self.ui.refracManual.isChecked():
            return False
        if self.ui.refracNoTrack.isChecked():
            if self.app.mount.obsSite.status == 0:
                return False

        suc = self.app.mount.setting.setRefractionParam(temperature=temp,
                                                        pressure=press)
        self.log.debug(f'Setting refrac temp:[{temp}], press:[{press}]')
        if not suc:
            self.msg.emit(2, 'System', 'Environment', 'No refraction update')
            return False
        return True

    def updateSourceGui(self) -> bool:
        """
        """
        for source in self.refractionSources:
            data = self.refractionSources[source]['data']
            uiPost = self.refractionSources[source]['uiPost']
            for field in self.envFields:
                ui = eval('self.ui.' + field + uiPost)
                value = data.get(self.envFields[field]['valueKey'])
                self.guiSetText(ui, self.envFields[field]['format'], value)

    def clearSourceGui(self, source: str, sender) -> bool:
        """
        """
        self.refractionSources[source]['data'].clear()
        self.ui.meteoblueIcon.setVisible(False)
        self.ui.meteoblueSeeing.setVisible(False)
        self.updateSourceGui()
