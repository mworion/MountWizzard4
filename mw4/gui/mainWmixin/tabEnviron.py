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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets
import requests
import numpy as np
import qimage2ndarray

# local import
from base.tpool import Worker


class Environ(object):
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

        # environment functions
        signals = self.app.sensorWeather.signals
        signals.deviceDisconnected.connect(self.clearSensorWeatherGui)

        # skymeter functions
        signals = self.app.skymeter.signals
        signals.deviceDisconnected.connect(self.clearSkymeterGui)

        # power weather functions
        signals = self.app.powerWeather.signals
        signals.deviceDisconnected.connect(self.clearPowerWeatherGui)

        # weather functions
        self.app.onlineWeather.signals.dataReceived.connect(self.updateOnlineWeatherGui)

        # weather functions
        self.app.mount.signals.settingDone.connect(self.updateDirectWeatherGui)
        self.app.mount.signals.settingDone.connect(self.updateRefractionUpdateType)

        # gui connections
        self.ui.setRefractionManual.clicked.connect(self.updateRefractionParameters)
        self.ui.isOnline.stateChanged.connect(self.updateClearOutside)
        self.ui.onlineWeatherGroup.clicked.connect(self.selectRefractionSource)
        self.ui.sensorWeatherGroup.clicked.connect(self.selectRefractionSource)
        self.ui.directWeatherGroup.clicked.connect(self.selectRefractionSource)
        self.ui.checkRefracNone.clicked.connect(self.setRefractionUpdateType)
        self.ui.checkRefracCont.clicked.connect(self.setRefractionUpdateType)
        self.ui.checkRefracNoTrack.clicked.connect(self.setRefractionUpdateType)

        # cyclic functions
        self.app.update1s.connect(self.updateFilterRefractionParameters)
        self.app.update1s.connect(self.updateRefractionParameters)
        self.app.update1s.connect(self.updateSkymeterGui)
        self.app.update1s.connect(self.updatePowerWeatherGui)
        self.app.update1s.connect(self.updateSensorWeatherGui)
        self.app.update30m.connect(self.updateClearOutside)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.checkRefracNone.setChecked(config.get('checkRefracNone', False))
        self.ui.checkRefracCont.setChecked(config.get('checkRefracCont', False))
        self.ui.checkRefracNoTrack.setChecked(config.get('checkRefracNoTrack', False))

        self.refractionSource = config.get('refractionSource', '')
        self.setRefractionSourceGui()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['checkRefracNone'] = self.ui.checkRefracNone.isChecked()
        config['checkRefracCont'] = self.ui.checkRefracCont.isChecked()
        config['checkRefracNoTrack'] = self.ui.checkRefracNoTrack.isChecked()
        config['refractionSource'] = self.refractionSource
        return True

    def updateRefractionUpdateType(self, setting):
        """
        :param setting:
        :return: success
        """
        if self.refractionSource != 'directWeather':
            return False

        if setting.weatherStatus == 0:
            self.ui.checkRefracNone.setChecked(True)
        elif setting.weatherStatus == 1:
            self.ui.checkRefracNoTrack.setChecked(True)
        elif setting.weatherStatus == 2:
            self.ui.checkRefracCont.setChecked(True)
        else:
            return False

        return True

    def setRefractionUpdateType(self):
        """
        :return: success
        """
        if self.refractionSource != 'directWeather':
            suc = self.app.mount.setting.setDirectWeatherUpdateType(0)
            return suc

        # otherwise we have to switch it on or off
        if self.ui.checkRefracNone.isChecked():
            suc = self.app.mount.setting.setDirectWeatherUpdateType(0)
        elif self.ui.checkRefracNoTrack.isChecked():
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
        which of the groups was clicked on. whit that information is detects the
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
        if self.refractionSource == 'onlineWeather':
            if not self.app.onlineWeather.data:
                return False
            temp = self.app.onlineWeather.data['temperature']
            press = self.app.onlineWeather.data['pressure']

        elif self.refractionSource == 'sensorWeather':
            key = 'WEATHER_PARAMETERS.WEATHER_TEMPERATURE'
            temp = self.app.sensorWeather.data.get(key, None)
            key = 'WEATHER_PARAMETERS.WEATHER_PRESSURE'
            press = self.app.sensorWeather.data.get(key, None)

        else:
            temp = None
            press = None

        if temp is None or press is None:
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

        if self.sender() != self.ui.setRefractionManual:
            if self.ui.checkRefracNone.isChecked():
                return False

            if self.ui.checkRefracNoTrack.isChecked():
                if self.app.mount.obsSite.status == 0:
                    return False

        suc = self.app.mount.setting.setRefractionParam(temperature=temp,
                                                        pressure=press)

        if not suc:
            self.app.message.emit('Cannot perform refraction update', 2)
            return False

        return True

    def clearSensorWeatherGui(self, deviceName):
        """
        :param deviceName:
        :return: true for test purpose
        """
        self.ui.sensorWeatherTemp.setText('-')
        self.ui.sensorWeatherPress.setText('-')
        self.ui.sensorWeatherDewPoint.setText('-')
        self.ui.sensorWeatherHumidity.setText('-')
        self.ui.sensorWeatherCloudCover.setText('-')
        self.ui.sensorWeatherRainVol.setText('-')
        self.ui.sensorWeatherWindSpeed.setText('-')
        self.ui.sensorWeatherWindDir.setText('-')
        self.ui.sensorWeatherSQR.setText('-')
        return True

    def updateSensorWeatherGui(self):
        """
        :return:    True if ok for testing
        """
        value = self.app.sensorWeather.data.get(
            'WEATHER_PARAMETERS.WEATHER_TEMPERATURE', None)
        self.guiSetText(self.ui.sensorWeatherTemp, '4.1f', value)

        value = self.app.sensorWeather.data.get(
            'WEATHER_PARAMETERS.WEATHER_PRESSURE', None)
        self.guiSetText(self.ui.sensorWeatherPress, '4.1f', value)

        value = self.app.sensorWeather.data.get(
            'WEATHER_PARAMETERS.WEATHER_DEWPOINT', None)
        self.guiSetText(self.ui.sensorWeatherDewPoint, '4.1f', value)

        value = self.app.sensorWeather.data.get(
            'WEATHER_PARAMETERS.WEATHER_HUMIDITY', None)
        self.guiSetText(self.ui.sensorWeatherHumidity, '3.0f', value)

        value = self.app.sensorWeather.data.get('cloudCover', None)
        self.guiSetText(self.ui.sensorWeatherCloudCover, '3.0f', value)

        value = self.app.sensorWeather.data.get('rain', None)
        self.guiSetText(self.ui.sensorWeatherRainVol, '5.2f', value)

        value = self.app.sensorWeather.data.get('windDir', None)
        self.guiSetText(self.ui.sensorWeatherWindDir, '3.0f', value)

        value = self.app.sensorWeather.data.get('windSpeed', None)
        self.guiSetText(self.ui.sensorWeatherWindSpeed, '3.0f', value)

        value = self.app.sensorWeather.data.get('SKY_QUALITY.SKY_BRIGHTNESS', None)
        self.guiSetText(self.ui.sensorWeatherSQR, '4.2f', value)
        return True

    def clearSkymeterGui(self, deviceName=''):
        """
        :param deviceName:
        :return: true for test purpose
        """
        self.ui.skymeterSQR.setText('-')
        self.ui.skymeterTemp.setText('-')
        return True

    def updateSkymeterGui(self):
        """
        :return:    True if ok for testing
        """
        value = self.app.skymeter.data.get('SKY_QUALITY.SKY_BRIGHTNESS', 0)
        self.guiSetText(self.ui.skymeterSQR, '5.2f', value)

        value = self.app.skymeter.data.get('SKY_QUALITY.SKY_TEMPERATURE', 0)
        self.guiSetText(self.ui.skymeterTemp, '4.1f', value)
        return True

    def clearPowerWeatherGui(self):
        """
        clearPowerWeatherGui changes the state of the Pegasus values to '-'

        :return: success for test
        """

        self.ui.powerTemp.setText('-')
        self.ui.powerHumidity.setText('-')
        self.ui.powerDewPoint.setText('-')

        return True

    def updatePowerWeatherGui(self):
        """
        updatePowerGui changes the style of the button related to the state of
        the Pegasus UPB device

        :return: success for test
        """

        value = self.app.powerWeather.data.get('WEATHER_PARAMETERS.WEATHER_TEMPERATURE', 0)
        self.guiSetText(self.ui.powerTemp, '4.1f', value)

        value = self.app.powerWeather.data.get('WEATHER_PARAMETERS.WEATHER_HUMIDITY', 0)
        self.guiSetText(self.ui.powerHumidity, '3.0f', value)

        value = self.app.powerWeather.data.get('WEATHER_PARAMETERS.WEATHER_DEWPOINT', 0)
        self.guiSetText(self.ui.powerDewPoint, '4.1f', value)

        return True

    def getWebDataWorker(self, url=''):
        """
        :param url:
        :return: data
        """
        if not url:
            return None

        try:
            data = requests.get(url, timeout=30)

        except Exception as e:
            self.log.critical(f'{url} general exception: {e}')
            return None

        if data.status_code != 200:
            self.log.warning(f'{url}: status nok')
            return None

        self.log.trace(f'{url}: {data.status_code}')
        return data

    @staticmethod
    def processClearOutsideImage(image=None):
        """
        processClearOutsideImage takes the image, split it and puts the image
        to the Gui. for the transformation qimage2ndarray is used because of
        the speed for the calculations. dim is a factor which reduces the
        lightness of the overall image

        :param image:
        :return: success
        """
        dim = 0.85
        image.convertToFormat(PyQt5.QtGui.QImage.Format_RGB32)
        imageBase = image.copy(0, 84, 624, 141)

        # transformation are done in numpy, because it's much faster
        width = imageBase.width()
        height = imageBase.height()
        imgArr = qimage2ndarray.rgb_view(imageBase)
        imgArr = imgArr.reshape(width * height, 3)
        img_Max = np.maximum(255 - imgArr, [32, 32, 32])
        temp = imgArr[:, 0] == imgArr[:, 1]
        check = np.array([temp, temp, temp]).transpose()

        # do the transform light to dark theme
        imgArr = np.where(check, img_Max, imgArr)

        # transforming back
        imgArr = imgArr.reshape(height, width, 3)

        # Compressing the image as the widget content is a png
        # removing some rows
        m = np.isin(imgArr, [[32, 32, 32], [255, 0, 0]])
        toDelete = []
        maxRow = 1
        line = maxRow
        for i in range(0, len(m[:, 1])):
            if not line and m[i, :].all() and i > 15:
                toDelete.append(i)
            elif line:
                line -= 1
            elif not m[i][:].all():
                line = maxRow
        imgArr = np.delete(imgArr, toDelete, axis=0)

        # re transfer to QImage from numpy array
        imageBase = qimage2ndarray.array2qimage(dim * imgArr)
        pixmapBase = PyQt5.QtGui.QPixmap().fromImage(imageBase)

        return pixmapBase

    def updateClearOutsideImage(self, data=None):
        """
        updateClearOutsideImage takes the returned data from a web fetch and
        makes an image out of it

        :param data:
        :return: success
        """
        if data is None:
            return False

        image = PyQt5.QtGui.QImage()
        if not hasattr(data, 'content'):
            return False
        if not isinstance(data.content, bytes):
            return False

        image.loadFromData(data.content)
        pixmapBase = self.processClearOutsideImage(image=image)
        self.ui.picClearOutside.setPixmap(pixmapBase)
        return True

    def getClearOutside(self, url=''):
        """
        getClearOutside initiates the worker thread to get the web data fetched

        :param url:
        :return:
        """
        worker = Worker(self.getWebDataWorker, url)
        worker.signals.result.connect(self.updateClearOutsideImage)
        self.threadPool.start(worker)

    def updateClearOutside(self):
        """
        updateClearOutside downloads the actual clear outside image and displays
        it in environment tab. it checks first if online is set, otherwise not
        download will take place. it will be updated every 30 minutes.

        confirmation for using the service :

        Grant replied Aug 5, 10:01am
        Hi Michael,
        No problem at all embedding the forecast as shown in your image :-)
        We appreciate the support.
        Kindest Regards,
        Grant

        :return: success
        """
        if not self.ui.isOnline.isChecked():
            pixmap = PyQt5.QtGui.QPixmap(':/pics/offlineMode.png')
            self.ui.picClearOutside.setPixmap(pixmap)
            return False

        # prepare coordinates for website
        loc = self.app.mount.obsSite.location
        lat = loc.latitude.degrees
        lon = loc.longitude.degrees

        webSite = 'http://clearoutside.com/forecast_image_medium/'
        url = f'{webSite}{lat:4.2f}/{lon:4.2f}/forecast.png'
        self.getClearOutside(url=url)
        return True

    def clearOnlineWeatherGui(self):
        """
        :return: true for test purpose
        """
        self.ui.onlineWeatherTemp.setText('-')
        self.ui.onlineWeatherPress.setText('-')
        self.ui.onlineWeatherHumidity.setText('-')
        self.ui.onlineWeatherDewPoint.setText('-')
        self.ui.onlineWeatherCloudCover.setText('-')
        self.ui.onlineWeatherWindSpeed.setText('-')
        self.ui.onlineWeatherWindDir.setText('-')
        self.ui.onlineWeatherRainVol.setText('-')
        return True

    def updateOnlineWeatherGui(self, data=None):
        """
        :return: success
        """
        if not data:
            self.clearOnlineWeatherGui()
            return False

        value = self.app.onlineWeather.data.get('temperature', None)
        self.guiSetText(self.ui.onlineWeatherTemp, '4.1f', value)

        value = self.app.onlineWeather.data.get('pressure', None)
        self.guiSetText(self.ui.onlineWeatherPress, '5.1f', value)

        value = self.app.onlineWeather.data.get('humidity', None)
        self.guiSetText(self.ui.onlineWeatherHumidity, '3.0f', value)

        value = self.app.onlineWeather.data.get('dewPoint', None)
        self.guiSetText(self.ui.onlineWeatherDewPoint, '4.1f', value)

        value = self.app.onlineWeather.data.get('cloudCover', None)
        self.guiSetText(self.ui.onlineWeatherCloudCover, '3.0f', value)

        value = self.app.onlineWeather.data.get('windSpeed', None)
        self.guiSetText(self.ui.onlineWeatherWindSpeed, '3.0f', value)

        value = self.app.onlineWeather.data.get('windDir', None)
        self.guiSetText(self.ui.onlineWeatherWindDir, '3.0f', value)

        value = self.app.onlineWeather.data.get('rain', None)
        self.guiSetText(self.ui.onlineWeatherRainVol, '5.2f', value)
        return True

    def clearDirectWeatherGui(self):
        """
        updateOnlineWeatherGui takes the returned data from the dict to the Gui

        :return: true for test purpose
        """
        self.ui.directWeatherTemp.setText('-')
        self.ui.directWeatherPress.setText('-')
        self.ui.directWeatherHumidity.setText('-')
        self.ui.directWeatherDewPoint.setText('-')
        return True

    def updateDirectWeatherGui(self, setting=None):
        """
        :param setting:
        :return: success
        """
        if not self.deviceStat['directWeather']:
            self.clearDirectWeatherGui()
            return False

        if setting is None:
            return False

        value = setting.weatherTemperature
        self.guiSetText(self.ui.directWeatherTemp, '4.1f', value)

        value = setting.weatherPressure
        self.guiSetText(self.ui.directWeatherPress, '5.1f', value)

        value = setting.weatherHumidity
        self.guiSetText(self.ui.directWeatherHumidity, '3.0f', value)

        value = setting.weatherDewPoint
        self.guiSetText(self.ui.directWeatherDewPoint, '4.1f', value)
        return True
