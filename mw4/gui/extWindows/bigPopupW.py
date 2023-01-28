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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import
from gui.utilities import toolsQtWidget
from gui.widgets.bigPopup_ui import Ui_BigPopup


class BigPopup(toolsQtWidget.MWidget):
    """
    the StopPopup window class handles

    """

    __all__ = ['BigPopup']

    def __init__(self, app):

        super().__init__()
        self.app = app
        self.ui = Ui_BigPopup()
        self.ui.setupUi(self)
        self.parent = app.mainW
        self.msg = app.msg
        self.setWindowTitle('Big buttons')

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'bigPopupW' not in self.app.config:
            self.app.config['bigPopupW'] = {}
        config = self.app.config['bigPopupW']
        self.positionWindow(config)
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config
        if 'bigPopupW' not in config:
            config['bigPopupW'] = {}
        else:
            config['bigPopupW'].clear()
        config = config['bigPopupW']

        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        return True

    def showWindow(self):
        """
        :return: True for test purpose
        """
        self.wIcon(self.ui.mountOn, 'power-on')
        self.wIcon(self.ui.mountOff, 'power-off')
        self.wIcon(self.ui.stop, 'hand')

        self.app.colorChange.connect(self.colorChange)
        self.app.update1s.connect(self.updateDeviceStats)
        self.app.mount.signals.pointDone.connect(self.updateStatus)
        self.ui.stop.clicked.connect(lambda: self.app.virtualStop.emit())
        self.ui.mountOn.clicked.connect(lambda: self.app.mountOn.emit())
        self.ui.mountOff.clicked.connect(lambda: self.app.mountOff.emit())
        self.show()
        return True

    def updateDeviceStats(self):
        """
        :return:
        """
        isMount = self.app.deviceStat.get('mount', False)
        self.changeStyleDynamic(self.ui.mountOn, 'running', isMount)
        self.changeStyleDynamic(self.ui.mountOff, 'running', not isMount)
        return True

    def updateStatus(self):
        """
        :return:
        """
        if self.app.mount.obsSite.status == 1:
            self.changeStyleDynamic(self.ui.stop, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.stop, 'running', False)
        return True
