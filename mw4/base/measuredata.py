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
import logging
# external packages
import PyQt5
import numpy as np
# local imports


class MeasureData(object):
    """
    the class MeasureData inherits all information and handling of data management and
    storage

        >>> measure = MeasureData(
        >>>                 )
    """

    __all__ = ['MeasureData',
               'startMeasurement',
               'stopMeasurement',
               ]

    version = '0.100.0'
    logger = logging.getLogger(__name__)

    # update rate to 1 seconds for setting indi server
    CYCLE_UPDATE_TASK = 1000
    # maximum size of measurement task
    MAXSIZE = 24 * 60 * 60

    def __init__(self,
                 app,
                 ):
        self.app = app
        self.mutexMeasure = PyQt5.QtCore.QMutex()
        self.shorteningStart = True
        self.raRef = None
        self.decRef = None
        self.data = {
            'time': np.empty(shape=[0, 1], dtype='datetime64'),
            'sensorWeatherTemp': np.empty(shape=[0, 1]),
            'sensorWeatherHum': np.empty(shape=[0, 1]),
            'sensorWeatherPress': np.empty(shape=[0, 1]),
            'sensorWeatherDew': np.empty(shape=[0, 1]),
            'onlineWeatherTemp': np.empty(shape=[0, 1]),
            'onlineWeatherHum': np.empty(shape=[0, 1]),
            'onlineWeatherPress': np.empty(shape=[0, 1]),
            'onlineWeatherDew': np.empty(shape=[0, 1]),
            'directWeatherTemp': np.empty(shape=[0, 1]),
            'directWeatherHum': np.empty(shape=[0, 1]),
            'directWeatherPress': np.empty(shape=[0, 1]),
            'directWeatherDew': np.empty(shape=[0, 1]),
            'skyTemp': np.empty(shape=[0, 1]),
            'skySQR': np.empty(shape=[0, 1]),
            'raJNow': np.empty(shape=[0, 1]),
            'decJNow': np.empty(shape=[0, 1]),
            'status': np.empty(shape=[0, 1]),
            'powCurr1': np.empty(shape=[0, 1]),
            'powCurr2': np.empty(shape=[0, 1]),
            'powCurr3': np.empty(shape=[0, 1]),
            'powCurr4': np.empty(shape=[0, 1]),
            'powVolt': np.empty(shape=[0, 1]),
            'powCurr': np.empty(shape=[0, 1]),
            'powHum': np.empty(shape=[0, 1]),
            'powTemp': np.empty(shape=[0, 1]),
            'powDew': np.empty(shape=[0, 1]),
        }

        self.timerTask = PyQt5.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.measureTask)

    def startMeasurement(self):
        self.timerTask.start(self.CYCLE_UPDATE_TASK)

    def stopMeasurement(self):
        self.timerTask.stop()

    def calculateReference(self):
        """
        calculateReference run the states to get the calculation with references for
        RaDec deviations better stable. it takes into account, when the mount is tracking
        and when we calculate the offset (ref) to make the deviations balanced to zero

        :return: raJNow, decJNow
        """

        dat = self.data
        obs = self.app.mount.obsSite

        raJNow = 0
        decJNow = 0
        if obs.raJNow is None:
            return raJNow, decJNow

        length = len(dat['status'])
        period = min(length, 10)
        hasMean = length > 0 and period > 0

        if not hasMean:
            return raJNow, decJNow

        periodData = dat['status'][-period:]
        hasValidData = all(x is not None for x in periodData)

        if hasValidData:
            trackingIsStable = (periodData.mean() == 0)
        else:
            trackingIsStable = False

        if trackingIsStable:
            if self.raRef is None:
                self.raRef = obs.raJNow._degrees
            if self.decRef is None:
                self.decRef = obs.decJNow.degrees
            # we would like to have the difference in arcsec
            raJNow = (obs.raJNow._degrees - self.raRef) * 3600
            decJNow = (obs.decJNow.degrees - self.decRef) * 3600
        else:
            self.raRef = None
            self.decRef = None

        return raJNow, decJNow

    def checkStart(self, lenData):
        """
        checkStart throws the first N measurements away, because they or not valid

        :param lenData:
        :return: True if splitting happens
        """

        if self.shorteningStart and lenData > 2:
            self.shorteningStart = False
            for measure in self.data:
                self.data[measure] = np.delete(self.data[measure], range(0, 2))

    def checkSize(self, lenData):
        """
        checkSize keep tracking of memory usage of the measurement. if the measurement
        get s too much data, it split the history by half and only keeps the latest only
        for work.
        if as well throws the first N measurements away, because they or not valid

        :param lenData:
        :return: True if splitting happens
        """

        if lenData < self.MAXSIZE:
            return False

        for measure in self.data:
            self.data[measure] = np.split(self.data[measure], 2)[1]
        return True

    def measureTask(self):
        """
        measureTask runs all necessary pre processing and collecting task to assemble a
        large dict of lists, where all measurement data is stored. the intention later on
        would be to store and export this data.
        the time object is related to the time held in mount computer and is in utc timezone.

        data sources are:
            environment
            mount pointing position

        :return: success
        """

        if not self.mutexMeasure.tryLock():
            self.logger.info('overrun in measure')
            return False

        lenData = len(self.data['time'])
        self.checkStart(lenData)
        self.checkSize(lenData)

        dat = self.data
        obs = self.app.mount.obsSite

        # gathering the environment data
        sensorWeatherTemp = self.app.sensorWeather.data.get('WEATHER_TEMPERATURE', 0)
        sensorWeatherPress = self.app.sensorWeather.data.get('WEATHER_PRESSURE', 0)
        sensorWeatherDew = self.app.sensorWeather.data.get('WEATHER_DEWPOINT', 0)
        sensorWeatherHum = self.app.sensorWeather.data.get('WEATHER_HUMIDITY', 0)
        onlineWeatherTemp = self.app.onlineWeather.data.get('temperature', 0)
        onlineWeatherPress = self.app.onlineWeather.data.get('pressure', 0)
        onlineWeatherDew = self.app.onlineWeather.data.get('dewPoint', 0)
        onlineWeatherHum = self.app.onlineWeather.data.get('humidity', 0)
        directWeatherTemp = self.app.mount.setting.weatherTemperature
        directWeatherPress = self.app.mount.setting.weatherPressure
        directWeatherDew = self.app.mount.setting.weatherDewPoint
        directWeatherHum = self.app.mount.setting.weatherHumidity
        # gathering sqr values
        skySQR = self.app.skymeter.data.get('SKY_BRIGHTNESS', 0)
        skyTemp = self.app.skymeter.data.get('SKY_TEMPERATURE', 0)
        # gathering mount data
        raJNow, decJNow = self.calculateReference()
        # gathering data from power
        powCurr1 = self.app.power.data.get('POWER_CURRENT_1', 0)
        powCurr2 = self.app.power.data.get('POWER_CURRENT_2', 0)
        powCurr3 = self.app.power.data.get('POWER_CURRENT_3', 0)
        powCurr4 = self.app.power.data.get('POWER_CURRENT_4', 0)
        powVolt = self.app.power.data.get('SENSOR_VOLTAGE', 0)
        powCurr = self.app.power.data.get('SENSOR_CURRENT', 0)
        powTemp = self.app.power.data.get('WEATHER_TEMPERATURE', 0)
        powDew = self.app.power.data.get('WEATHER_DEWPOINT', 0)
        powHum = self.app.power.data.get('WEATHER_HUMIDITY', 0)

        # writing data to dict
        timeStamp = obs.timeJD.utc_datetime().replace(tzinfo=None)
        dat['time'] = np.append(dat['time'], np.datetime64(timeStamp))
        dat['sensorWeatherTemp'] = np.append(dat['sensorWeatherTemp'], sensorWeatherTemp)
        dat['sensorWeatherHum'] = np.append(dat['sensorWeatherHum'], sensorWeatherHum)
        dat['sensorWeatherPress'] = np.append(dat['sensorWeatherPress'], sensorWeatherPress)
        dat['sensorWeatherDew'] = np.append(dat['sensorWeatherDew'], sensorWeatherDew)
        dat['onlineWeatherTemp'] = np.append(dat['onlineWeatherTemp'], onlineWeatherTemp)
        dat['onlineWeatherHum'] = np.append(dat['onlineWeatherHum'], onlineWeatherHum)
        dat['onlineWeatherPress'] = np.append(dat['onlineWeatherPress'], onlineWeatherPress)
        dat['onlineWeatherDew'] = np.append(dat['onlineWeatherDew'], onlineWeatherDew)
        dat['directWeatherTemp'] = np.append(dat['directWeatherTemp'], directWeatherTemp)
        dat['directWeatherHum'] = np.append(dat['directWeatherHum'], directWeatherHum)
        dat['directWeatherPress'] = np.append(dat['directWeatherPress'], directWeatherPress)
        dat['directWeatherDew'] = np.append(dat['directWeatherDew'], directWeatherDew)
        dat['skySQR'] = np.append(dat['skySQR'], skySQR)
        dat['skyTemp'] = np.append(dat['skyTemp'], skyTemp)
        dat['raJNow'] = np.append(dat['raJNow'], raJNow)
        dat['decJNow'] = np.append(dat['decJNow'], decJNow)
        dat['status'] = np.append(dat['status'], obs.status)
        dat['powCurr1'] = np.append(dat['powCurr1'], powCurr1)
        dat['powCurr2'] = np.append(dat['powCurr2'], powCurr2)
        dat['powCurr3'] = np.append(dat['powCurr3'], powCurr3)
        dat['powCurr4'] = np.append(dat['powCurr4'], powCurr4)
        dat['powCurr'] = np.append(dat['powCurr'], powCurr)
        dat['powVolt'] = np.append(dat['powVolt'], powVolt)
        dat['powTemp'] = np.append(dat['powTemp'], powTemp)
        dat['powDew'] = np.append(dat['powDew'], powDew)
        dat['powHum'] = np.append(dat['powHum'], powHum)

        self.mutexMeasure.unlock()
        return True
