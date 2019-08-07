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
import time
# external packages
import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.uic
import requests
# local import
from mw4.base.tpool import Worker


class Environ(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        # environment functions
        signals = self.app.environ.client.signals
        signals.newNumber.connect(self.updateEnvironGUI)
        signals.deviceDisconnected.connect(self.clearEnvironGUI)

        # skymeter functions
        signals = self.app.skymeter.client.signals
        signals.newNumber.connect(self.updateSkymeterGUI)
        signals.deviceDisconnected.connect(self.clearSkymeterGUI)

        # gui connections
        self.ui.setRefractionManual.clicked.connect(self.updateRefractionParameters)
        self.app.update10s.connect(self.updateRefractionParameters)
        self.app.update10m.connect(self.updateOpenWeatherMap)
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

        self.ui.openWeatherMapKey.setText(config.get('openWeatherMapKey', ''))
        self.updateClearOutside()
        self.updateOpenWeatherMap()

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

        config['openWeatherMapKey'] = self.ui.openWeatherMapKey.text()

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

    def getWebDataWorker(self, url=''):
        """
        getWebDataWorker fetches a given url and does the error handling.

        :param url:
        :return: data
        """

        if not url:
            return None

        try:
            data = requests.get(url, timeout=10)
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

    def updateClearOutsideGui(self, image):
        """
        updateClearOutsideGui takes the returned data from a web fetch and puts the data
        to the Gui

        :param image:
        :return: True for test purpose
        """

        imageBase, imageHeader = image

        if imageBase is None:
            return False
        if imageHeader is None:
            return False

        pixmapBase = PyQt5.QtGui.QPixmap().fromImage(imageBase)
        pixmapHeader = PyQt5.QtGui.QPixmap().fromImage(imageHeader)
        self.ui.picClearOutside.setPixmap(pixmapBase)
        self.ui.picClearOutsideHeader.setPixmap(pixmapHeader)

        return True

    def getClearOutsideWorkerHelper(self, url=''):
        """
        getClearOutsideWorkerHelper replaces the direct call to getWebDataWorker because
        we need to do the data calculation for the image conversion in the separate thread
        as well. the calculation take roughly 1s and that's to much to keep the gui
        responsive

        :param url:
        :return: True for test purpose
        """

        data = self.getWebDataWorker(url=url)
        if not data:
            return None, None

        dim = 0.7
        image = PyQt5.QtGui.QImage()
        image.loadFromData(data.content)
        imageBase = image.copy(0, 84, 622, 141)
        imageHeader = image.copy(550, 1, 130, 80)

        for x in range(0, imageBase.width()):
            for y in range(0, imageBase.height()):
                point = PyQt5.QtCore.QPoint(x, y)
                r, g, b, a = imageBase.pixelColor(point).getRgb()
                if r != g:
                    r = dim * r
                    g = dim * g
                    b = dim * b
                else:
                    r = max(255 - r, 32)
                    g = max(255 - g, 32)
                    b = max(255 - b, 32)
                imageBase.setPixelColor(point,
                                        PyQt5.QtGui.QColor(r, g, b, 255))
        return imageBase, imageHeader

    def getClearOutside(self, url=''):
        """
        getClearOutside initiates the worker thread to get the web data fetched

        :param url:
        :return:
        """
        worker = Worker(self.getClearOutsideWorkerHelper, url)
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

        if self.ui.isOffline.isChecked():
            return False

        # prepare coordinates for website
        loc = self.app.mount.obsSite.location
        lat = loc.latitude.degrees
        lon = loc.longitude.degrees

        webSite = 'http://clearoutside.com/forecast_image_medium/'
        url = f'{webSite}{lat:4.2f}/{lon:4.2f}/forecast.png'
        self.getClearOutside(url=url)

        return True

    def updateOpenWeatherMapGui(self, data):
        """
        updateOpenWeatherMapGui takes the returned data from a web fetch and puts the data
        to the Gui

        :param data:
        :return: True for test purpose
        """

        if data is None:
            return False

        val = data.json()
        val = val['list'][0]

        self.ui.weatherTemp.setText(f'{val["main"]["temp"]-273.15:4.1f}')
        self.ui.weatherPress.setText(f'{val["main"]["grnd_level"]:5.1f}')
        self.ui.weatherHumidity.setText(f'{val["main"]["humidity"]:3.0f}')
        self.ui.weatherCloudCover.setText(f'{val["clouds"]["all"]:3.0f}')
        self.ui.weatherWindSpeed.setText(f'{val["wind"]["speed"]:3.0f}')
        self.ui.weatherWindDir.setText(f'{val["wind"]["deg"]:3.0f}')
        self.ui.weatherRainVol.setText(f'{val["rain"]["3h"]:5.2f}')

        return True

    def getOpenWeatherMap(self, url=''):
        """
        getOpenWeatherMap initiates the worker thread to get the web data fetched

        :param url:
        :return:
        """
        worker = Worker(self.getWebDataWorker, url)
        worker.signals.result.connect(self.updateOpenWeatherMapGui)
        self.threadPool.start(worker)

    def updateOpenWeatherMap(self):
        """
        updateOpenWeatherMap downloads the actual OpenWeatherMap image and displays it in
        environment tab. it checks first if online is set, otherwise not download will take
        place. it will be updated every 10 minutes.

        :return: success
        """

        if self.ui.isOffline.isChecked():
            return False
        if not self.ui.openWeatherMapKey.text():
            return False

        # prepare coordinates for website
        loc = self.app.mount.obsSite.location
        lat = loc.latitude.degrees
        lon = loc.longitude.degrees
        apiKey = self.ui.openWeatherMapKey.text()

        webSite = 'http://api.openweathermap.org/data/2.5/forecast'
        url = f'{webSite}?lat={lat:1.0f}&lon={lon:1.0f}&APPID={apiKey}'
        self.getOpenWeatherMap(url=url)

        return True
