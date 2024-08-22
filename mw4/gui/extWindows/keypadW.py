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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PySide6.QtCore import Signal, QObject, QMutex
from PySide6.QtGui import QPixmap
from qimage2ndarray import array2qimage
import numpy as np

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import keypad_ui
from base.tpool import Worker
from logic.keypad.keypad import KeyPad


class KeypadSignals(QObject):
    """
    """
    __all__ = ['KeypadSignals']

    textRow = Signal(object, object)
    imgChunk = Signal(object, object, object)
    keyPressed = Signal(object)
    keyUp = Signal(object)
    keyDown = Signal(object)
    mousePressed = Signal(object)
    mouseReleased = Signal(object)
    cursorPos = Signal(object, object)
    clearCursor = Signal()


class KeypadWindow(toolsQtWidget.MWidget):
    """
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
        """
        if 'keypadW' not in self.app.config:
            self.app.config['keypadW'] = {}
        config = self.app.config['keypadW']

        self.positionWindow(config)

    def storeConfig(self):
        """
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

    def closeEvent(self, closeEvent):
        """
        """
        self.storeConfig()
        self.keypad.closeWebsocket()
        super().closeEvent(closeEvent)

    def keyPressEvent(self, keyEvent):
        """
        """
        key = keyEvent.key()
        if key == 16777216:
            key = 27
        elif key == 16777220:
            key = 13
        elif key == 16777249:
            key = 16

        if self.inputActive and keyEvent.type() == 6:
            self.signals.keyPressed.emit(key)
        elif not self.inputActive and keyEvent.type() == 6:
            self.signals.keyDown.emit(key)
            self.signals.keyUp.emit(key)

        super().keyPressEvent(keyEvent)

    def showWindow(self):
        """
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

    def colorChange(self):
        """
        """
        self.setStyleSheet(self.mw4Style)
        self.clearGraphics()

    def setupButtons(self):
        """
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

    def websocketClear(self):
        """
        """
        self.websocketMutex.unlock()

    def startKeypad(self):
        """
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
        """
        self.keypad.closeWebsocket()
        self.startKeypad()

    def buttonPressed(self):
        """
        """
        button = self.sender()
        if button not in self.buttons:
            return False

        self.signals.mousePressed.emit(self.buttons[button])
        return True

    def buttonReleased(self):
        """
        """
        button = self.sender()
        if button not in self.buttons:
            return False

        self.signals.mouseReleased.emit(self.buttons[button])
        return True

    def writeTextRow(self, row, text):
        """
        """
        if not -1 < row < 5:
            return False

        if text.startswith('>'):
            self.rows[row].setStyleSheet(f'background-color: {self.M_SEC};')
        else:
            self.rows[row].setStyleSheet(f'background-color: {self.M_BACK};')
        self.rows[row].setText(text)

        if row == 4 and not text.startswith('\x00'):
            self.clearGraphics()

        return True

    def clearGraphics(self):
        """
        """
        self.graphics = np.zeros([64, 128, 3], dtype=np.uint8)
        self.drawGraphics()

    def clearDisplay(self):
        """
        """
        for row in range(5):
            self.writeTextRow(row, '')
        self.clearGraphics()
        self.clearCursor()
        self.inputActive = False

    def clearCursor(self):
        """
        """
        self.inputActive = False
        self.ui.cursor.setVisible(False)

    def setCursorPos(self, row, col):
        """
        """
        self.inputActive = True
        x = self.rows[row].x()
        y = self.rows[row].y()
        height = self.rows[row].height()

        self.ui.cursor.setStyleSheet(f'background-color: {self.M_BACK};')
        self.ui.cursor.setStyleSheet(f'color: {self.M_PRIM};')
        self.ui.cursor.setVisible(True)
        self.ui.cursor.move(x + 16 * col, y + height)

    def drawGraphics(self):
        """
        """
        color = self.hex2rgb(self.M_PRIM)
        back = self.hex2rgb(self.M_BACK)
        pColor = [255, 255, 255]
        bColor = [0, 0, 0]

        img = np.copy(self.graphics)
        img[np.where((self.graphics == pColor).all(axis=2))] = color
        img[np.where((self.graphics == bColor).all(axis=2))] = back
        image = array2qimage(img)
        pixmap = QPixmap().fromImage(image).scaled(256, 128)
        self.ui.graphics.setPixmap(pixmap)

    def buildGraphics(self, imgArr, yPos, xPos):
        """
        """
        dy, dx, _ = imgArr.shape
        self.graphics[yPos: yPos + dy, xPos: xPos + dx] = imgArr
