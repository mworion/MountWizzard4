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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

import glob
import os
import sys
import unittest.mock as mock
from pathlib import Path


import PySide6


import mw4.loader


def test_main_1():
    class App:
        @staticmethod
        def exec():
            return 0

        @staticmethod
        def setWindowIcon(a):
            return 0

    class Splash:
        @staticmethod
        def showMessage(a):
            return

        @staticmethod
        def setValue(a):
            return

        @staticmethod
        def close():
            return

    files = glob.glob("tests/work/config/*.cfg")
    for f in files:
        os.remove(f)

    mwGlob = {
        "configDir": Path("tests/work/config"),
        "dataDir": Path("tests/work/data"),
        "tempDir": Path("tests/work/temp"),
        "imageDir": Path("tests/work/image"),
        "modelDir": Path("tests/work/model"),
        "workDir": Path("mw4/tests/work"),
        "modeldata": "4.0",
    }
    with mock.patch.object(PySide6.QtCore.QBasicTimer, "start"):
        with mock.patch.object(PySide6.QtCore.QTimer, "start"):
            with mock.patch.object(mw4.loader, "QIcon"):
                with mock.patch.object(mw4.loader, "MyApp", return_value=App()):
                    with mock.patch.object(mw4.loader, "SplashScreen", return_value=Splash()):
                        with mock.patch.object(mw4.loader, "MountWizzard4"):
                            with mock.patch.object(
                                mw4.loader, "setupWorkDirs", return_value=mwGlob
                            ):
                                with mock.patch.object(sys, "exit"):
                                    with mock.patch.object(sys, "excepthook"):
                                        mw4.loader.main()
