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
from PyQt5.QtCore import pyqtSignal, QObject

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import keypad_ui
from base.tpool import Worker
from logic.virtkeypad.virtkeypad import KeyPad


class KeypadSignals(QObject):
    __all__ = ['KeypadSignals']

    textRow = pyqtSignal(object, object)
    imgChunk = pyqtSignal(object, object, object)
    keyPressed = pyqtSignal(object)
    cursorPos = pyqtSignal(object, object)


class KeypadWindow(toolsQtWidget.MWidget):
    """
    the KeypadWindow window class handles

    """

    __all__ = ['KeypadWindow',
               ]

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.threadPool = app.threadPool
        self.ui = keypad_ui.Ui_KeypadDialog()
        self.ui.setupUi(self)
        self.signals = KeypadSignals()
        self.keypad = KeyPad(self.signals)
        self.buttons = None
        self.rows = [
            self.ui.row0,
            self.ui.row1,
            self.ui.row2,
            self.ui.row3,
            self.ui.row4,
        ]

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
        self.keypad.closeWebsocket()
        self.storeConfig()
        self.app.colorChange.disconnect(self.colorChange)
        self.signals.textRow.disconnect(self.writeTextRow)
        self.signals.cursorPos.disconnect(self.setCursorPos)
        self.setupButtons(connect=False)
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
        self.app.colorChange.connect(self.colorChange)
        self.signals.textRow.connect(self.writeTextRow)
        self.signals.cursorPos.connect(self.setCursorPos)
        self.setupButtons(connect=True)
        self.show()
        worker = Worker(self.keypad.workerWebsocket, self.app.mount.host)
        self.threadPool.start(worker)
        return True

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        return True

    def setupButtons(self, connect=True):
        self.buttons = {
            self.ui.b0: 'key_0',
            self.ui.b1: 'key_1',
            self.ui.b2: 'key_2',
            self.ui.b3: 'key_3',
            self.ui.b4: 'key_4',
            self.ui.b5: 'key_5',
            self.ui.b6: 'key_6',
            self.ui.b7: 'key_7',
            self.ui.b8: 'key_8',
            self.ui.b9: 'key_9',
            self.ui.besc: 'key_esc',
            self.ui.bmenu: 'key_menu',
            self.ui.bstop: 'key_stop',
            self.ui.bplus: 'key_plus',
            self.ui.bminus: 'key_minus',
            self.ui.bup: 'key_up',
            self.ui.bdown: 'key_down',
            self.ui.bleft: 'key_left',
            self.ui.bright: 'key_right',
            self.ui.benter: 'key_enter',
        }
        for button in self.buttons:
            if connect:
                button.clicked.connect(self.buttonPress)
            else:
                button.clicked.disconnect(self.buttonPress)
        return True

    def buttonPress(self):
        """
        :return:
        """
        button = self.sender()
        if button not in self.buttons:
            return False

        keyData = self.keypad.buttonCodes[self.buttons[button]]
        self.signals.keyPressed.emit(keyData)
        return True

    def writeTextRow(self, row, text):
        """
        :param row:
        :param text:
        :return:
        """
        if not -1 < row < 5:
            return False

        if text[0] == '>':
            self.rows[row].setStyleSheet(f'background-color: {self.M_GREY};')
        else:
            self.rows[row].setStyleSheet(f'background-color: {self.M_BACK};')
        self.rows[row].setText(text)
        return True

    def setCursorPos(self, col, row):
        """
        :param col:
        :param row:
        :return:
        """
        print(row, col)
        self.rows[row].setCursorPosition(col)
        return True
