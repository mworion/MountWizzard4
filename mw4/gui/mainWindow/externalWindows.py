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
from functools import partial

# external packages
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget

# local import
from base import packageConfig
if packageConfig.isAvailable:
    from gui.extWindows.simulatorW import SimulatorWindow

from gui.utilities.toolsQtWidget import sleepAndEvents, MWidget
from gui.extWindows.keypadW import KeypadWindow
from gui.extWindows.messageW import MessageWindow
from gui.extWindows.hemisphereW import HemisphereWindow
from gui.extWindows.measureW import MeasureWindow
from gui.extWindows.imageW import ImageWindow
from gui.extWindows.satelliteW import SatelliteWindow
from gui.extWindows.analyseW import AnalyseWindow
from gui.extWindows.videoW1 import VideoWindow1
from gui.extWindows.videoW2 import VideoWindow2
from gui.extWindows.videoW3 import VideoWindow3
from gui.extWindows.videoW4 import VideoWindow4
from gui.extWindows.bigPopupW import BigPopup


class ExternalWindows(MWidget):
    """
    """

    __all__ = ['ExternalWindows']

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app

        self.uiWindows = {'showMessageW': {
            'button': self.mainW.ui.openMessageW,
            'classObj': None,
            'name': 'MessageDialog',
            'class': MessageWindow,
        },  'showHemisphereW': {
            'button': self.mainW.ui.openHemisphereW,
            'classObj': None,
            'name': 'HemisphereDialog',
            'class': HemisphereWindow,
        },  'showImageW': {
            'button': self.mainW.ui.openImageW,
            'classObj': None,
            'name': 'ImageDialog',
            'class': ImageWindow,
        },  'showMeasureW': {
            'button': self.mainW.ui.openMeasureW,
            'classObj': None,
            'name': 'MeasureDialog',
            'class': MeasureWindow,
        },  'showSatelliteW': {
            'button': self.mainW.ui.openSatelliteW,
            'classObj': None,
            'name': 'SatelliteDialog',
            'class': SatelliteWindow,
        },  'showAnalyseW': {
            'button': self.mainW.ui.openAnalyseW,
            'classObj': None,
            'name': 'AnalyseDialog',
            'class': AnalyseWindow,
        },  'showVideoW1': {
            'button': self.mainW.ui.openV1,
            'classObj': None,
            'name': 'Video1',
            'class': VideoWindow1,
        },  'showVideoW2': {
            'button': self.mainW.ui.openV2,
            'classObj': None,
            'name': 'Video2',
            'class': VideoWindow2,
        },  'showVideoW3': {
            'button': self.mainW.ui.openV3,
            'classObj': None,
            'name': 'Video3',
            'class': VideoWindow3,
        },  'showVideoW4': {
            'button': self.mainW.ui.openV4,
            'classObj': None,
            'name': 'Video4',
            'class': VideoWindow4,
        },  'showKeypadW': {
            'button': self.mainW.ui.openKeypadW,
            'classObj': None,
            'name': 'KeypadDialog',
            'class': KeypadWindow,
        },  'showBigPopupW': {
            'button': self.mainW.ui.big,
            'classObj': None,
            'name': 'BigPopup',
            'class': BigPopup,
        }}

        if packageConfig.isAvailable:
            self.uiWindows['showSimulatorW'] = {
                'button': self.mainW.ui.mountConnected,
                'classObj': None,
                'name': 'SimulatorDialog',
                'class': SimulatorWindow,
            }

        for window in self.uiWindows:
            self.uiWindows[window]['button'].clicked.connect(
                partial(self.toggleWindow, window))

        self.app.update1s.connect(self.updateWindowsStats)
        self.mainW.ui.collectWindows.clicked.connect(self.collectWindows)

    def storeConfig(self) -> None:
        """
        """
        config = self.app.config
        for window in self.uiWindows:
            config[window] = bool(self.uiWindows[window]['classObj'])
            if config[window]:
                self.uiWindows[window]['classObj'].storeConfig()

    def updateWindowsStats(self) -> None:
        """
        """
        for win in self.uiWindows:
            winObj = self.uiWindows[win]

            if winObj['classObj']:
                self.changeStyleDynamic(winObj['button'], 'running', True)
            else:
                self.changeStyleDynamic(winObj['button'], 'running', False)

    def deleteWindowResource(self, widget: QWidget = None) -> bool:
        """
        :return: success
        """
        if not widget:
            return False

        for window in self.uiWindows:
            if self.uiWindows[window]['name'] != widget.objectName():
                continue
            del self.uiWindows[window]['classObj']
            self.uiWindows[window]['classObj'] = None

        return True

    def buildWindow(self, window: str) -> None:
        """
        """
        self.uiWindows[window]['classObj'] = self.uiWindows[window]['class'](self.app)
        self.uiWindows[window]['classObj'].destroyed.connect(self.deleteWindowResource)
        self.uiWindows[window]['classObj'].initConfig()
        self.uiWindows[window]['classObj'].showWindow()

    def showExtendedWindows(self) -> None:
        """
        """
        for window in self.uiWindows:
            if not self.app.config.get(window, False):
                continue
            self.buildWindow(window)

    def toggleWindow(self, windowName) -> None:
        """
        """
        if not self.uiWindows[windowName]['classObj']:
            self.buildWindow(windowName)
        else:
            self.uiWindows[windowName]['classObj'].close()

    def waitClosedExtendedWindows(self) -> bool:
        """
        """
        waitDeleted = True
        while waitDeleted:
            for window in self.uiWindows:
                if self.uiWindows[window]['classObj']:
                    continue

                waitDeleted = False
            sleepAndEvents(100)
        return True

    def closeExtendedWindows(self) -> None:
        """
        """
        for window in self.uiWindows:
            if not self.uiWindows[window]['classObj']:
                continue

            self.uiWindows[window]['classObj'].close()
        self.waitClosedExtendedWindows()

    def collectWindows(self) -> None:
        """
        """
        i = 0
        for i, window in enumerate(self.uiWindows):
            if self.uiWindows[window]['classObj']:
                self.uiWindows[window]['classObj'].resize(800, 600)
                self.uiWindows[window]['classObj'].move(i * 50 + 10, i * 50 + 10)
                self.uiWindows[window]['classObj'].activateWindow()
        self.mainW.move(i * 50 + 10, i * 50 + 10)
        self.mainW.activateWindow()
