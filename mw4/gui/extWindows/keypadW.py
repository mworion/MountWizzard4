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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import sip

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import keypad_ui


class KeypadWindow(toolsQtWidget.MWidget):
    """
    the KeypadWindow window class handles

    """

    __all__ = ['KeypadWindow',
               ]

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = keypad_ui.Ui_KeypadDialog()
        self.ui.setupUi(self)
        self.host = None
        self.browser = QWebEngineView()
        self.ui.keypad.addWidget(self.browser)

        # avoid flickering in white
        self.browser.setVisible(False)
        self.browser.page().setBackgroundColor(PyQt5.QtCore.Qt.transparent)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        if 'keypadW' not in self.app.config:
            self.app.config['keypadW'] = {}
        config = self.app.config['keypadW']
        height = config.get('height', 500)
        width = config.get('width', 260)
        self.resize(width, height)
        x = config.get('winPosX', 0)
        y = config.get('winPosY', 0)
        if x > self.screenSizeX - width:
            x = 0
        if y > self.screenSizeY - height:
            y = 0
        if x != 0 and y != 0:
            self.move(x, y)
        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        if 'keypadW' not in self.app.config:
            self.app.config['keypadW'] = {}

        config = self.app.config['keypadW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.storeConfig()
        self.browser.loadFinished.disconnect(self.loadFinished)
        sip.delete(self.browser)
        self.browser = None
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        :return:
        """
        if not self.app.mount.setting.webInterfaceStat:
            self.app.message.emit('Enable webinterface', 0)
            suc = self.app.mount.setting.setWebInterface(True)
            if not suc:
                self.app.message.emit('Could not enable webinterface', 2)
        self.browser.loadFinished.connect(self.loadFinished)
        self.show()
        self.showUrl()
        return True

    def loadFinished(self):
        """
        :return:
        """
        self.browser.setVisible(True)
        return True

    def showUrl(self):
        """
        :return: success
        """
        if not self.app.mount.host[0]:
            return False

        file = f'qrc:/webif/virtkeypad.html?host={self.app.mount.host[0]}'
        self.browser.load(PyQt5.QtCore.QUrl(file))
        return True
