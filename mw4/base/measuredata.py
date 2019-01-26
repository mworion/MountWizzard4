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
import logging
# external packages
import PyQt5
import numpy as np
# local imports


class MeasureData(PyQt5.QtCore.QObject):
    """
    the class MeasureData inherits all information and handling of data management and
    storage

        >>> measure = MeasureData(
        >>>                 )
    """

    __all__ = ['MeasureData',
               ]

    version = '0.2'
    logger = logging.getLogger(__name__)

    # update rate to 1 seconds for setting indi server
    CYCLE_UPDATE_TASK = 1000

    def __init__(self,
                 app,
                 ):
        super().__init__()
        self.app = app
        self.raRef = None
        self.decRef = None
        self.data = {
            'time': np.empty(shape=[0, 1], dtype='datetime64'),
            'temp': np.empty(shape=[0, 1]),
            'humidity': np.empty(shape=[0, 1]),
            'press': np.empty(shape=[0, 1]),
            'dewTemp': np.empty(shape=[0, 1]),
            'sqr': np.empty(shape=[0, 1]),
            'raJNow': np.empty(shape=[0, 1]),
            'decJNow': np.empty(shape=[0, 1]),
        }

        self.timerTask = PyQt5.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self._measureTask)
        self.timerTask.start(self.CYCLE_UPDATE_TASK)

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
        if not self.app.mainW.ui.checkMeasurement.isChecked():
            return False
        # gathering the environment data
        obs = self.app.mount.obsSite
        envTemp = self.app.environment.wDevice['local']['data'].get('WEATHER_TEMPERATURE', 0)
        envPress = self.app.environment.wDevice['local']['data'].get('WEATHER_BAROMETER', 0)
        envDew = self.app.environment.wDevice['local']['data'].get('WEATHER_DEWPOINT', 0)
        envHum = self.app.environment.wDevice['local']['data'].get('WEATHER_HUMIDITY', 0)
        envSQR = self.app.environment.wDevice['sqm']['data'].get('SKY_BRIGHTNESS', 0)

        # gathering the mount data. data will only be != 0 if mount is tracking
        if obs.raJNow is not None:
            if obs.status == 0:
                if self.raRef is None:
                    self.raRef = obs.raJNow.hours * 3600
                if self.decRef is None:
                    self.decRef = obs.decJNow.degrees * 3600
                raJNow = obs.raJNow.hours * 3600 - self.raRef
                decJNow = obs.decJNow.degrees * 3600 - self.decRef
            else:
                self.raRef = None
                self.decRef = None
                raJNow = 0
                decJNow = 0
        else:
            raJNow = 0
            decJNow = 0

        # writing data to dict
        dat = self.data
        timeStamp = obs.timeJD.utc_datetime().replace(tzinfo=None)
        dat['time'] = np.append(dat['time'], np.datetime64(timeStamp))
        dat['temp'] = np.append(dat['temp'], envTemp)
        dat['humidity'] = np.append(dat['humidity'], envHum)
        dat['press'] = np.append(dat['press'], envPress)
        dat['dewTemp'] = np.append(dat['dewTemp'], envDew)
        dat['sqr'] = np.append(dat['sqr'], envSQR)
        dat['raJNow'] = np.append(dat['raJNow'], raJNow)
        dat['decJNow'] = np.append(dat['decJNow'], decJNow)

        return True
