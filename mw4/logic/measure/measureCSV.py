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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import csv

# external packages
import PySide6

# local imports


class MeasureDataCSV(PySide6.QtCore.QObject):
    """ """

    log = logging.getLogger("MW4")

    # update rate to 1 seconds for setting indi server
    CYCLE_UPDATE_TASK = 1000
    # maximum size of measurement task
    MAXSIZE = 24 * 60 * 60

    def __init__(self, app=None, parent=None, data=None):
        super().__init__()

        self.app = app
        self.parent = parent
        self.data = data
        self.deviceName = "CSV"
        self.csvFilename = ""
        self.defaultConfig = {
            "csv": {
                "deviceName": "save to file",
            }
        }
        self.csvFile = None
        self.csvWriter = None

        # time for measurement
        self.timerTask = PySide6.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.measureTask)

    def openCSV(self) -> None:
        """ """
        nameTime = self.app.mount.obsSite.timeJD.utc_strftime("%Y-%m-%d-%H-%M-%S")
        self.csvFilename = f"{self.app.mwGlob['measureDir']}/measure-{nameTime}.csv"

        self.csvFile = open(self.csvFilename, "w+")
        fieldnames = [
            "time",
            "deltaRaJNow",
            "deltaDecJNow",
            "errorAngularPosRA",
            "errorAngularPosDEC",
            "status",
            "sensor1WeatherTemp",
            "sensor1WeatherHum",
            "sensor1WeatherPress",
            "sensor1WeatherDew",
            "sensor1WeatherCloud",
            "sensor1WeatherRain",
            "sensor1WeatherSky",
            "sensor2WeatherTemp",
            "sensor2WeatherHum",
            "sensor2WeatherPress",
            "sensor2WeatherDew",
            "sensor2WeatherCloud",
            "sensor2WeatherRain",
            "sensor2WeatherSky",
            "sensor3WeatherTemp",
            "sensor3WeatherHum",
            "sensor3WeatherPress",
            "sensor3WeatherDew",
            "sensor3WeatherCloud",
            "sensor3WeatherRain",
            "sensor3WeatherSky",
            "onlineWeatherTemp",
            "onlineWeatherHum",
            "onlineWeatherPress",
            "onlineWeatherDew",
            "onlineWeatherCloud",
            "onlineWeatherRain",
            "onlineWeatherSky",
            "directWeatherTemp",
            "directWeatherHum",
            "directWeatherPress",
            "directWeatherDew",
            "filterNumber",
            "focusPosition",
            "powCurr1",
            "powCurr2",
            "powCurr3",
            "powCurr4",
            "powVolt",
            "powCurr",
            "cameraTemp",
            "cameraPower",
            "timeDiff",
        ]

        self.csvWriter = csv.DictWriter(self.csvFile, fieldnames=fieldnames)
        self.csvWriter.writeheader()

    def writeCSV(self) -> None:
        """ """
        if not self.csvFile or not self.csvWriter:
            return

        row = dict()
        for key in self.data.keys():
            row[key] = self.data[key][0]

        self.csvWriter.writerow(row)

    def closeCSV(self) -> None:
        """ """
        if not self.csvFile or not self.csvWriter:
            return

        self.csvFile.close()
        self.csvWriter = None
        self.csvFile = None

    def startCommunication(self) -> None:
        """ """
        self.parent.setEmptyData()
        self.timerTask.start(self.CYCLE_UPDATE_TASK)
        self.openCSV()

    def stopCommunication(self) -> None:
        """ """
        self.closeCSV()
        self.timerTask.stop()

    def measureTask(self) -> None:
        """
        measureTask runs all necessary pre-processing and collecting task to
        assemble a large dict of lists, where all measurement data is stored.
        the intention later on would be to store and export this data.
        the time object is related to the time held in mount computer and is
        in utc timezone.

        data sources are:
            environment
            mount pointing position

        :return: success
        """
        self.parent.measureTask()
        self.writeCSV()
