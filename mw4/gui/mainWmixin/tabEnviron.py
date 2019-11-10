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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.uic
import requests
import numpy as np
import qimage2ndarray
# local import
from mw4.base.tpool import Worker


class EnvironGui(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):

        self.filteredTemperature = None
        self.filteredPressure = None
        self.refractionSources = {'weather': self.ui.weatherGroup,
                                  'environ': self.ui.environGroup,
                                  'internalSensor': self.ui.internalGroup,
                                  }
        self.refractionSource = ''

        # environment functions
        signals = self.app.environ.client.signals
        signals.newNumber.connect(self.updateEnvironGUI)
        signals.deviceDisconnected.connect(self.clearEnvironGUI)

        # skymeter functions
        signals = self.app.skymeter.client.signals
        signals.newNumber.connect(self.updateSkymeterGUI)
        signals.deviceDisconnected.connect(self.clearSkymeterGUI)

        # weather functions
        self.app.weather.signals.dataReceived.connect(self.updateOpenWeatherMapGui)

        # gui connections
        self.ui.setRefractionManual.clicked.connect(self.updateRefractionParameters)
        self.ui.isOnline.stateChanged.connect(self.updateClearOutside)
        self.ui.weatherGroup.clicked.connect(self.selectRefractionSource)
        self.ui.environGroup.clicked.connect(self.selectRefractionSource)
        self.ui.internalGroup.clicked.connect(self.selectRefractionSource)

        # cyclic functions
        self.app.update1s.connect(self.updateFilterRefractionParameters)
        self.app.update1s.connect(self.updateRefractionParameters)
        self.app.update30m.connect(self.updateClearOutside)

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

        self.refractionSource = config.get('refractionSource', '')
        self.setRefractionSourceGui()
        self.updateClearOutside()
        self.deviceStat['internalSensor'] = None

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
        config['refractionSource'] = self.refractionSource

        return True

    def setRefractionSourceGui(self):
        """
        setRefractionSourceGui sets the gui elements to a recognizable setting and disables
        all others

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
        selectRefractionSource receives all button presses on groups and checks which of the
        groups was clicked on. whit that information is detects the index in the list of
        groups.

        :return: success
        """

        for source, group in self.refractionSources.items():
            if group != self.sender():
                continue
            if group.isChecked():
                self.refractionSource = source
            else:
                self.refractionSource = ''

        self.setRefractionSourceGui()

        return True

    def updateFilterRefractionParameters(self):
        """
        updateFilter initializes the filter with the first values or is rolling the
        moving average

        :return:
        """

        if self.refractionSource == 'weather':
            if not self.app.weather.data:
                return False
            temp = self.app.weather.data['temperature']
            press = self.app.weather.data['pressure']
        elif self.refractionSource == 'environ':
            temp = self.app.environ.data.get('WEATHER_TEMPERATURE', None)
            press = self.app.environ.data.get('WEATHER_PRESSURE', None)
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
        getFilteredRefracParams filters local temperature and pressure with and moving
        average filter over 100 seconds and returns the filtered values.

        :return:  temperature and pressure
        """

        if self.filteredTemperature is not None and self.filteredPressure is not None:
            temp = np.mean(self.filteredTemperature)
            press = np.mean(self.filteredPressure)
            return temp, press
        else:
            return None, None

    def updateRefractionParameters(self):
        """
        updateRefractionParameters takes the actual conditions for update into account and
        does the update of the refraction parameters. this could be done during when mount
        is not in tracking state or continuously

        :return: success if update happened
        """

        temp, press = self.movingAverageRefractionParameters()

        if temp is None or press is None:
            return False

        if not self.app.mount.mountUp:
            return False
        if self.ui.checkRefracNone.isChecked():
            return False
        if self.ui.checkRefracNoTrack.isChecked():
            if self.app.mount.obsSite.status == 0:
                return False

        suc = self.app.mount.setting.setRefractionParam(temperature=temp,
                                                        pressure=press)

        if not suc:
            self.app.message.emit('Cannot perform refraction update', 2)
            self.logger.info(f'No refraction update Temp:{temp}, Press:{press}')
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
        self.ui.skymeterSQR.setText('{0:5.2f}'.format(value))
        value = self.app.skymeter.data.get('SKY_TEMPERATURE', 0)
        self.ui.skymeterTemp.setText('{0:4.1f}'.format(value))

    def getWebDataWorker(self, url=''):
        """
        getWebDataWorker fetches a given url and does the error handling.

        :param url:
        :return: data
        """

        if not url:
            return None

        try:
            data = requests.get(url, timeout=30)
        except TimeoutError:
            self.logger.error(f'{url} not reachable')
            return None
        except Exception as e:
            self.logger.error(f'{url} general exception: {e}')
            return None

        if data.status_code != 200:
            self.logger.error(f'{url}: status nok')
            return None
        self.logger.debug(f'{url}: {data.status_code}')
        return data

    def updateClearOutsideImages(self, image=None):
        """
        updateClearOutsideImages takes the image, split it and puts the image
        to the Gui. for the transformation qimage2ndarray is used because of the speed
        for the calculations. dim is a factor which reduces the lightness of the overall
        image

        :param image:
        :return: success
        """

        if image is None:
            return False

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
        # removing some lines
        m = np.isin(imgArr, [[32, 32, 32], [255, 0, 0]])
        toDelete = []
        maxLine = 1
        line = maxLine
        for i in range(0, len(m[:])):
            if not line and m[i][:].all() and i > 15:
                toDelete.append(i)
            elif line:
                line -= 1
            elif not m[i][:].all():
                line = maxLine
        imgArr = np.delete(imgArr, toDelete, axis=0)
        # re transfer to QImage from numpy array
        imageBase = qimage2ndarray.array2qimage(dim * imgArr)

        pixmapBase = PyQt5.QtGui.QPixmap().fromImage(imageBase)
        self.ui.picClearOutside.setPixmap(pixmapBase)

        return True

    def updateClearOutsideGui(self, data=None):
        """
        updateClearOutsideGui takes the returned data from a web fetch and makes an image
        out of it

        :param data:
        :return: success
        """

        if data is None:
            return False

        image = PyQt5.QtGui.QImage()
        image.loadFromData(data.content)
        suc = self.updateClearOutsideImages(image=image)
        return suc

    def getClearOutside(self, url=''):
        """
        getClearOutside initiates the worker thread to get the web data fetched

        :param url:
        :return:
        """
        worker = Worker(self.getWebDataWorker, url)
        worker.signals.result.connect(self.updateClearOutsideGui)
        self.threadPool.start(worker)

    def updateClearOutside(self):
        """
        updateClearOutside downloads the actual clear outside image and displays it in
        environment tab. it checks first if online is set, otherwise not download will take
        place. it will be updated every 30 minutes.

        confirmation for using the service :

        Grant replied Aug 5, 10:01am
        Hi Michael,
        No problem at all embedding the forecast as shown in your image :-)
        We appreciate the support.
        Kindest Regards,
        Grant

        :return: success
        """

        pixmapHeader = PyQt5.QtGui.QPixmap(':/clearoutside.png')
        self.ui.picClearOutsideHeader.setPixmap(pixmapHeader)

        if not self.ui.isOnline.isChecked():
            pixmap = PyQt5.QtGui.QPixmap(':/clearoutsideoff.png')
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

    def clearOpenWeatherMapGui(self):
        """

        :return: true for test purpose
        """
        self.ui.weatherTemp.setText('-')
        self.ui.weatherPress.setText('-')
        self.ui.weatherHumidity.setText('-')
        self.ui.weatherDewPoint.setText('-')
        self.ui.weatherCloudCover.setText('-')
        self.ui.weatherWindSpeed.setText('-')
        self.ui.weatherWindDir.setText('-')
        self.ui.weatherRainVol.setText('-')

        return True

    def updateOpenWeatherMapGui(self, data):
        """
        updateOpenWeatherMapGui takes the returned data from the dict to the Gui

        :return: True for test purpose
        """

        if not data:
            self.clearOpenWeatherMapGui()
            return False

        if 'temperature' in data:
            self.ui.weatherTemp.setText(f'{data["temperature"]:4.1f}')
        if 'pressure' in data:
            self.ui.weatherPress.setText(f'{data["pressure"]:5.1f}')
        if 'humidity' in data:
            self.ui.weatherHumidity.setText(f'{data["humidity"]:3.0f}')
        if 'dewPoint' in data:
            self.ui.weatherDewPoint.setText(f'{data["dewPoint"]:4.1f}')
        if 'cloudCover' in data:
            self.ui.weatherCloudCover.setText(f'{data["cloudCover"]:3.0f}')
        if 'windSpeed' in data:
            self.ui.weatherWindSpeed.setText(f'{data["windSpeed"]:3.0f}')
        if 'windDir' in data:
            self.ui.weatherWindDir.setText(f'{data["windDir"]:3.0f}')
        if 'rain' in data:
            self.ui.weatherRainVol.setText(f'{data["rain"]:5.2f}')

        return True
