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
import numpy as np
import pytest
import unittest.mock as mock
from mw4.base.deviceRegistry import DeviceEntry
from mw4.logic.measure.measure import MeasureData
from mw4.logic.measure.measureCSV import MeasureDataCSV
from mw4.logic.measure.measureRaw import MeasureDataRaw
from tests.unit_tests.unitTestAddOns.baseTestApp import App


class Data:
    def __init__(self, data):
        self.data = data


@pytest.fixture(autouse=True, scope="module")
def function():
    func = MeasureData(app=App())
    yield func


def test_property(function):
    function.framework = "raw"
    function.deviceName = "test"
    assert function.deviceName == "test"


def test_collectDataDevices(function):
    # All devices listed in the measure mapping that have an instance are collected.
    function.collectDataDevices()
    assert "camera" in function.measuredDevices
    assert "focuser" in function.measuredDevices
    assert "directWeather" in function.measuredDevices


def test_collectDataDevices_unknownActiveDriver(function):
    # Devices not in the measure mapping are excluded.
    function.collectDataDevices()
    assert "sensor1Weather" in function.measuredDevices
    assert "unknownDevice" not in function.measuredDevices


def test_collectDataDevices_driverClassNone(function):
    # collectDataDevices uses dReg directly; devices with a real instance are included.
    function.collectDataDevices()
    assert "camera" in function.measuredDevices
    assert "focuser" in function.measuredDevices
    assert "directWeather" in function.measuredDevices


def test_clearData_1(function):
    function.measuredDevices = {"directWeather": object(), "test": object()}
    function.clearData()


def test_startCommunication_1(function):
    function.framework = "raw"
    function.run["raw"].deviceName = function.run["raw"].config.deviceName
    with (
        mock.patch.object(function.run[function.framework], "startCommunication"),
        mock.patch.object(function, "collectDataDevices"),
        mock.patch.object(function, "clearData"),
        mock.patch.object(function.signals, "deviceConnected"),
    ):
        function.startCommunication()


def test_stopCommunication_1(function):
    function.framework = "raw"
    function.run["raw"].deviceName = function.run["raw"].config.deviceName
    with (
        mock.patch.object(function.run[function.framework], "stopCommunication"),
        mock.patch.object(function.signals, "deviceDisconnected"),
    ):
        function.stopCommunication()


def test_checkStart_1(function):
    function.checkStart()


def test_checkStart_2(function):
    function.shorteningStart = True
    function.checkStart()


def test_checkStart_3(function):
    function.data = {"time": [2, 2, 2]}
    function.shorteningStart = True
    function.checkStart()


def test_checkSize_1(function):
    function.data.clear()
    function.data["time"] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data["directWeather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = np.array(
        [0, 0, 0, 0, 0, 0, 0, 0]
    )
    function.MAXSIZE = 20
    function.checkSize()


def test_checkSize_2(function):
    function.data.clear()
    function.data["time"] = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    function.data["directWeather-WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = np.array(
        [0, 0, 0, 0, 0, 0, 0, 0]
    )
    function.MAXSIZE = 5
    function.checkSize()


def test_measureTask_1(function):
    function.mutexMeasure.lock()
    function.measureTask()
    function.mutexMeasure.unlock()


def test_measureTask_2(function):
    data = {
        "WEATHER_PARAMETERS.WEATHER_TEMPERATURE": 0,
        "WEATHER_PARAMETERS.WEATHER_PRESSURE": 0,
        "WEATHER_PARAMETERS.WEATHER_DEWPOINT": 0,
        "WEATHER_PARAMETERS.WEATHER_HUMIDITY": 0,
    }

    function.measuredDevices = {"directWeather": Data(data=data)}
    function.clearData()
    with (
        mock.patch.object(function, "checkStart"),
        mock.patch.object(function, "checkSize"),
    ):
        function.measureTask()


