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
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import shutil
import time
import os
import pytest

# external packages
import PySide6

# local import
from mainApp import MountWizzard4
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope="function")
def app(qapp):
    if not os.path.isfile("tests/work/data/de440_mw4.bsp"):
        shutil.copy(r"tests/testData/de440_mw4.bsp", r"tests/work/data/de440_mw4.bsp")


def test_start_parameters_1(qapp):
    mwGlob = {
        "configDir": "tests/work/config",
        "dataDir": "tests/work/data",
        "tempDir": "tests/work/temp",
        "imageDir": "tests/work/image",
        "modelDir": "tests/work/model",
        "workDir": "tests/work",
    }
    with open(mwGlob["workDir"] + "/test.run", "w+") as test:
        test.write("test")

    with mock.patch.object(PySide6.QtWidgets.QWidget, "show"):
        with mock.patch.object(PySide6.QtCore.QTimer, "start"):
            with mock.patch.object(PySide6.QtCore.QBasicTimer, "start"):
                with mock.patch.object(
                    MountWizzard4, "checkAndSetAutomation", return_value=None
                ):
                    MountWizzard4(mwGlob=mwGlob, application=qapp)
                    time.sleep(10)


def test_start_parameters_2(qapp):
    mwGlob = {
        "configDir": "tests/work/config",
        "dataDir": "tests/work/data",
        "tempDir": "tests/work/temp",
        "imageDir": "tests/work/image",
        "modelDir": "tests/work/model",
        "workDir": "tests/work",
    }
    with open(mwGlob["workDir"] + "/test.run", "w+") as test:
        test.write("test")

    with mock.patch.object(PySide6.QtWidgets.QWidget, "show"):
        with mock.patch.object(PySide6.QtCore.QTimer, "start"):
            with mock.patch.object(PySide6.QtCore.QBasicTimer, "start"):
                with mock.patch.object(
                    MountWizzard4, "checkAndSetAutomation", return_value=None
                ):
                    MountWizzard4(mwGlob=mwGlob, application=qapp)
                    time.sleep(10)
