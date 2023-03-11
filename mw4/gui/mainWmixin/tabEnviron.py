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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import platform
import webbrowser

# external packages
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem

# local import


class Environ:
    """
    """

    def __init__(self):
        self.refractionSources = {'onlineWeather': self.ui.onlineWeatherGroup,
                                  'sensorWeather': self.ui.sensorWeatherGroup,
                                  'directWeather': self.ui.directWeatherGroup,
                                  }
        self.refractionSource = ''
        self.filteredTemperature = None
        self.filteredPressure = None
        self.seeingEnabled = False

        signals = self.app.sensorWeather.signals
        signals.deviceDisconnected.connect(self.clearSensorWeatherGui)
        signals = self.app.skymeter.signals
        signals.deviceDisconnected.connect(self.clearSkymeterGui)
        signals = self.app.onlineWeather.signals
        signals.deviceDisconnected.connect(self.clearOnlineWeatherGui)
        signals = self.app.directWeather.signals
        signals.deviceDisconnected.connect(self.clearDirectWeatherGui)
        signals = self.app.powerWeather.signals
        signals.deviceDisconnected.connect(self.clearPowerWeatherGui)
        signals = self.app.seeingWeather.signals
        signals.deviceDisconnected.connect(self.clearSeeingEntries)
        signals = self.app.seeingWeather.signals
        signals.deviceConnected.connect(self.prepareSeeingTable)

        # weather functions
        self.app.mount.signals.settingDone.connect(self.updateDirectWeatherGui)
        self.app.mount.signals.settingDone.connect(self.updateRefractionUpdateType)
        # gui connections
        self.ui.onlineWeatherGroup.clicked.connect(self.selectRefractionSource)
        self.ui.sensorWeatherGroup.clicked.connect(self.selectRefractionSource)
        self.ui.directWeatherGroup.clicked.connect(self.selectRefractionSource)
        self.ui.refracManual.clicked.connect(self.setRefractionUpdateType)
        self.ui.refracCont.clicked.connect(self.setRefractionUpdateType)
        self.ui.refracNoTrack.clicked.connect(self.setRefractionUpdateType)
        self.ui.unitTimeUTC.toggled.connect(self.updateSeeingEntries)
        self.app.seeingWeather.signals.update.connect(self.prepareSeeingTable)
        self.clickable(self.ui.meteoblueIcon).connect(self.openMeteoblue)
        # cyclic functions
        self.app.update1s.connect(self.smartEnvironGui)
        self.app.update1s.connect(self.updateFilterRefractionParameters)
        self.app.update1s.connect(self.updateRefractionParameters)
        self.app.update1s.connect(self.updateSkymeterGui)
        self.app.update1s.connect(self.updatePowerWeatherGui)
        self.app.update1s.connect(self.updateSensorWeatherGui)
        self.app.update1s.connect(self.updateOnlineWeatherGui)
        self.app.start3s.connect(self.enableSeeingEntries)
        self.app.update30m.connect(self.updateSeeingEntries)
        self.app.colorChange.connect(self.prepareSeeingTable)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.refracManual.setChecked(config.get('refracManual', False))
        self.ui.refracCont.setChecked(config.get('refracCont', False))
        self.ui.refracNoTrack.setChecked(config.get('refracNoTrack', False))
        self.refractionSource = config.get('refractionSource', '')
        self.setRefractionSourceGui()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['refracManual'] = self.ui.refracManual.isChecked()
        config['refracCont'] = self.ui.refracCont.isChecked()
        config['refracNoTrack'] = self.ui.refracNoTrack.isChecked()
        config['refractionSource'] = self.refractionSource
        return True

    def smartEnvironGui(self):
        """
        smartEnvironGui enables and disables gui actions depending on the actual
        state of the different environment devices. it is run every 1 second
        synchronously, because it can't be simpler done with dynamic approach.
        all different situations in a running environment is done locally.

        :return: true for test purpose
        """
        environ = {
            'directWeather': self.ui.directWeatherGroup,
            'sensorWeather': self.ui.sensorWeatherGroup,
            'onlineWeather': self.ui.onlineWeatherGroup,
            'skymeter': self.ui.skymeterGroup,
            'powerWeather': self.ui.powerGroup,
        }
        for key, group in environ.items():
            stat = self.deviceStat.get(key, None)
            if stat is None:
                group.setFixedWidth(0)
                group.setEnabled(False)
            elif stat:
                group.setMinimumSize(75, 0)
                group.setEnabled(True)
            else:
                group.setMinimumSize(75, 0)
                group.setEnabled(False)
        return True

    def updateRefractionUpdateType(self):
        """
        :return: success
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
        :return: success
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
        setRefractionSourceGui sets the gui elements to a recognizable setting
        and disables all others

        :return: success
        """
        for source, group in self.refractionSources.items():
            if self.refractionSource == source:
                self.changeStyleDynamic(group, 'refraction', True)
                group.setChecked(True)
            else:
                self.changeStyleDynamic(group, 'refraction', False)
                group.setChecked(False)
        return True

    def selectRefractionSource(self):
        """
        selectRefractionSource receives all button presses on groups and checks
        which of the groups was clicked on. with that information is detects the
        index in the list of groups.

        :return: success
        """
        old = self.refractionSource

        for source, group in self.refractionSources.items():
            if group != self.sender():
                continue
            if group.isChecked():
                self.refractionSource = source
            else:
                self.refractionSource = ''

        if old != self.refractionSource:
            self.filteredTemperature = None
            self.filteredPressure = None

        self.setRefractionSourceGui()
        self.setRefractionUpdateType()
        return True

    def updateFilterRefractionParameters(self):
        """
        updateFilter initializes the filter with the first values or is rolling
        the moving average

        :return:
        """
        if self.refractionSource == 'sensorWeather':
            key = 'WEATHER_PARAMETERS.WEATHER_TEMPERATURE'
            temp = self.app.sensorWeather.data.get(key)
            key = 'WEATHER_PARAMETERS.WEATHER_PRESSURE'
            press = self.app.sensorWeather.data.get(key)
        elif self.refractionSource == 'onlineWeather':
            key = 'WEATHER_PARAMETERS.WEATHER_TEMPERATURE'
            temp = self.app.onlineWeather.data.get(key)
            key = 'WEATHER_PARAMETERS.WEATHER_PRESSURE'
            press = self.app.onlineWeather.data.get(key)
        else:
            temp = None
            press = None

        if temp is None or press is None or press < 500:
            self.filteredTemperature = None
            self.filteredPressure = None
            return False

        if self.filteredTemperature is None:
            self.filteredTemperature = np.full(100, temp)
        else:
            self.filteredTemperature = np.roll(self.filteredTemperature, 1)
            self.filteredTemperature[0] = temp

        if self.filteredPressure is None:
            self.filteredPressure = np.full(100, press)
        else:
            self.filteredPressure = np.roll(self.filteredPressure, 1)
            self.filteredPressure[0] = press

        return True

    def movingAverageRefractionParameters(self):
        """
        getFilteredRefracParams filters local temperature and pressure with and
        moving average filter over 100 seconds and returns the filtered values.

        :return:  temperature and pressure
        """
        if self.filteredTemperature is None or self.filteredPressure is None:
            return None, None

        temp = np.mean(self.filteredTemperature)
        press = np.mean(self.filteredPressure)
        return temp, press

    def updateRefractionParameters(self):
        """
        updateRefractionParameters takes the actual conditions for update into
        account and does the update of the refraction parameters. this could be
        done during when mount is not in tracking state or continuously

        :return: success if update happened
        """
        if self.refractionSource == 'directWeather':
            return False
        if not self.deviceStat['mount']:
            return False

        temp, press = self.movingAverageRefractionParameters()
        if temp is None or press is None:
            return False
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

    def updateSensorWeatherGui(self):
        """
        :return:    True if ok for testing
        """
        value = self.app.sensorWeather.data.get(
            'WEATHER_PARAMETERS.WEATHER_TEMPERATURE')
        self.guiSetText(self.ui.sensorWeatherTemp, '4.1f', value)
        value = self.app.sensorWeather.data.get(
            'WEATHER_PARAMETERS.WEATHER_PRESSURE')
        self.guiSetText(self.ui.sensorWeatherPress, '4.1f', value)
        value = self.app.sensorWeather.data.get(
            'WEATHER_PARAMETERS.WEATHER_DEWPOINT')
        self.guiSetText(self.ui.sensorWeatherDewPoint, '4.1f', value)
        value = self.app.sensorWeather.data.get(
            'WEATHER_PARAMETERS.WEATHER_HUMIDITY')
        self.guiSetText(self.ui.sensorWeatherHumidity, '3.0f', value)
        return True

    def clearSensorWeatherGui(self, deviceName=''):
        """
        :param deviceName:
        :return: true for test purpose
        """
        self.app.sensorWeather.data.clear()
        self.ui.meteoblueIcon.setVisible(False)
        self.ui.meteoblueSeeing.setVisible(False)
        self.updateSensorWeatherGui()
        return True

    def updateSkymeterGui(self):
        """
        :return:    True if ok for testing
        """
        value = self.app.skymeter.data.get('SKY_QUALITY.SKY_BRIGHTNESS')
        self.guiSetText(self.ui.skymeterSQR, '5.2f', value)
        value = self.app.skymeter.data.get('SKY_QUALITY.SKY_TEMPERATURE')
        self.guiSetText(self.ui.skymeterTemp, '4.1f', value)
        return True

    def clearSkymeterGui(self, deviceName=''):
        """
        :param deviceName:
        :return: true for test purpose
        """
        self.app.skymeter.data.clear()
        self.updateSkymeterGui()
        return True

    def updatePowerWeatherGui(self):
        """
        updatePowerGui changes the style of the button related to the state of
        the Pegasus UPB device

        :return: success for test
        """
        value = self.app.powerWeather.data.get('WEATHER_PARAMETERS.WEATHER_TEMPERATURE')
        self.guiSetText(self.ui.powerTemp, '4.1f', value)
        value = self.app.powerWeather.data.get('WEATHER_PARAMETERS.WEATHER_HUMIDITY')
        self.guiSetText(self.ui.powerHumidity, '3.0f', value)
        value = self.app.powerWeather.data.get('WEATHER_PARAMETERS.WEATHER_DEWPOINT')
        self.guiSetText(self.ui.powerDewPoint, '4.1f', value)
        return True

    def clearPowerWeatherGui(self):
        """
        clearPowerWeatherGui changes the state of the Pegasus values to '-'

        :return: success for test
        """
        self.app.powerWeather.data.clear()
        self.updatePowerWeatherGui()
        return True

    def updateOnlineWeatherGui(self):
        """
        :return: success
        """
        value = self.app.onlineWeather.data.get('temperature')
        self.guiSetText(self.ui.onlineWeatherTemp, '4.1f', value)
        value = self.app.onlineWeather.data.get('pressure')
        self.guiSetText(self.ui.onlineWeatherPress, '5.1f', value)
        value = self.app.onlineWeather.data.get('humidity')
        self.guiSetText(self.ui.onlineWeatherHumidity, '3.0f', value)
        value = self.app.onlineWeather.data.get('dewPoint')
        self.guiSetText(self.ui.onlineWeatherDewPoint, '4.1f', value)
        value = self.app.onlineWeather.data.get('cloudCover')
        self.guiSetText(self.ui.onlineWeatherCloudCover, '3.0f', value)
        value = self.app.onlineWeather.data.get('rain')
        self.guiSetText(self.ui.onlineWeatherRainVol, '5.2f', value)
        return True

    def clearOnlineWeatherGui(self):
        """
        updateOnlineWeatherGui takes the returned data from the dict to the Gui

        :return: true for test purpose
        """
        self.app.onlineWeather.data.clear()
        self.updateOnlineWeatherGui()
        return True

    def updateDirectWeatherGui(self):
        """
        :return: success
        """
        value = self.app.directWeather.data.get(
            'WEATHER_PARAMETERS.WEATHER_TEMPERATURE')
        self.guiSetText(self.ui.directWeatherTemp, '4.1f', value)
        value = self.app.directWeather.data.get(
            'WEATHER_PARAMETERS.WEATHER_PRESSURE')
        self.guiSetText(self.ui.directWeatherPress, '4.1f', value)
        value = self.app.directWeather.data.get(
            'WEATHER_PARAMETERS.WEATHER_DEWPOINT')
        self.guiSetText(self.ui.directWeatherDewPoint, '4.1f', value)
        value = self.app.directWeather.data.get(
            'WEATHER_PARAMETERS.WEATHER_HUMIDITY')
        self.guiSetText(self.ui.directWeatherHumidity, '3.0f', value)
        return True

    def clearDirectWeatherGui(self):
        """
        updateOnlineWeatherGui takes the returned data from the dict to the Gui

        :return: true for test purpose
        """
        self.app.directWeather.data.clear()
        self.updateDirectWeatherGui()
        return True

    def addSkyfieldTimeObject(self, data):
        """
        :param data:
        :return:
        """
        ts = self.app.mount.obsSite.ts
        data['time'] = []

        for date, hour in zip(data['date'], data['hour']):
            y, m, d = date.split('-')
            data['time'].append(ts.utc(int(y), int(m), int(d), hour, 0, 0))
        return True

    def updateSeeingEntries(self):
        """
        :return:
        """
        if 'hourly' not in self.app.seeingWeather.data:
            return False

        self.ui.seeingGroup.setTitle('Seeing data ' + self.timeZoneString())
        ts = self.app.mount.obsSite.ts
        fields = ['time', 'time', 'high_clouds', 'mid_clouds', 'low_clouds',
                  'seeing_arcsec', 'seeing1', 'seeing2', 'temperature',
                  'relative_humidity', 'badlayer_top', 'badlayer_bottom',
                  'badlayer_gradient', 'jetstream']
        colorMain = self.cs['M_BLUE'][0]
        colorBlack = self.cs['M_BLACK'][0]
        colorWhite = self.cs['M_WHITE'][0]
        seeTab = self.ui.meteoblueSeeing
        data = self.app.seeingWeather.data['hourly']
        self.addSkyfieldTimeObject(data)

        for i in range(0, 96):
            isActual = abs(data['time'][i] - ts.now()) < 1 / 48

            for j, field in enumerate(fields):
                t = f'{data[field][i]}'
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignHCenter)
                item.setForeground(QColor(self.M_BLUE))

                if j == 0:
                    t = self.convertTime(data[field][i], '%d%b')
                elif j == 1:
                    t = self.convertTime(data[field][i], '%H:00')
                elif j in [2, 3, 4]:
                    color = self.calcHexColor(colorMain, data[field][i] / 100)
                    item.setBackground(QColor(color))
                    item.setForeground(QColor(colorWhite))
                elif j in [6]:
                    color = self.calcHexColor(data['seeing1_color'][i], 0.8)
                    item.setBackground(QColor(color))
                    item.setForeground(QColor(colorBlack))
                elif j in [7]:
                    color = self.calcHexColor(data['seeing2_color'][i], 0.8)
                    item.setBackground(QColor(color))
                    item.setForeground(QColor(colorBlack))
                elif j in [10, 11]:
                    val = float('0' + data[field][i]) / 1000
                    t = f'{val:1.1f}'

                if isActual:
                    item.setForeground(QColor(self.M_PINK))
                    val = data['seeing_arcsec'][i]
                    self.ui.limitForecast.setText(f'{val}')
                    val = self.app.seeingWeather.data['meta']['last_model_update']
                    self.ui.limitForecastDate.setText(f'{val}')
                    columnCenter = i
                else:
                    columnCenter = 1

                item.setText(t)
                seeTab.setItem(j, i, item)

        seeTab.selectColumn(columnCenter + 10)
        return True

    def clearSeeingEntries(self):
        """
        :return:
        """
        self.ui.meteoblueSeeing.clear()
        self.ui.meteoblueIcon.setVisible(False)
        self.ui.meteoblueSeeing.setVisible(False)
        self.seeingEnabled = False
        return True

    def enableSeeingEntries(self):
        """
        :return:
        """
        if not self.seeingEnabled:
            return False

        self.ui.meteoblueIcon.setVisible(True)
        self.ui.meteoblueSeeing.setVisible(True)
        return True

    def prepareSeeingTable(self):
        """
        :return:
        """
        vl = ['Date [dd mon]',
              'Hour [hh:mm]',
              'High clouds  [%]',
              'Mid clouds  [%]',
              'Low clouds [%]',
              'Seeing [arcsec]',
              'Seeing index 1',
              'Seeing index 2',
              'Ground Temp [°C]',
              'Humidity [%]',
              'Bad Layers Top [km]',
              'Bad Layers Bot [km]',
              'Bad Layers [K/100m]',
              'Jet stream [m/s]',
              '',
              ]

        self.seeingEnabled = True
        self.enableSeeingEntries()
        seeTab = self.ui.meteoblueSeeing
        if platform.system() == 'Darwin':
            seeTab.setRowCount(15)
        else:
            seeTab.setRowCount(14)
        seeTab.setColumnCount(96)
        seeTab.setVerticalHeaderLabels(vl)
        seeTab.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        seeTab.verticalHeader().setDefaultSectionSize(18)
        self.updateSeeingEntries()
        seeTab.resizeColumnsToContents()
        return True

    def openMeteoblue(self):
        """
        :return:
        """
        url = 'https://www.meteoblue.com/de/wetter/outdoorsports/seeing'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'Environment', 'Browser failed')
        else:
            self.msg.emit(0, 'System', 'Environment', 'Meteoblue opened')
        return True
