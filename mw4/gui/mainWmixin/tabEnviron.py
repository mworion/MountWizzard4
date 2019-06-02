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


class Environ(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        # mount
        self.app.mount.signals.settDone.connect(self.updateSettingGUI)
        self.app.mount.signals.locationDone.connect(self.updateLocGUI)
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
        self.app.update10s.connect(self.updateRefractionParameters)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.checkRefracNone.setChecked(config.get('checkRefracNone', False))
        self.ui.checkRefracCont.setChecked(config.get('checkRefracCont', False))
        self.ui.checkRefracNoTrack.setChecked(config.get('checkRefracNoTrack', False))
        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
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
