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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import datetime
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
# local import


class SiteStatus(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def local__init__(self):
        ms = self.app.mount.signals
        ms.settDone.connect(self.updateSettingGUI)
        ms.settDone.connect(self.updateSetStatGUI)
        ms.settDone.connect(self.updateLocGUI)

        es = self.app.environment.client.signals
        es.serverConnected.connect(self.indiEnvironConnected)
        es.serverDisconnected.connect(self.indiEnvironDisconnected)
        es.newDevice.connect(self.newEnvironDevice)
        es.removeDevice.connect(self.removeEnvironDevice)
        es.newNumber.connect(self.updateEnvironGUI)
        es.deviceConnected.connect(self.deviceEnvironConnected)
        es.deviceDisconnected.connect(self.deviceEnvironDisconnected)

        self.clickable(self.ui.meridianLimitTrack).connect(self.setMeridianLimitTrack)
        self.clickable(self.ui.meridianLimitSlew).connect(self.setMeridianLimitSlew)
        self.clickable(self.ui.horizonLimitHigh).connect(self.setHorizonLimitHigh)
        self.clickable(self.ui.horizonLimitLow).connect(self.setHorizonLimitLow)
        self.clickable(self.ui.slewRate).connect(self.setSlewRate)
        self.clickable(self.ui.siteLatitude).connect(self.setLatitude)
        self.clickable(self.ui.siteLongitude).connect(self.setLongitude)
        self.clickable(self.ui.siteElevation).connect(self.setElevation)
        self.ui.setRefractionManual.clicked.connect(self.updateRefractionParameters)


    def initConfig(self):
        if 'mainW' not in self.app.config:
            return False
        config = self.app.config['mainW']
        self.ui.checkRefracNone.setChecked(config.get('checkRefracNone', False))
        self.ui.checkRefracCont.setChecked(config.get('checkRefracCont', False))
        self.ui.checkRefracNoTrack.setChecked(config.get('checkRefracNoTrack', False))
        return True

    def storeConfig(self):
        if 'mainW' not in self.app.config:
            self.app.config['mainW'] = {}
        config = self.app.config['mainW']
        config['checkRefracNone'] = self.ui.checkRefracNone.isChecked()
        config['checkRefracCont'] = self.ui.checkRefracCont.isChecked()
        config['checkRefracNoTrack'] = self.ui.checkRefracNoTrack.isChecked()

        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """
        return True

    def clearMountGUI(self):
        """
        clearMountGUI rewrites the gui in case of a special event needed for clearing up

        :return: success for test
        """

        self.updateSettingGUI()
        self.updateSetStatGUI()
        self.updateLocGUI()
        return True

    def updateRefractionParameters(self):
        """
        updateRefractionParameters takes the actual conditions for update into account and
        does the update of the refraction parameters. this could be done during when mount
        is not in tracking state or continuously

        :return: success if update happened
        """

        if not self.app.mount.mountUp:
            return False
        if self.ui.checkRefracNone.isChecked():
            return False
        if self.ui.checkRefracNoTrack.isChecked():
            if self.app.mount.obsSite.status != 0:
                return False
        temp, press = self.app.environment.getFilteredRefracParams()
        if temp is None or press is None:
            return False
        suc = self.app.mount.obsSite.setRefractionParam(temperature=temp,
                                                        pressure=press)
        if not suc:
            self.app.message.emit('Cannot perform refraction update', 2)
            return False
        return True

    def updateSettingGUI(self):
        """
        updateSetGUI update the gui upon events triggered be the reception of new settings
        from the mount. the mount data is polled, so we use this signal as well for the
        update process.

        :return:    True if ok for testing
        """

        sett = self.app.mount.sett

        if sett.slewRate is not None:
            self.ui.slewRate.setText('{0:2.0f}'.format(sett.slewRate))
        else:
            self.ui.slewRate.setText('-')

        if sett.timeToFlip is not None:
            self.ui.timeToFlip.setText('{0:3.0f}'.format(sett.timeToFlip))
        else:
            self.ui.timeToFlip.setText('-')

        if sett.timeToMeridian() is not None:
            self.ui.timeToMeridian.setText('{0:3.0f}'.format(sett.timeToMeridian()))
        else:
            self.ui.timeToMeridian.setText('-')

        if sett.refractionTemp is not None:
            self.ui.refractionTemp.setText('{0:+4.1f}'.format(sett.refractionTemp))
            self.ui.refractionTemp1.setText('{0:+4.1f}'.format(sett.refractionTemp))
        else:
            self.ui.refractionTemp.setText('-')
            self.ui.refractionTemp1.setText('-')

        if sett.refractionPress is not None:
            self.ui.refractionPress.setText('{0:6.1f}'.format(sett.refractionPress))
            self.ui.refractionPress1.setText('{0:6.1f}'.format(sett.refractionPress))
        else:
            self.ui.refractionPress.setText('-')
            self.ui.refractionPress1.setText('-')

        if sett.meridianLimitTrack is not None:
            self.ui.meridianLimitTrack.setText(str(sett.meridianLimitTrack))
        else:
            self.ui.meridianLimitTrack.setText('-')

        if sett.meridianLimitSlew is not None:
            self.ui.meridianLimitSlew.setText(str(sett.meridianLimitSlew))
        else:
            self.ui.meridianLimitSlew.setText('-')

        if sett.horizonLimitLow is not None:
            self.ui.horizonLimitLow.setText(str(sett.horizonLimitLow))
        else:
            self.ui.horizonLimitLow.setText('-')

        if sett.horizonLimitHigh is not None:
            self.ui.horizonLimitHigh.setText(str(sett.horizonLimitHigh))
        else:
            self.ui.horizonLimitHigh.setText('-')

        return True

    def updateSetStatGUI(self):
        """
        updateSetStatGUI update the gui upon events triggered be the reception of new
        settings from the mount. the mount data is polled, so we use this signal as well
        for the update process.

        :return:    True if ok for testing
        """

        sett = self.app.mount.sett

        if sett.UTCExpire is not None:
            ui = self.ui.UTCExpire
            ui.setText(sett.UTCExpire)
            # coloring if close to end:
            now = datetime.datetime.now()
            expire = datetime.datetime.strptime(sett.UTCExpire, '%Y-%m-%d')
            deltaYellow = datetime.timedelta(days=30)
            if now > expire:
                self.changeStyleDynamic(ui, 'color', 'red')
            elif now > expire - deltaYellow:
                self.changeStyleDynamic(ui, 'color', 'yellow')
            else:
                self.changeStyleDynamic(ui, 'color', '')
        else:
            self.ui.UTCExpire.setText('-')

        if sett.statusUnattendedFlip is not None:
            self.ui.statusUnattendedFlip.setText('ON' if sett.statusUnattendedFlip else 'OFF')
        else:
            self.ui.statusUnattendedFlip.setText('-')

        if sett.statusDualTracking is not None:
            self.ui.statusDualTracking.setText('ON' if sett.statusDualTracking else 'OFF')
        else:
            self.ui.statusDualTracking.setText('-')

        if sett.statusRefraction is not None:
            self.ui.statusRefraction.setText('ON' if sett.statusRefraction else 'OFF')
        else:
            self.ui.statusRefraction.setText('-')

        # check tracking speed
        if self.app.mount.sett.checkRateLunar():
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', 'true')
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', 'false')
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', 'false')
        elif self.app.mount.sett.checkRateSidereal():
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', 'false')
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', 'true')
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', 'false')
        elif self.app.mount.sett.checkRateSolar():
            self.changeStyleDynamic(self.ui.setLunarTracking, 'running', 'false')
            self.changeStyleDynamic(self.ui.setSiderealTracking, 'running', 'false')
            self.changeStyleDynamic(self.ui.setSolarTracking, 'running', 'true')

        return True

    def updateLocGUI(self):
        """
        updateLocGUI update the gui upon events triggered be the reception of new
        settings from the mount. the mount data is polled, so we use this signal as well
        for the update process.

        :return:    True if ok for testing
        """

        obs = self.app.mount.obsSite

        if obs.location is not None:
            self.ui.siteLongitude.setText(obs.location.longitude.dstr())
            self.ui.siteLatitude.setText(obs.location.latitude.dstr())
            self.ui.siteElevation.setText(str(obs.location.elevation.m))
        else:
            self.ui.siteLongitude.setText('-')
            self.ui.siteLatitude.setText('-')
            self.ui.siteElevation.setText('-')

        return True

    def setMeridianLimitTrack(self):
        """
        setMeridianLimitTrack implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        sett = self.app.mount.sett
        msg = PyQt5.QtWidgets.QMessageBox
        obs = self.app.mount.obsSite
        actValue = sett.meridianLimitTrack
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Meridian Limit Track',
                               'Value (-20-20):',
                               actValue,
                               -20,
                               20,
                               1,
                               )
        if ok:
            if obs.setMeridianLimitTrack(value):
                self.app.message.emit('Meridian Limit Track: [{0}]'.format(value), 0)
                return True
            else:
                self.app.message.emit('Meridian Limit Track cannot be set', 2)
                return False
        else:
            return False

    def setMeridianLimitSlew(self):
        """
        setMeridianLimitSlew implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        sett = self.app.mount.sett
        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        actValue = sett.meridianLimitSlew
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Meridian Limit Slew',
                               'Value (-20-20):',
                               actValue,
                               -20,
                               20,
                               1,
                               )
        if ok:
            if obs.setMeridianLimitSlew(value):
                self.app.message.emit('Meridian Limit Slew: [{0}]'.format(value), 0)
                return True
            else:
                self.app.message.emit('Meridian Limit Slew cannot be set', 2)
                return False
        else:
            return False

    def setHorizonLimitHigh(self):
        """
        setHorizonLimitHigh implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        sett = self.app.mount.sett
        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        actValue = sett.horizonLimitHigh
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Horizon Limit High',
                               'Value (0-90):',
                               actValue,
                               0,
                               90,
                               1,
                               )
        if ok:
            if obs.setHorizonLimitHigh(value):
                self.app.message.emit('Horizon Limit High: [{0}]'.format(value), 0)
                return True
            else:
                self.app.message.emit('Horizon Limit High cannot be set', 2)
                return False
        else:
            return False

    def setHorizonLimitLow(self):
        """
        setHorizonLimitLow implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        sett = self.app.mount.sett
        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        actValue = sett.horizonLimitLow
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Horizon Limit Low',
                               'Value (0-90):',
                               actValue,
                               0,
                               90,
                               1,
                               )
        if ok:
            if obs.setHorizonLimitLow(value):
                self.app.message.emit('Horizon Limit Low: [{0}]'.format(value), 0)
                return True
            else:
                self.app.message.emit('Horizon Limit Low cannot be set', 2)
                return False
        else:
            return False

    def setSlewRate(self):
        """
        setSlewRate implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """
        sett = self.app.mount.sett
        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        actValue = sett.slewRate
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set Slew Rate',
                               'Value (1-20):',
                               actValue,
                               1,
                               20,
                               1,
                               )
        if ok:
            if obs.setSlewRate(value):
                self.app.message.emit('Slew Rate: [{0}]'.format(value), 0)
                return True
            else:
                self.app.message.emit('Slew Rate cannot be set', 2)
                return False
        else:
            return False

    def setLongitude(self):
        """
        setSiteLongitude implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        if obs.location is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getText(self,
                                'Set Site Longitude',
                                'Value: (East positive)',
                                PyQt5.QtWidgets.QLineEdit.Normal,
                                obs.location.longitude.dstr(),
                                )
        if ok:
            if obs.setLongitude(value):
                self.app.message.emit('Longitude: [{0}]'.format(value), 0)
                self.app.mount.getLocation()
                return True
            else:
                self.app.message.emit('Longitude cannot be set', 2)
                return False
        else:
            return False

    def setLatitude(self):
        """
        setSiteLatitude implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        if obs.location is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getText(self,
                                'Set Site Latitude',
                                'Value:',
                                PyQt5.QtWidgets.QLineEdit.Normal,
                                obs.location.latitude.dstr(),
                                )
        if ok:
            if obs.setLatitude(value):
                self.app.message.emit('Latitude: [{0}]'.format(value), 0)
                self.app.mount.getLocation()
                return True
            else:
                self.app.message.emit('Latitude cannot be set', 2)
                return False
        else:
            return False

    def setElevation(self):
        """
        setSiteElevation implements a modal dialog for entering the value

        :return:    success as bool if value could be changed
        """

        obs = self.app.mount.obsSite
        msg = PyQt5.QtWidgets.QMessageBox
        if obs.location is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when Mount not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getDouble(self,
                                  'Set Site Elevation',
                                  'Value: (meters)',
                                  obs.location.elevation.m,
                                  0,
                                  8000,
                                  1,
                                  )
        if ok:
            if obs.setElevation(value):
                self.app.message.emit('Elevation: [{0}]'.format(value), 0)
                self.app.mount.getLocation()
                return True
            else:
                self.app.message.emit('Elevation cannot be set', 2)
        else:
            return False

    def newEnvironDevice(self, deviceName):
        self.app.message.emit('INDI device [{0}] found'.format(deviceName), 0)

    def removeEnvironDevice(self, deviceName):
        """
        removeEnvironDevice clears the gui data and calls deviceEnvironment to update
        the status of the device itself.

        :param deviceName:
        :return: nothing
        """

        envDev = self.app.environment.wDevice
        if deviceName == envDev['sqm']['name']:
            self.ui.SQR.setText('-')
        if deviceName == envDev['local']['name']:
            self.ui.localTemp.setText('-')
            self.ui.localPress.setText('-')
            self.ui.localDewPoint.setText('-')
            self.ui.localHumidity.setText('-')
        if deviceName == envDev['global']['name']:
            self.ui.globalTemp.setText('-')
            self.ui.globalPress.setText('-')
            self.ui.globalDewPoint.setText('-')
            self.ui.globalHumidity.setText('-')
            self.ui.cloudCover.setText('-')
            self.ui.windSpeed.setText('-')
            self.ui.rainVol.setText('-')
            self.ui.snowVol.setText('-')

        self.deviceEnvironDisconnected(deviceName)
        self.app.message.emit('INDI device [{0}] removed'.format(deviceName), 0)
        return True

    def indiEnvironConnected(self):
        self.app.message.emit('INDI server environment connected', 0)

    def indiEnvironDisconnected(self):
        self.app.message.emit('INDI server environment disconnected', 0)

    def updateEnvironGUI(self, deviceName):
        """
        updateEnvironGUI shows the data which is received through INDI client

        :return:    True if ok for testing
        """

        envDev = self.app.environment.wDevice

        if deviceName == envDev['sqm']['name']:
            value = envDev['sqm']['data']['SKY_BRIGHTNESS']
            self.ui.SQR.setText('{0:5.2f}'.format(value))

        if deviceName == envDev['local']['name']:
            value = envDev['local']['data'].get('WEATHER_TEMPERATURE', 0)
            self.ui.localTemp.setText('{0:4.1f}'.format(value))
            value = envDev['local']['data'].get('WEATHER_BAROMETER', 0)
            self.ui.localPress.setText('{0:5.1f}'.format(value))
            value = envDev['local']['data'].get('WEATHER_DEWPOINT', 0)
            self.ui.localDewPoint.setText('{0:4.1f}'.format(value))
            value = envDev['local']['data'].get('WEATHER_HUMIDITY', 0)
            self.ui.localHumidity.setText('{0:3.0f}'.format(value))

        if deviceName == envDev['global']['name']:
            value = envDev['global']['data'].get('WEATHER_TEMPERATURE', 0)
            self.ui.globalTemp.setText('{0:4.1f}'.format(value))
            value = envDev['global']['data'].get('WEATHER_PRESSURE', 0)
            self.ui.globalPress.setText('{0:5.1f}'.format(value))
            value = envDev['global']['data'].get('WEATHER_DEWPOINT', 0)
            self.ui.globalDewPoint.setText('{0:4.1f}'.format(value))
            value = envDev['global']['data'].get('WEATHER_HUMIDITY', 0)
            self.ui.globalHumidity.setText('{0:4.1f}'.format(value))
            value = envDev['global']['data'].get('WEATHER_CLOUD_COVER', 0)
            self.ui.cloudCover.setText('{0:3.0f}'.format(value))
            value = envDev['global']['data'].get('WEATHER_WIND_SPEED', 0)
            self.ui.windSpeed.setText('{0:3.0f}'.format(value))
            value = envDev['global']['data'].get('WEATHER_RAIN_HOUR', 0)
            self.ui.rainVol.setText('{0:3.0f}'.format(value))
            value = envDev['global']['data'].get('WEATHER_SNOW_HOUR', 0)
            self.ui.snowVol.setText('{0:3.0f}'.format(value))

            # setting forecast (only for open weather map)
            if deviceName != 'OpenWeatherMap':
                return
            forecast = int(envDev['global']['data'].get('WEATHER_FORECAST', 3))
            self.changeStyleDynamic(self.ui.weatherForecast,
                                    'color',
                                    self.TRAFFICLIGHTCOLORS[forecast],
                                    )
            forecastID = int(envDev['global']['data'].get('WEATHER_CODE', 0))
            text = self.app.environment.WEATHER_ID[forecastID][0]
            iconID = self.app.environment.WEATHER_ID[forecastID][1]
            iconRef = ':/' + iconID + '.png'
            icon = PyQt5.QtGui.QPixmap(iconRef)
            icon = icon.scaled(25, 25, PyQt5.QtCore.Qt.KeepAspectRatio)
            self.ui.weatherForecastIcon.setPixmap(icon)
            self.ui.weatherForecast.setText(text)

    @staticmethod
    def updateEnvironMainStat(uiList):
        """
        updateEnvironMainStat collects the dynamic properties of all environ widgets
        if mor than one is green -> color from red to yellow. if all are green -> result
        will be green

        :param uiList:
        :return: status according TRAFFIC LIGHTS
        """

        countR = 0
        countSum = 0
        for ui in uiList:
            color = ui.property('color')
            if color is None:
                continue
            if color == 'red':
                countR += 1
            countSum += 1
        if countSum == 0:
            status = 3
        elif countR == 0:
            status = 0
        elif countR == countSum:
            status = 2
        else:
            status = 1
        return status

    def _getStatusList(self):
        """
        _getStatusList defines device names list and corresponding ui widgets

        :return: list devices name, list of widgets
        """

        names = [self.app.environment.wDevice['local']['name'],
                 self.app.environment.wDevice['global']['name'],
                 self.app.environment.wDevice['sqm']['name'],
                 ]
        uiList = [self.ui.localWeatherName,
                  self.ui.globalWeatherName,
                  self.ui.sqmName,
                  ]
        return names, uiList

    def deviceEnvironConnected(self, deviceName):
        """
        deviceEnvironConnected is called whenever a device is connected and used for setting
        the device status right

        :param deviceName: name of device connected
        :return:
        """

        names, uiList = self._getStatusList()
        for name, ui in zip(names, uiList):
            if deviceName != name:
                continue
            self.changeStyleDynamic(ui, 'color', 'green')
        status = self.updateEnvironMainStat(uiList)
        ui = self.ui.environmentConnected
        self.changeStyleDynamic(ui, 'color', self.TRAFFICLIGHTCOLORS[status])

    def deviceEnvironDisconnected(self, deviceName):
        """
        deviceEnvironDisconnected is called whenever a device is disconnected and used for
        setting the device status right

        :param deviceName: name of device disconnected
        :return:
        """

        names, uiList = self._getStatusList()
        for name, ui in zip(names, uiList):
            if deviceName != name:
                continue
            self.changeStyleDynamic(ui, 'color', 'red')
        status = self.updateEnvironMainStat(uiList)
        ui = self.ui.environmentConnected
        self.changeStyleDynamic(ui, 'color', self.TRAFFICLIGHTCOLORS[status])
