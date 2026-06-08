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
import mw4
import pytest
from mw4.gui.extWindows.setting.tabSettDevice import SettDevice
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QPushButton
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = SettDevice(mainW)
    yield window
    mainW.app.threadPool.waitForDone(10000)




def test_initConfig_1(function):
    function.app.config["WindowSetting"] = {}
    with (
        mock.patch.object(function, "setupDeviceGui"),
        mock.patch.object(function, "startDrivers"),
        mock.patch.object(function.dHandling, "loadDriversDataFromConfig"),
    ):
        function.initConfig()


def test_storeConfig_1(function):
    function.app.config["WindowSetting"] = {}
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_setupDeviceGui_1(function):
    function.driversData = {
        "telescope": {
            "framework": "astap",
            "frameworks": {
                "astap": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                    "searchRadius": 30,
                    "appPath": "test",
                },
            },
        }
    }
    function.setupDeviceGui()


def test_setupDeviceGui_2(function):
    function.driversData = {
        "test": {
            "framework": "astap",
            "frameworks": {
                "astap": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                    "searchRadius": 30,
                    "appPath": "test",
                },
            },
        }
    }
    function.setupDeviceGui()


def test_processPopupResults_2(function):
    class UI:
        ok = QPushButton()

    class Test:
        returnValues = {
            "driver": "telescope",
            "indiCopyConfig": True,
            "alpacaCopyConfig": True,
        }
        ui = UI()

    function.driversData = {
        "telescope": {
            "framework": "astap",
            "frameworks": {
                "astap": {
                    "deviceName": "",
                    "deviceList": ["test", "test1"],
                    "searchRadius": 30,
                    "appPath": "test",
                },
            },
        }
    }
    function.devicePopup = Test()
    function.devicePopup.ui.ok.clicked.connect(function.processPopupResults)
    with mock.patch.object(function, "copyConfig"):
        function.processPopupResults()


def test_processPopupResults_3(function):
    class UI:
        ok = QPushButton()

    class Test:
        returnValues = {"driver": "telescope"}
        ui = UI()

    function.driversData = {
        "telescope": {
            "framework": "astap",
            "frameworks": {
                "astap": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                    "searchRadius": 30,
                    "appPath": "test",
                },
            },
        }
    }
    function.devicePopup = Test()
    function.devicePopup.ui.ok.clicked.connect(function.processPopupResults)
    with mock.patch.object(function, "stopDriver"), mock.patch.object(function, "startDriver"):
        function.processPopupResults()


def test_copyConfig_1(function):
    function.driversData = {
        "telescope": {
            "framework": "astap",
            "frameworks": {
                "astap": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                    "searchRadius": 30,
                    "appPath": "test",
                },
            },
        }
    }
    with (
        mock.patch.object(function, "stopDriver"),
        mock.patch.object(function, "startDriver"),
        mock.patch.object(function.app.dReg, "configurable", return_value=[]),
    ):
        function.copyConfig("telescope", "telescope")


def test_copyConfig_2(function):
    function.driversData = {
        "telescope": {
            "framework": "indi",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                },
            },
        },
        "cover": {
            "framework": "indi",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                },
            },
        },
    }
    with (
        mock.patch.object(function, "stopDriver"),
        mock.patch.object(function, "startDriver"),
        mock.patch.object(function.app.dReg, "configurable", return_value=[]),
    ):
        function.copyConfig("telescope", "indi")


def test_copyConfig_3(function):
    function.driversData = {
        "telescope": {
            "framework": "indi",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                },
            },
        },
        "cover": {
            "framework": "indi",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                },
            },
        },
    }
    with (
        mock.patch.object(function, "stopDriver"),
        mock.patch.object(function, "startDriver"),
        mock.patch.object(function.app.dReg, "configurable", return_value=[]),
    ):
        function.copyConfig("telescope", "test")


def test_copyConfig_4(function):
    function.driversData = {
        "telescope": {
            "framework": "indi",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                    "test": 1,
                },
            },
        },
        "cover": {
            "framework": "indi",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                    "test": 2,
                },
            },
        },
    }
    with (
        mock.patch.object(function, "stopDriver"),
        mock.patch.object(function, "startDriver"),
        mock.patch.object(function.app.dReg, "configurable", return_value=[]),
    ):
        function.copyConfig("telescope", "indi")


def test_callPopup_1(function):
    class Pop:
        class OK:
            class Clicked:
                class Connect:
                    @staticmethod
                    def connect(a):
                        return

                clicked = Connect()

            ok = Clicked()

        def initConfig(self):
            pass

        ui = OK()

    function.driversData = {"cover": {}}
    with (
        mock.patch.object(function, "stopDriver"),
        mock.patch.object(
            mw4.gui.extWindows.setting.tabSettDevice, "DevicePopup", return_value=Pop()
        ),
    ):
        function.callPopup("cover")


def test_dispatchDriverDropdown_1(function):
    function.driversData = {
        "telescope": {
            "framework": "indi",
        }
    }
    function.setupUiDriver["telescope"]["uiDropDown"].addItem("indi - test")
    with mock.patch.object(function, "stopDriver"), mock.patch.object(function, "startDriver"):
        function.dispatchDriverDropdown("telescope", 1)


def test_dispatchDriverDropdown_2(function):
    function.driversData = {
        "dome": {
            "framework": "indi",
        }
    }
    function.setupUiDriver["dome"]["uiDropDown"].addItem("device disabled")
    with mock.patch.object(function, "stopDriver"), mock.patch.object(function, "startDriver"):
        function.dispatchDriverDropdown("dome", 0)


def test_deviceConnected_2(function):
    function.driversData = {
        "filter": {"framework": "indi", "frameworks": {"indi": {"loadConfig": True}}}
    }
    function.BACK_GREEN = "#000000"
    function.deviceConnected("filter", "test")


def test_deviceConnected_3(function):
    function.driversData = {
        "dome": {"framework": "indi", "frameworks": {"indi": {"loadConfig": True}}}
    }
    function.BACK_GREEN = "#000000"
    function.deviceConnected("dome", "test")


def test_deviceDisconnected_1(function):
    function.deviceDisconnected("dome", "test")


def test_startDrivers_1(function):
    function.ui.autoConnectASCOM.setChecked(True)
    with mock.patch.object(function.dHandling, "startDrivers"):
        function.startDrivers()


def test_stopDrivers_1(function):
    with mock.patch.object(function.dHandling, "stopDrivers"):
        function.stopDrivers()


def test_startDriver_1(function):
    with mock.patch.object(function.dHandling, "startDriver"):
        function.startDevice("telescope", True)


def test_stopDriver_1(function):
    with mock.patch.object(function.dHandling, "stopDriver"):
        function.stopDevice("telescope")


def test_copyConfig_with_entries(function):
    class MockEntry:
        def __init__(self, name, framework):
            self.name = name
            self.instance = mock.Mock()
            self.instance.framework = framework

    function.driversData = {
        "telescope": {
            "framework": "indi",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                    "testParam": "testValue",
                },
            },
        },
        "camera": {
            "framework": "indi",
            "frameworks": {
                "indi": {
                    "deviceName": "camera",
                    "deviceList": ["test", "test1"],
                    "testParam": "oldValue",
                },
            },
        },
    }
    mock_entries = [
        MockEntry("telescope", "indi"),
        MockEntry("camera", "indi"),
    ]
    with (
        mock.patch.object(function, "stopDriver"),
        mock.patch.object(function.app.dReg, "configurable", return_value=mock_entries),
    ):
        function.copyConfig("telescope", "indi")

