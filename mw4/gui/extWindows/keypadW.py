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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PySide6.QtCore import Signal, QObject, QMutex
from PySide6.QtGui import QPixmap
from qimage2ndarray import array2qimage
import numpy as np
from functools import partial

# local import
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets import keypad_ui
from base.tpool import Worker
from logic.keypad.keypad import KeyPad


class KeypadSignals(QObject):
    """ """

    textRow = Signal(object, object)
    imgChunk = Signal(object, object, object)
    keyPressed = Signal(object)
    keyUp = Signal(object)
    keyDown = Signal(object)
    mousePressed = Signal(object)
    mouseReleased = Signal(object)
    cursorPos = Signal(object, object)
    clearCursor = Signal()


class KeypadWindow(MWidget):
    """ """

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.msg = app.msg
        self.threadPool = app.threadPool
        self.ui = keypad_ui.Ui_KeypadDialog()
        self.ui.setupUi(self)
        self.signals = KeypadSignals()
        self.keypad = KeyPad(self.signals)
        self.inputActive: bool = False
        self.websocketMutex = QMutex()
        self.worker: Worker = None

        self.graphics = np.zeros([64, 128, 3], dtype=np.uint8)
        self.buttons = {
            "key_0": self.ui.b0,
            "key_1": self.ui.b1,
            "key_2": self.ui.b2,
            "key_3": self.ui.b3,
            "key_4": self.ui.b4,
            "key_5": self.ui.b5,
            "key_6": self.ui.b6,
            "key_7": self.ui.b7,
            "key_8": self.ui.b8,
            "key_9": self.ui.b9,
            "key_esc": self.ui.besc,
            "key_menu": self.ui.bmenu,
            "key_stop": self.ui.bstop,
            "key_plus": self.ui.bplus,
            "key_minus": self.ui.bminus,
            "key_up": self.ui.bup,
            "key_down": self.ui.bdown,
            "key_left": self.ui.bleft,
            "key_right": self.ui.bright,
            "key_enter": self.ui.benter,
        }
        self.rows = [
            self.ui.row0,
            self.ui.row1,
            self.ui.row2,
            self.ui.row3,
            self.ui.row4,
        ]

    def initConfig(self) -> None:
        """ """
        config = self.app.config.get("keypadW", {})
        self.positionWindow(config)

    def storeConfig(self) -> None:
        """ """
        configMain = self.app.config
        configMain["keypadW"] = {}
        config = configMain["keypadW"]

        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()
        config["width"] = self.width()

    def closeEvent(self, closeEvent) -> None:
        """ """
        self.storeConfig()
        self.keypad.closeWebsocket()
        super().closeEvent(closeEvent)

    def keyPressEvent(self, keyEvent) -> None:
        """ """
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

    def showWindow(self) -> None:
        """ """
        if not self.app.mount.setting.webInterfaceStat:
            self.msg.emit(0, "System", "Mount", "Enable webinterface")
            if not self.app.mount.setting.setWebInterface(True):
                self.msg.emit(2, "System", "Mount", "Could not enable webinterface")
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

    def colorChange(self) -> None:
        """ """
        self.setStyleSheet(self.mw4Style)
        for row in self.rows:
            row.setStyleSheet(f"background-color: {self.M_BACK};")
        self.clearGraphics()

    def setupButtons(self) -> None:
        """ """
        for button in self.buttons:
            self.buttons[button].pressed.connect(partial(self.buttonPressed, button))
            self.buttons[button].released.connect(partial(self.buttonReleased, button))

    def websocketClear(self) -> None:
        """ """
        self.websocketMutex.unlock()

    def startKeypad(self) -> None:
        """ """
        if not self.websocketMutex.tryLock():
            return

        self.clearDisplay()
        self.writeTextRow(2, "Connecting ...")
        self.worker = Worker(self.keypad.workerWebsocket, self.app.mount.host)
        self.worker.signals.finished.connect(self.websocketClear)
        self.threadPool.start(self.worker)

    def hostChanged(self) -> None:
        """ """
        self.keypad.closeWebsocket()
        self.websocketMutex.unlock()
        self.startKeypad()

    def buttonPressed(self, button: str) -> None:
        """ """
        self.signals.mousePressed.emit(button)

    def buttonReleased(self, button: str) -> None:
        """ """
        self.signals.mouseReleased.emit(button)

    def writeTextRow(self, row: int, text: str) -> None:
        """ """
        if not -1 < row < 5:
            return

        col = self.M_SEC if text.startswith(">") else self.M_BACK
        self.rows[row].setStyleSheet(f"background-color: {col};")
        self.rows[row].setText(text)

        if row == 4 and not text.startswith("\x00"):
            self.clearGraphics()

    def clearGraphics(self) -> None:
        """ """
        self.graphics = np.zeros([64, 128, 3], dtype=np.uint8)
        self.drawGraphics()

    def clearDisplay(self) -> None:
        """ """
        for row in range(5):
            self.writeTextRow(row, "")
        self.clearGraphics()
        self.clearCursor()
        self.inputActive = False

    def clearCursor(self):
        """ """
        self.inputActive = False
        self.ui.cursor.setVisible(False)

    def setCursorPos(self, row: int, col: int) -> None:
        """ """
        self.inputActive = True
        x = self.rows[row].x()
        y = self.rows[row].y()
        height = self.rows[row].height()

        self.ui.cursor.setStyleSheet(f"background-color: {self.M_BACK};")
        self.ui.cursor.setStyleSheet(f"color: {self.M_PRIM};")
        self.ui.cursor.setVisible(True)
        self.ui.cursor.move(x + 16 * col, y + height)

    def drawGraphics(self) -> None:
        """ """
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

    def buildGraphics(self, imgArr: np.array, yPos: int, xPos: int) -> None:
        """ """
        dy, dx, _ = imgArr.shape
        self.graphics[yPos : yPos + dy, xPos : xPos + dx] = imgArr
