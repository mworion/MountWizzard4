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
from PyQt5.QtCore import pyqtSignal, QObject, QMutex
from PyQt5.QtGui import QPixmap
from qimage2ndarray import array2qimage
import numpy as np

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import keypad_ui
from base.tpool import Worker
from logic.keypad.keypad import KeyPad


class KeypadSignals(QObject):
    __all__ = ['KeypadSignals']

    textRow = pyqtSignal(object, object)
    imgChunk = pyqtSignal(object, object, object)
    keyPressed = pyqtSignal(object)
    keyUp = pyqtSignal(object)
    keyDown = pyqtSignal(object)
    mousePressed = pyqtSignal(object)
    mouseReleased = pyqtSignal(object)
    cursorPos = pyqtSignal(object, object)
    clearCursor = pyqtSignal()


class KeypadWindow(toolsQtWidget.MWidget):
    """
    the KeypadWindow window class handles

    """

    __all__ = ['KeypadWindow']

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.msg = app.msg
        self.threadPool = app.threadPool
        self.ui = keypad_ui.Ui_KeypadDialog()
        self.ui.setupUi(self)
        self.signals = KeypadSignals()
        self.keypad = KeyPad(self.signals)
        self.buttons = None
        self.inputActive = False
        self.websocketMutex = QMutex()
        self.graphics = np.zeros([64, 128, 3], dtype=np.uint8)
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

        self.positionWindow(config)
        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config
        if 'keypadW' not in config:
            config['keypadW'] = {}
        else:
            config['keypadW'].clear()
        config = config['keypadW']

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
        self.keypad.closeWebsocket()
        super().closeEvent(closeEvent)

    def keyPressEvent(self, keyEvent):
        """
        :param keyEvent:
        :return:
        """
        key = keyEvent.key()
        if key == 16777216:
            key = 27
        elif key == 16777220:
            key = 13
        elif key == 16777249:
            key == 16

        if self.inputActive and keyEvent.type() == 6:
            self.signals.keyPressed.emit(key)
        elif not self.inputActive and keyEvent.type() == 6:
            self.signals.keyDown.emit(key)
            self.signals.keyUp.emit(key)

        super().keyPressEvent(keyEvent)

    def showWindow(self):
        """
        :return:
        """
        if not self.app.mount.setting.webInterfaceStat:
            self.msg.emit(0, 'System', 'Mount', 'Enable webinterface')
            suc = self.app.mount.setting.setWebInterface(True)
            if not suc:
                self.msg.emit(2, 'System', 'Mount',
                              'Could not enable webinterface')
        self.app.colorChange.connect(self.colorChange)
        self.app.hostChanged.connect(self.hostChanged)
        self.signals.textRow.connect(self.writeTextRow)
        self.signals.cursorPos.connect(self.setCursorPos)
        self.signals.imgChunk.connect(self.buildGraphics)
        self.signals.clearCursor.connect(self.clearCursor)
        self.app.update1s.connect(self.drawGraphics)
        self.setupButtons()
        self.show()
        self.startKeypad()
        return True

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        self.clearGraphics()
        return True

    def setupButtons(self):
        """
        :return:
        """
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
            button.pressed.connect(self.buttonPressed)
            button.released.connect(self.buttonReleased)
        return True

    def websocketClear(self):
        """
        :return:
        """
        self.websocketMutex.unlock()
        return True

    def startKeypad(self):
        """
        :return:
        """
        if not self.websocketMutex.tryLock():
            return False

        self.clearDisplay()
        self.writeTextRow(2, 'Connecting ...')
        worker = Worker(self.keypad.workerWebsocket, self.app.mount.host)
        worker.signals.finished.connect(self.websocketClear)
        self.threadPool.start(worker)
        return True

    def hostChanged(self):
        """
        :return:
        """
        self.keypad.closeWebsocket()
        self.startKeypad()
        return True

    def buttonPressed(self):
        """
        :return:
        """
        button = self.sender()
        if button not in self.buttons:
            return False

        self.signals.mousePressed.emit(self.buttons[button])
        return True

    def buttonReleased(self):
        """
        :return:
        """
        button = self.sender()
        if button not in self.buttons:
            return False

        self.signals.mouseReleased.emit(self.buttons[button])
        return True

    def writeTextRow(self, row, text):
        """
        :param row:
        :param text:
        :return:
        """
        if not -1 < row < 5:
            return False

        if text.startswith('>'):
            self.rows[row].setStyleSheet(f'background-color: {self.M_GREY};')
        else:
            self.rows[row].setStyleSheet(f'background-color: {self.M_BACK};')
        self.rows[row].setText(text)

        if row == 4 and not text.startswith('\x00'):
            self.clearGraphics()

        return True

    def clearGraphics(self):
        """
        :return:
        """
        self.graphics = np.zeros([64, 128, 3], dtype=np.uint8)
        self.drawGraphics()
        return True

    def clearDisplay(self):
        """
        :return:
        """
        for row in range(5):
            self.writeTextRow(row, '')
        self.clearGraphics()
        self.clearCursor()
        self.inputActive = False
        return True

    def clearCursor(self):
        """
        :return:
        """
        self.inputActive = False
        self.ui.cursor.setVisible(False)
        return True

    def setCursorPos(self, row, col):
        """
        :param row:
        :param col:
        :return:
        """
        self.inputActive = True
        x = self.rows[row].x()
        y = self.rows[row].y()
        height = self.rows[row].height()

        self.ui.cursor.setStyleSheet(f'background-color: {self.M_BACK};')
        self.ui.cursor.setStyleSheet(f'color: {self.M_BLUE};')
        self.ui.cursor.setVisible(True)
        self.ui.cursor.move(x + 16 * col, y + height)
        return True

    def drawGraphics(self):
        """
        :return:
        """
        color = self.hex2rgb(self.M_BLUE)
        back = self.hex2rgb(self.M_BACK)
        pColor = [255, 255, 255]
        bColor = [0, 0, 0]

        img = np.copy(self.graphics)
        img[np.where((self.graphics == pColor).all(axis=2))] = color
        img[np.where((self.graphics == bColor).all(axis=2))] = back
        image = array2qimage(img)
        pixmap = QPixmap().fromImage(image).scaled(256, 128)
        self.ui.graphics.setPixmap(pixmap)
        return True

    def buildGraphics(self, imgArr, yPos, xPos):
        """
        :return:
        """
        dy, dx, _ = imgArr.shape
        self.graphics[yPos: yPos + dy, xPos: xPos + dx] = imgArr
        return True
