############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock

import pytest

# external packages
from PySide6.QtWidgets import QPushButton

import mw4.gui
from mw4.gui.mainWaddon.tabSett_Device import SettDevice
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = SettDevice(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_setDefaultData(function):
    config = {"camera": {}}
    function.setDefaultData("camera", config)


def test_loadDriversDataFromConfig_1(function):
    config = {}
    function.loadDriversDataFromConfig(config)


def test_loadDriversDataFromConfig_2(function):
    config = {"driversData": {"test": ""}}
    function.loadDriversDataFromConfig(config)


def test_initConfig_1(function):
    function.app.config["mainW"] = {}
    with mock.patch.object(function, "setupDeviceGui"):
        with mock.patch.object(function, "startDrivers"):
            with mock.patch.object(function, "loadDriversDataFromConfig"):
                function.initConfig()


def test_storeConfig_1(function):
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
    with mock.patch.object(function, "stopDriver"):
        with mock.patch.object(function, "startDriver"):
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
    with mock.patch.object(function, "stopDriver"):
        with mock.patch.object(function, "startDriver"):
            function.copyConfig("telescope", "telescope")


def test_copyConfig_2(function):
    function.drivers["telescope"]["class"].framework = "indi"
    function.drivers["cover"]["class"].framework = "indi"
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
    with mock.patch.object(function, "stopDriver"):
        with mock.patch.object(function, "startDriver"):
            function.copyConfig("telescope", "indi")


def test_copyConfig_3(function):
    function.drivers["telescope"]["class"].framework = "indi"
    function.drivers["cover"]["class"].framework = "indi"
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
    with mock.patch.object(function, "stopDriver"):
        with mock.patch.object(function, "startDriver"):
            function.copyConfig("telescope", "test")


def test_copyConfig_4(function):
    function.drivers["telescope"]["class"].framework = "indi"
    function.drivers["cover"]["class"].framework = "indi"
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
    with mock.patch.object(function, "stopDriver"):
        with mock.patch.object(function, "startDriver"):
            function.copyConfig("telescope", "indi")
            assert function.driversData["cover"]["frameworks"]["indi"]["test"] == 1


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

        ui = OK()

    function.driversData = {"cover": {}}
    test = function.drivers
    function.drivers = {"cover": {"deviceType": "cover", "class": mock.Mock()}}
    with mock.patch.object(mw4.gui.mainWaddon.tabSett_Device, "DevicePopup", return_value=Pop()):
        function.callPopup("cover")
    function.drivers = test


def test_stopDriver_2(function):
    function.drivers["telescope"]["class"].framework = None
    function.stopDriver("telescope")


def test_stopDriver_3(function):
    function.drivers["telescope"]["class"].framework = "indi"
    function.drivers["telescope"]["class"].run["indi"].deviceName = "indi"
    function.stopDriver("telescope")


def test_stopDrivers(function):
    with mock.patch.object(function, "stopDriver"):
        function.stopDrivers()


def test_configDriver_2(function):
    function.driversData = {
        "telescope": {
            "framework": "",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                },
            },
        }
    }
    function.configDriver("telescope")


def test_configDriver_3(function):
    function.driversData = {
        "telescope": {
            "framework": "indi",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                },
            },
        }
    }
    function.configDriver("telescope")


def test_startDriver_2(function):
    function.driversData = {
        "telescope": {
            "framework": "",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                },
            },
        }
    }
    function.startDriver("telescope", False)


def test_startDriver_3(function):
    function.driversData = {
        "telescope": {
            "framework": "indi",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                },
            },
        }
    }
    with mock.patch.object(function, "configDriver"):
        function.startDriver("telescope", False)


def test_startDriver_4(function):
    function.driversData = {
        "telescope": {
            "framework": "indi",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                },
            },
        }
    }
    with mock.patch.object(function, "configDriver"):
        with mock.patch.object(function, "configDriver"):
            function.startDriver("telescope", True)


def test_startDrivers_1(function):
    function.driversData = {
        "telescope": {
            "framework": "",
            "frameworks": {
                "indi": {
                    "deviceName": "astap",
                    "deviceList": ["test", "test1"],
                },
            },
        }
    }
    function.startDrivers()


def test_startDrivers_2(function):
    function.ui.autoConnectASCOM.setChecked(False)
    function.driversData = {
        "telescope": {
            "framework": "ascom",
        }
    }
    with mock.patch.object(function, "startDriver") as testMock:
        function.startDrivers()
        assert testMock.call_args.args == ("telescope", False)


def test_startDrivers_3(function):
    function.ui.autoConnectASCOM.setChecked(True)
    function.driversData = {
        "telescope": {
            "framework": "ascom",
        }
    }
    with mock.patch.object(function, "startDriver") as testMock:
        function.startDrivers()
        assert testMock.call_args.args == ("telescope", True)


def test_startDrivers_4(function):
    function.ui.autoConnectASCOM.setChecked(False)
    function.driversData = {
        "telescope": {
            "framework": "indi",
        }
    }
    with mock.patch.object(function, "startDriver") as testMock:
        function.startDrivers()
        assert testMock.call_args.args == ("telescope", True)


def test_manualStopAllAscomDrivers_1(function):
    function.driversData = {
        "telescope": {
            "framework": "ascom",
        }
    }
    with mock.patch.object(function, "stopDriver"):
        function.manualStopAllAscomDrivers()


def test_manualStartAllAscomDrivers_1(function):
    function.driversData = {
        "telescope": {
            "framework": "ascom",
        }
    }
    with mock.patch.object(function, "startDriver"):
        function.manualStartAllAscomDrivers()


def test_dispatchDriverDropdown_1(function):
    function.driversData = {
        "telescope": {
            "framework": "indi",
        }
    }
    function.drivers["telescope"]["uiDropDown"].addItem("indi - test")
    with mock.patch.object(function, "stopDriver"):
        with mock.patch.object(function, "startDriver"):
            function.dispatchDriverDropdown("telescope", 1)


def test_dispatchDriverDropdown_2(function):
    function.driversData = {
        "dome": {
            "framework": "indi",
        }
    }
    function.drivers["dome"]["uiDropDown"].addItem("device disabled")
    with mock.patch.object(function, "stopDriver"):
        with mock.patch.object(function, "startDriver"):
            function.dispatchDriverDropdown("dome", 0)


def test_serverDisconnected_1(function):
    function.serverDisconnected("dome", [])


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