def test_collectDataDevices_noneClass(function):
    # Entries whose instance is None must not appear in devices.
    savedDrivers = dict(function.app.dReg.d)
    function.app.dReg.d["camera"] = DeviceEntry(
        name="camera", instance=object(), deviceType="camera", isConfigurable=True
    )
    function.app.dReg.d["focuser"] = DeviceEntry(
        name="focuser", instance=None, deviceType="focuser", isConfigurable=True
    )
    try:
        function.collectDataDevices()
        assert "camera" in function.measuredDevices
        assert "focuser" not in function.measuredDevices
    finally:
        function.app.dReg.d.update(savedDrivers)


class TestMeasureDataRaw:
    @pytest.fixture(autouse=True, scope="function")
    def setUp(self):
        self.app = App()
        self.parent = MeasureData(app=self.app)
        self.data = {}
        self.raw = MeasureDataRaw(app=self.app, parent=self.parent, data=self.data)
        yield

    def test_init(self):
        assert self.raw.app == self.app
        assert self.raw.parent == self.parent
        assert self.raw.data == self.data
        assert self.raw.config.deviceName == "RAW display"
        assert hasattr(self.raw, "config")

    def test_startCommunication(self):
        with mock.patch.object(self.raw.timerTask, "start") as mock_start:
            self.raw.startCommunication()
            mock_start.assert_called_once_with(self.parent.CYCLE_UPDATE_TASK)

    def test_stopCommunication(self):
        with mock.patch.object(self.raw.timerTask, "stop") as mock_stop:
            self.raw.stopCommunication()
            mock_stop.assert_called_once()

    def test_measureTask(self):
        with mock.patch.object(self.parent, "measureTask") as mock_measure:
            self.raw.measureTask()
            mock_measure.assert_called_once()


class TestMeasureDataCSV:
    @pytest.fixture(autouse=True, scope="function")
    def setUp(self):
        self.app = App()
        self.parent = MeasureData(app=self.app)
        self.data = {}
        self.csv = MeasureDataCSV(app=self.app, parent=self.parent, data=self.data)
        yield

    def test_init(self):
        assert self.csv.app == self.app
        assert self.csv.parent == self.parent
        assert self.csv.data == self.data
        assert self.csv.config.deviceName == "CSV to file"
        assert hasattr(self.csv, "config")

    def test_writeHeaderCSV(self, tmp_path):
        csv_file = tmp_path / "test_header.csv"
        self.csv.csvFilename = csv_file
        self.csv.writeHeaderCSV()
        assert csv_file.exists()
        content = csv_file.read_text()
        assert "time" in content
        assert "mount-timeDiff" in content

    def test_writeCSV(self, tmp_path):
        csv_file = tmp_path / "test_write.csv"
        self.csv.csvFilename = csv_file
        self.csv.data = {
            "time": np.array([1]),
            "mount-timeDiff": np.array([10]),
            "filterNumber": np.array([0]),
        }
        self.csv.writeCSV()
        assert csv_file.exists()
        content = csv_file.read_text()
        assert "1" in content
        assert "10" in content

    def test_startCommunication(self, tmp_path):
        with (
            mock.patch.object(self.csv.timerTask, "start") as mock_start,
            mock.patch.object(self.app.mount.obsSite.timeJD, "utc_strftime") as mock_time,
            mock.patch.object(self.app, "mwGlob", {"measureDir": tmp_path}),
        ):
            mock_time.return_value = "2024-01-01-12-00-00"
            self.csv.startCommunication()
            mock_start.assert_called_once_with(self.parent.CYCLE_UPDATE_TASK)
            assert "measure-2024-01-01-12-00-00.csv" in str(self.csv.csvFilename)

    def test_stopCommunication(self):
        with mock.patch.object(self.csv.timerTask, "stop") as mock_stop:
            self.csv.stopCommunication()
            mock_stop.assert_called_once()

    def test_measureTask(self):
        with (
            mock.patch.object(self.parent, "measureTask"),
            mock.patch.object(self.csv, "writeCSV") as mock_write,
        ):
            self.csv.measureTask()
            mock_write.assert_called_once()
