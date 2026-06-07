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
from unittest import mock


def test_addMissingFrameworksData_1(function):
    config = {"camera": {"frameworks": {"ascom": {}}}}
    cameraClass = function.app.dReg.drivers["camera"].instance
    with (
        mock.patch.object(cameraClass, "run", {"indi": None}),
        mock.patch.object(
            cameraClass,
            "defaultConfig",
            {"framework": "", "frameworks": {"indi": {"dummy": {}}}},
        ),
    ):
        result = function.addMissingFrameworksData("camera", config)
    assert result == {"camera": {"frameworks": {"ascom": {}, "indi": {"dummy": {}}}}}


def test_addMissingDefaultData_1(function):
    config = {"camera": {"ascom": {}}}
    with mock.patch.object(function, "addMissingFrameworksData"):
        function.addMissingDefaultData(config)


def test_removeUnknownDriversData_1(function):
    config = {"driversData": {"test": {}}}
    res = function.removeUnknownDriversData(config)
    assert res == {}


def test_loadDriversDataFromConfig_1(function):
    config = {}
    with (
        mock.patch.object(function, "addMissingDefaultData"),
        mock.patch.object(function, "removeUnknownDriversData"),
    ):
        function.loadDriversDataFromConfig(config)
        assert not function.driversData


def test_stopDriver_1(function):
    function.driversData["camera"] = {"framework": "indi"}
    cameraInstance = function.app.dReg["camera"].instance
    mockRun = {"indi": mock.MagicMock(deviceName="test_device")}
    with (
        mock.patch.object(cameraInstance, "framework", "indi"),
        mock.patch.object(cameraInstance, "run", mockRun),
        mock.patch.object(cameraInstance, "stopCommunication"),
    ):
        function.stopDriver("camera")
    assert function.app.dReg["camera"].stat is None


def test_stopDriver_2(function):
    function.driversData["camera"] = {"framework": "ascom"}
    cameraInstance = function.app.dReg["camera"].instance
    with (
        mock.patch.object(cameraInstance, "framework", "ascom"),
        mock.patch.object(cameraInstance, "run", {}),
    ):
        function.stopDriver("camera")


def test_stopDriver_3(function):
    function.driversData["camera"] = {"framework": "indi"}
    cameraInstance = function.app.dReg["camera"].instance
    mockRun = {"indi": mock.MagicMock(deviceName="")}
    with (
        mock.patch.object(cameraInstance, "framework", "indi"),
        mock.patch.object(cameraInstance, "run", mockRun),
    ):
        function.stopDriver("camera")


def test_stopDrivers_1(function):
    with mock.patch.object(function, "stopDriver") as mock_stop:
        function.stopDrivers()
        mock_stop.assert_called()


def test_configDriver_1(function):
    function.driversData["camera"] = {
        "framework": "indi",
        "frameworks": {"indi": {"loadConfig": True, }},
    }
    cameraInstance = function.app.dReg["camera"].instance
    mockRun = {"indi": mock.MagicMock()}
    with mock.patch.object(cameraInstance, "run", mockRun):
        function.configDriver("camera")
    assert function.app.dReg["camera"].stat is False


def test_configDriver_2(function):
    function.driversData["camera"] = {"framework": "ascom", "frameworks": {}}
    cameraInstance = function.app.dReg["camera"].instance
    with mock.patch.object(cameraInstance, "run", {}):
        function.configDriver("camera")


def test_startDriver_1(function):
    function.driversData["camera"] = {
        "framework": "indi",
        "frameworks": {"indi": {"loadConfig": True}},
    }
    cameraInstance = function.app.dReg["camera"].instance
    mockRun = {"indi": mock.MagicMock()}
    with (
        mock.patch.object(cameraInstance, "run", mockRun),
        mock.patch.object(function, "configDriver"),
    ):
        function.startDriver("camera", False)
    assert cameraInstance.loadConfig is True


def test_startDriver_2(function):
    function.driversData["camera"] = {
        "framework": "indi",
        "frameworks": {"indi": {"loadConfig": True}},
    }
    cameraInstance = function.app.dReg["camera"].instance
    mockRun = {"indi": mock.MagicMock()}
    with (
        mock.patch.object(cameraInstance, "run", mockRun),
        mock.patch.object(function, "configDriver"),
        mock.patch.object(cameraInstance, "startCommunication"),
    ):
        function.startDriver("camera", True)


def test_startDriver_3(function):
    function.driversData["camera"] = {"framework": "ascom", "frameworks": {}}
    cameraInstance = function.app.dReg["camera"].instance
    with mock.patch.object(cameraInstance, "run", {}):
        function.startDriver("camera", False)


def test_startDrivers_1(function):
    function.driversData["camera"] = {"framework": ""}
    with mock.patch.object(function, "startDriver"):
        function.startDrivers(False)


def test_startDrivers_2(function):
    function.driversData["camera"] = {"framework": "ascom"}
    with mock.patch.object(function, "startDriver") as mock_start:
        function.startDrivers(True)
        mock_start.assert_called()


def test_startDrivers_3(function):
    with mock.patch.object(function, "startDriver"):
        function.startDrivers(False)


def test_manualStopAllAscomDrivers_1(function):
    function.driversData["camera"] = {"framework": "ascom"}
    with mock.patch.object(function, "stopDriver") as mock_stop:
        function.manualStopAllAscomDrivers()
        mock_stop.assert_called()


def test_manualStopAllAscomDrivers_2(function):
    function.driversData["camera"] = {"framework": "alpaca"}
    with mock.patch.object(function, "stopDriver") as mock_stop:
        function.manualStopAllAscomDrivers()
        mock_stop.assert_called()


def test_manualStartAllAscomDrivers_1(function):
    function.driversData["camera"] = {"framework": "ascom"}
    with mock.patch.object(function, "startDriver") as mock_start:
        function.manualStartAllAscomDrivers()
        mock_start.assert_called()
