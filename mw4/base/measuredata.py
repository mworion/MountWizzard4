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
# Python  v3.7.3
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

    version = '0.4'
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
            'envTemp': np.empty(shape=[0, 1]),
            'envHum': np.empty(shape=[0, 1]),
            'envPress': np.empty(shape=[0, 1]),
            'envDew': np.empty(shape=[0, 1]),
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
        self.timerTask.timeout.connect(self._measureTask)

    def startMeasurement(self):
        self.timerTask.start(self.CYCLE_UPDATE_TASK)

    def stopMeasurement(self):
        self.timerTask.stop()

    def _calculateReference(self):
        """
        _calculateReference run the states to get the calculation with references for
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
                self.raRef = obs.raJNow.hours * 3600
            if self.decRef is None:
                self.decRef = obs.decJNow.degrees * 3600
            raJNow = obs.raJNow.hours * 3600 - self.raRef
            decJNow = obs.decJNow.degrees * 3600 - self.decRef
        else:
            self.raRef = None
            self.decRef = None

        return raJNow, decJNow

    def _checkSize(self):
        """
        _reduceSize keep tracking of memory usage of the measurement. if the measurement
        get s too much data, it split the history by half and only keeps the latest only
        for work.
        if as well throws the first N measurements away, because they or not valid

        :return: True if splitting happens
        """

        lenData = len(self.data['time'])
        if self.shorteningStart and lenData > 2:
            self.shorteningStart = False
            for measure in self.data:
                self.data[measure] = np.delete(self.data[measure], range(0, 2))

        if lenData < self.MAXSIZE:
            return False

        for measure in self.data:
            self.data[measure] = np.split(self.data[measure], 2)[1]
        return True

    def _measureTask(self):
        """
        _measureTask runs all necessary pre processing and collecting task to assemble a
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

        self._checkSize()

        dat = self.data
        obs = self.app.mount.obsSite

        # gathering the environment data
        envTemp = self.app.environ.data.get('WEATHER_TEMPERATURE', 0)
        envPress = self.app.environ.data.get('WEATHER_PRESSURE', 0)
        envDew = self.app.environ.data.get('WEATHER_DEWPOINT', 0)
        envHum = self.app.environ.data.get('WEATHER_HUMIDITY', 0)
        # gathering sqr values
        skySQR = self.app.skymeter.data.get('SKY_BRIGHTNESS', 0)
        skyTemp = self.app.skymeter.data.get('SKY_TEMPERATURE', 0)
        # gathering mount data
        raJNow, decJNow = self._calculateReference()
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
        dat['envTemp'] = np.append(dat['envTemp'], envTemp)
        dat['envHum'] = np.append(dat['envHum'], envHum)
        dat['envPress'] = np.append(dat['envPress'], envPress)
        dat['envDew'] = np.append(dat['envDew'], envDew)
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
