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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import csv

# external packages
import PyQt6

# local imports


class MeasureDataCSV(PyQt6.QtCore.QObject):
    """
    the class MeasureDataCSV inherits all information and handling of data management and
    storage

        >>> measure = MeasureDataCSV(
        >>>             app=None,
        >>>             parent=None,
        >>>             data=None,
        >>>                 )
    """

    __all__ = ['MeasureDataCSV',
               ]

    log = logging.getLogger(__name__)

    # update rate to 1 seconds for setting indi server
    CYCLE_UPDATE_TASK = 1000
    # maximum size of measurement task
    MAXSIZE = 24 * 60 * 60

    def __init__(self, app=None, parent=None, data=None):
        super().__init__()

        self.app = app
        self.parent = parent
        self.data = data
        self.deviceName = 'CSV'
        self.csvFilename = ''
        self.defaultConfig = {
            'csv': {
                'deviceName': 'save to file',
            }
        }
        self.csvFile = None
        self.csvWriter = None

        # time for measurement
        self.timerTask = PyQt6.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.measureTask)

    def openCSV(self):
        """
        :return: success
        """
        nameTime = self.app.mount.obsSite.timeJD.utc_strftime('%Y-%m-%d-%H-%M-%S')
        self.csvFilename = f'{self.app.mwGlob["measureDir"]}/measure-{nameTime}.csv'

        self.csvFile = open(self.csvFilename, 'w+')
        fieldnames = ['time',
                      'deltaRaJNow',
                      'deltaDecJNow',
                      'errorAngularPosRA',
                      'errorAngularPosDEC',
                      'status',
                      'sensor1WeatherTemp',
                      'sensor1WeatherHum',
                      'sensor1WeatherPress',
                      'sensor1WeatherDew',
                      'sensor1WeatherCloud',
                      'sensor1WeatherRain',
                      'sensor1WeatherSky',
                      'sensor2WeatherTemp',
                      'sensor2WeatherHum',
                      'sensor2WeatherPress',
                      'sensor2WeatherDew',
                      'sensor2WeatherCloud',
                      'sensor2WeatherRain',
                      'sensor2WeatherSky',
                      'sensor3WeatherTemp',
                      'sensor3WeatherHum',
                      'sensor3WeatherPress',
                      'sensor3WeatherDew',
                      'sensor3WeatherCloud',
                      'sensor3WeatherRain',
                      'sensor3WeatherSky',
                      'onlineWeatherTemp',
                      'onlineWeatherHum',
                      'onlineWeatherPress',
                      'onlineWeatherDew',
                      'onlineWeatherCloud',
                      'onlineWeatherRain',
                      'onlineWeatherSky',
                      'directWeatherTemp',
                      'directWeatherHum',
                      'directWeatherPress',
                      'directWeatherDew',
                      'filterNumber',
                      'focusPosition',
                      'powCurr1',
                      'powCurr2',
                      'powCurr3',
                      'powCurr4',
                      'powVolt',
                      'powCurr',
                      'cameraTemp',
                      'cameraPower',
                      'timeDiff',
                      ]

        self.csvWriter = csv.DictWriter(self.csvFile, fieldnames=fieldnames)
        self.csvWriter.writeheader()

        return True

    def writeCSV(self):
        """
        :return: success for write
        """
        if not self.csvFile or not self.csvWriter:
            return False

        row = dict()
        for key in self.data.keys():
            row[key] = self.data[key][0]

        self.csvWriter.writerow(row)
        return True

    def closeCSV(self):
        """
        :return: success for close
        """
        if not self.csvFile or not self.csvWriter:
            return False

        self.csvFile.close()
        self.csvWriter = None
        self.csvFile = None
        return True

    def startCommunication(self):
        """
        startCommunication starts cycling of the polling.
        :return: True for test purpose
        """
        self.parent.setEmptyData()
        self.timerTask.start(self.CYCLE_UPDATE_TASK)
        self.openCSV()
        return True

    def stopCommunication(self):
        """
        stopCommunication stops the device
        :return: true for test purpose
        """
        self.closeCSV()
        self.timerTask.stop()
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
        suc = self.parent.measureTask()
        if suc:
            self.writeCSV()

        return suc
