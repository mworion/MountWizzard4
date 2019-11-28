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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import time
import json
import pkg_resources
import base64
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineScript
# local import
import mw4
from mw4.gui import widget
from mw4.gui.widgets import keypad_ui


class KeypadWindow(widget.MWidget):
    """
    the message window class handles

    """

    __all__ = ['KeypadWindow',
               ]

    logger = logging.getLogger(__name__)

    def __init__(self, app):
        super().__init__()
        self.app = app

        self.ui = keypad_ui.Ui_KeypadDialog()
        self.ui.setupUi(self)
        self.initUI()
        self.browser = PyQt5.QtWebEngineWidgets.QWebEngineView()
        self.ui.keypad.addWidget(self.browser)
        self.browser.setStyleSheet('background-color: #202020;')
        self.browser.setVisible(False)

        file = PyQt5.QtCore.QFile()
        file.setFileName(':/jquery.min.js')
        file.open(PyQt5.QtCore.QIODevice.ReadOnly)
        self.jQuery = file.readAll()
        self.jQuery.append("\nvar qt = {'jQuery': jQuery.noConflict(true) };")
        self.jQuery = bytes(self.jQuery).decode()
        file.close()

        self.initConfig()
        self.showWindow()

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
        x = config.get('winPosX', 100)
        y = config.get('winPosY', 100)
        if x > self.screenSizeX:
            x = 0
        if y > self.screenSizeY:
            y = 0
        self.move(x, y)
        height = config.get('height', 500)
        width = config.get('width', 260)
        self.resize(width, height)
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

        # gui signals
        super().closeEvent(closeEvent)

    def showWindow(self):
        """

        :return:
        """

        self.showUrl()
        self.show()

    def clearWindow(self):
        """
        clearWindow resets the window and shows empty text.

        :return: true for test purpose
        """

        self.ui.message.clear()
        return True

    def removeMainMenu(self):
        """

        :return: True for test purpose
        """

        s = "qt.jQuery('div').find('.global-header').hide();"
        self.browser.page().runJavaScript(s, QWebEngineScript.ApplicationWorld)

        return True

    def setKeypadBackground(self):
        """

        :return: True for test purpose
        """

        s = "qt.jQuery('div').find('.virtkeypad').css('background-color','#202020');"
        self.browser.page().runJavaScript(s, QWebEngineScript.ApplicationWorld)
        s = "qt.jQuery('div').find('.global-main').css('background-color','#202020');"
        self.browser.page().runJavaScript(s, QWebEngineScript.ApplicationWorld)

        return True

    def loadFinished(self):
        """

        :return:
        """

        self.browser.page().setBackgroundColor(PyQt5.QtCore.Qt.transparent)
        self.browser.page().runJavaScript(self.jQuery, QWebEngineScript.ApplicationWorld)
        self.removeMainMenu()
        self.setKeypadBackground()
        self.browser.setVisible(True)

    def showUrl(self):
        """

        :return: success
        """

        host = self.app.mainW.ui.mountHost.text()
        if not host:
            return False

        self.browser.loadFinished.connect(self.loadFinished)

        url = f'http://{host}/virtkeypad.html'
        self.browser.load(PyQt5.QtCore.QUrl(url))

        return True
