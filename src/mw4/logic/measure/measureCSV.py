############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import csv
import logging
import PySide6
from dataclasses import dataclass, field
from pathlib import Path
from collections.abc import Any


@dataclass
class DeviceConfigMeasureCSV:
    deviceName: str = field(default="")
    filePath: str = field(default="")


class MeasureDataCSV(PySide6.QtCore.QObject):
    FieldNames = [
        "time",
        "mount-timeDiff",
        "mount-deltaRaJNow",
        "mount-deltaDecJNow",
        "mount-errorAngularPosRA",
        "mount-errorAngularPosDEC",
        "mount-status",
        "sensor1Weather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
        "sensor1Weather-WEATHER_PARAMETERS.WEATHER_HUMIDITY",
        "sensor1Weather-WEATHER_PARAMETERS.WEATHER_PRESSURE",
        "sensor1Weather-WEATHER_PARAMETERS.WEATHER_DEWPOINT",
        "sensor1Weather-WEATHER_PARAMETERS.CloudCov",
        "sensor1Weather-WEATHER_PARAMETERS.RainVol",
        "sensor1Weather-SKY_QUALITY.SKY_BRIGHTNESS",
        "sensor2Weather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
        "sensor2Weather-WEATHER_PARAMETERS.WEATHER_HUMIDITY",
        "sensor2Weather-WEATHER_PARAMETERS.WEATHER_PRESSURE",
        "sensor2Weather-WEATHER_PARAMETERS.WEATHER_DEWPOINT",
        "sensor2Weather-WEATHER_PARAMETERS.CloudCov",
        "sensor2Weather-WEATHER_PARAMETERS.RainVol",
        "sensor2Weather-SKY_QUALITY.SKY_BRIGHTNESS",
        "sensor3Weather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
        "sensor3Weather-WEATHER_PARAMETERS.WEATHER_HUMIDITY",
        "sensor3Weather-WEATHER_PARAMETERS.WEATHER_PRESSURE",
        "sensor3Weather-WEATHER_PARAMETERS.WEATHER_DEWPOINT",
        "sensor3Weather-WEATHER_PARAMETERS.CloudCov",
        "sensor3Weather-WEATHER_PARAMETERS.RainVol",
        "sensor3Weather-SKY_QUALITY.SKY_BRIGHTNESS",
        "sensor4Weather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
        "sensor4Weather-WEATHER_PARAMETERS.WEATHER_HUMIDITY",
        "sensor4Weather-WEATHER_PARAMETERS.WEATHER_PRESSURE",
        "sensor4Weather-WEATHER_PARAMETERS.WEATHER_DEWPOINT",
        "sensor4Weather-WEATHER_PARAMETERS.CloudCov",
        "sensor4Weather-WEATHER_PARAMETERS.RainVol",
        "sensor4Weather-SKY_QUALITY.SKY_BRIGHTNESS",
        "directWeather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE",
        "directWeather-WEATHER_PARAMETERS.WEATHER_HUMIDITY",
        "directWeather-WEATHER_PARAMETERS.WEATHER_PRESSURE",
        "directWeather-WEATHER_PARAMETERS.WEATHER_DEWPOINT",
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
    ]
    log = logging.getLogger("MW4")

    def __init__(
        self, app: Any = None, parent: Any = None, data: dict[str, float] = {}
    ) -> None:
        super().__init__()

        self.app = app
        self.parent = parent
        self.data = parent.data
        self.config = DeviceConfigMeasureCSV()
        self.config.deviceName = "CSV to file"
        self.csvFilename: Path = Path()
        self.csvFile: Any = None
        self.csvWriter: Any = None

        # time for measurement
        self.timerTask = PySide6.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.measureTask)

    def writeHeaderCSV(self) -> None:
        with open(self.csvFilename, "w+") as csvFile:
            csvWriter = csv.DictWriter(csvFile, fieldnames=self.FieldNames)
            csvWriter.writeheader()

    def writeCSV(self) -> None:
        row = {}
        for key in self.data:
            row[key] = self.data[key][0]
        with open(self.csvFilename, "a+") as csvFile:
            csvWriter = csv.DictWriter(csvFile, fieldnames=self.FieldNames)
            csvWriter.writerow(row)

    def startCommunication(self) -> None:
        self.timerTask.start(self.parent.CYCLE_UPDATE_TASK)
        nameTime = self.app.dReg["mount"].timeJD.utc_strftime("%Y-%m-%d-%H-%M-%S")
        self.csvFilename = self.app.mwGlob["measureDir"] / f"measure-{nameTime}.csv"
        self.writeHeaderCSV()

    def stopCommunication(self) -> None:
        self.timerTask.stop()

    def measureTask(self) -> None:
        self.parent.measureTask()
        self.writeCSV()
