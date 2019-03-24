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

    def __init__(self):
        # mount
        self.app.mount.signals.settDone.connect(self.updateSettingGUI)
        self.app.mount.signals.settDone.connect(self.updateLocGUI)
        self.app.mount.signals.fwDone.connect(self.updateFwGui)

        # environment functions
        signals = self.app.environ.client.signals
        signals.newNumber.connect(self.updateEnvironGUI)
        signals.deviceDisconnected.connect(self.clearEnvironGUI)

        # skymeter functions
        signals = self.app.skymeter.client.signals
        signals.newNumber.connect(self.updateSkymeterGUI)
        signals.deviceDisconnected.connect(self.clearSkymeterGUI)

        # weather functions
        signals = self.app.weather.client.signals
        signals.newNumber.connect(self.updateWeatherGUI)
        signals.deviceDisconnected.connect(self.clearWeatherGUI)

        # gui connections
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
        config = self.app.config['mainW']
        self.ui.checkRefracNone.setChecked(config.get('checkRefracNone', False))
        self.ui.checkRefracCont.setChecked(config.get('checkRefracCont', False))
        self.ui.checkRefracNoTrack.setChecked(config.get('checkRefracNoTrack', False))
        return True

    def storeConfig(self):
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

    def clearGUI(self):
        """
        clearGUI rewrites the gui in case of a special event needed for clearing up

        :return: success for test
        """
        self.updateSettingGUI()
        self.updateSetStatGUI()
        self.updateLocGUI()
        self.updateFwGui()
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
            if self.app.mount.obsSite.status == 0:
                return False
        temp, press = self.app.environ.getFilteredRefracParams()
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
        updateSettingGUI update the gui upon events triggered be the reception of new
        settings from the mount. the mount data is polled, so we use this signal as well
        for the update process.

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

        return True

    def updateFwGui(self):
        """
        updateFwGui write all firmware data to the gui.

        :return:    True if ok for testing
        """

        fw = self.app.mount.fw

        if fw.productName is not None:
            self.ui.productName.setText(fw.productName)
        else:
            self.ui.productName.setText('-')

        if fw.numberString is not None:
            self.ui.numberString.setText(fw.numberString)
        else:
            self.ui.numberString.setText('-')

        if fw.fwdate is not None:
            self.ui.fwdate.setText(fw.fwdate)
        else:
            self.ui.fwdate.setText('-')

        if fw.fwtime is not None:
            self.ui.fwtime.setText(fw.fwtime)
        else:
            self.ui.fwtime.setText('-')

        if fw.hwVersion is not None:
            self.ui.hwVersion.setText(fw.hwVersion)
        else:
            self.ui.hwVersion.setText('-')

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

    def clearEnvironGUI(self, deviceName):
        """
        clearEnvironGUI clears the gui data

        :param deviceName:
        :return: true for test purpose
        """

        self.ui.environTemp.setText('-')
        self.ui.environPress.setText('-')
        self.ui.environDewPoint.setText('-')
        self.ui.environHumidity.setText('-')

        return True

    def updateEnvironGUI(self, deviceName):
        """
        updateEnvironGUI shows the data which is received through INDI client

        :return:    True if ok for testing
        """

        value = self.app.environ.data.get('WEATHER_TEMPERATURE', 0)
        self.ui.environTemp.setText('{0:4.1f}'.format(value))
        value = self.app.environ.data.get('WEATHER_PRESSURE', 0)
        self.ui.environPress.setText('{0:5.1f}'.format(value))
        value = self.app.environ.data.get('WEATHER_DEWPOINT', 0)
        self.ui.environDewPoint.setText('{0:4.1f}'.format(value))
        value = self.app.environ.data.get('WEATHER_HUMIDITY', 0)
        self.ui.environHumidity.setText('{0:3.0f}'.format(value))

    def clearSkymeterGUI(self, deviceName):
        """
        clearEnvironGUI clears the gui data

        :param deviceName:
        :return: true for test purpose
        """

        self.ui.skymeterSQR.setText('-')
        self.ui.skymeterTemp.setText('-')

        return True

    def updateSkymeterGUI(self, deviceName):
        """
        updateSkymeterGUI shows the data which is received through INDI client

        :return:    True if ok for testing
        """

        value = self.app.skymeter.data.get('SKY_BRIGHTNESS', 0)
        self.ui.skymeterSQR.setText('{0:4.1f}'.format(value))
        value = self.app.skymeter.data.get('SKY_TEMPERATURE', 0)
        self.ui.skymeterTemp.setText('{0:4.1f}'.format(value))

    def clearWeatherGUI(self, deviceName):
        """
        clearEnvironGUI clears the gui data

        :param deviceName:
        :return: true for test purpose
        """

        self.ui.weatherTemp.setText('-')
        self.ui.weatherPress.setText('-')
        self.ui.weatherDewPoint.setText('-')
        self.ui.weatherHumidity.setText('-')
        self.ui.weatherCloudCover.setText('-')
        self.ui.weatherWindSpeed.setText('-')
        self.ui.weatherRainVol.setText('-')
        self.ui.weatherSnowVol.setText('-')
        return True

    def updateWeatherGUI(self, deviceName):
        """
        updateSkymeterGUI shows the data which is received through INDI client

        :return:    True if ok for testing
        """

        value = self.app.weather.data.get('WEATHER_TEMPERATURE', 0)
        self.ui.weatherTemp.setText('{0:4.1f}'.format(value))
        value = self.app.weather.data.get('WEATHER_PRESSURE', 0)
        self.ui.weatherPress.setText('{0:5.1f}'.format(value))
        value = self.app.weather.data.get('WEATHER_DEWPOINT', 0)
        self.ui.weatherDewPoint.setText('{0:4.1f}'.format(value))
        value = self.app.weather.data.get('WEATHER_HUMIDITY', 0)
        self.ui.weatherHumidity.setText('{0:3.0f}'.format(value))
        value = self.app.weather.data.get('WEATHER_CLOUD_COVER', 0)
        self.ui.weatherCloudCover.setText('{0:3.0f}'.format(value))
        value = self.app.weather.data.get('WEATHER_WIND_SPEED', 0)
        self.ui.weatherWindSpeed.setText('{0:3.0f}'.format(value))
        value = self.app.weather.data.get('WEATHER_RAIN_HOUR', 0)
        self.ui.weatherRainVol.setText('{0:3.0f}'.format(value))
        value = self.app.weather.data.get('WEATHER_SNOW_HOUR', 0)
        self.ui.weatherSnowVol.setText('{0:3.0f}'.format(value))
