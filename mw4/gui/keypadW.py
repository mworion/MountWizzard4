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
        self.storeConfig()

        # gui signals
        super().closeEvent(closeEvent)

    def showWindow(self):
        """

        :return:
        """

        suc = self.showUrl()
        if suc:
            self.show()

    def clearWindow(self):
        """
        clearWindow resets the window and shows empty text.

        :return: true for test purpose
        """

        self.ui.message.clear()
        return True

    @staticmethod
    def insertStyleSheet(ui=None, name='', source='', immediately=False):
        """

        :param ui:
        :param name:
        :param source:
        :param immediately:
        :return: True for test purpose
        """

        script = QWebEngineScript()

        s = "(function() {"
        s += f"  css = document.getElementById('{name}');"
        s += "  css.type = 'text/css';"
        s += "  document.head.appendChild(css);"
        s += f" css.innerText = '{source}';"
        s += "})()"

        if immediately:
            ui.page().runJavaScript(s, QWebEngineScript.ApplicationWorld)

        script.setName(name)
        script.setSourceCode(s)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(True)
        script.setWorldId(QWebEngineScript.ApplicationWorld)
        ui.page().scripts().insert(script)

        return True

    @staticmethod
    def removeStyleSheet(ui=None, name='', immediately=False):
        """

        :param ui:
        :param name:
        :param immediately:
        :return: True for test purpose
        """

        s = "(function() {"
        s += f" var element = document.getElementById({name});"
        s += "  element.outerHTML = '';"
        s += "  delete element;"
        s += "})()"

        script = ui.page().scripts().findScript(name)

        if immediately:
            ui.page().runJavaScript(s, QWebEngineScript.ApplicationWorld)

        ui.page().scripts().remove(script)

        return True

    @staticmethod
    def removeClass(ui=None, name='',):
        """

        :param ui:
        :param name:
        :return: True for test purpose
        """

        s = f"val el = document.getElements('div').remove('{name}');"
        ui.page().runJavaScript(s, QWebEngineScript.ApplicationWorld)

        return True

    @staticmethod
    def setStyleKeypad(ui=None, name='', value=''):
        """

        :param ui:
        :param name:
        :param value:
        :return: True for test purpose
        """

        script = QWebEngineScript()
        s = f"document.querySelector('.{name}').style.backgroundColor = 'green';"

        print(s)

        script.setName('test')
        script.setSourceCode(s)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(True)
        script.setWorldId(QWebEngineScript.ApplicationWorld)
        ui.page().scripts().insert(script)

        return True

    def showUrl(self):
        """

        :return: success
        """

        host = self.app.mainW.ui.mountHost.text()
        if not host:
            return False

        url = f'http://{host}/virtkeypad.html'
        self.browser.load(PyQt5.QtCore.QUrl(url))

        # source = 'document.body.style.backgroundColor = "red";'
        source = 'background-color: #ff00ffff;'

        # self.setStyleKeypad(ui=self.browser, name='virtkp_canvas')

        self.removeClass(ui=self.browser, name='global-header')

        return True
