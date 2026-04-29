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
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################
import datetime
import logging
from dateutil.tz import tzlocal
from mw4.gui.styles.styles import Styles
from mw4.gui.utilities.qtHelpers import svg2icon
from pathlib import Path
from PySide6.QtCore import QDir, QSize, Qt
from PySide6.QtGui import (
    QGuiApplication,
    QKeyEvent,
    QPixmap,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QPushButton,
    QWidget,
)
from skyfield.api import Time


class MWidget(QWidget, Styles):
    log = logging.getLogger("MW4")

    def __init__(self):
        super().__init__()
        self.initUI()
        self.screenSizeX = QGuiApplication.primaryScreen().geometry().width()
        self.screenSizeY = QGuiApplication.primaryScreen().geometry().height()

        newFlag = Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowSystemMenuHint
        newFlag = (
            newFlag
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
        )
        self.setWindowFlags(self.windowFlags() | newFlag)
        self.setWindowIcon(self.mwIcon)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.app = None
        self.ui = None

    @staticmethod
    def saveWindowAsPNG(window) -> None:
        name = window.windowTitle().replace(" ", "_")
        timeTrigger = datetime.datetime.now(datetime.UTC)
        timeTag = timeTrigger.strftime("%Y-%m-%d-%H-%M-%S")
        path = window.app.mwGlob["logDir"]
        fullFileName = f"{path}/{timeTag}-{name}.png"
        window.log.info(f"Screenshot: [{fullFileName}]")
        window.grab().save(fullFileName)

    def saveAllWindowsAsPNG(self, window):
        windows = window.app.mainW.externalWindows.uiWindows
        self.saveWindowAsPNG(window)
        for window in windows:
            if windows[window]["classObj"]:
                self.saveWindowAsPNG(windows[window]["classObj"])

    def keyPressEvent(self, keyEvent: QKeyEvent) -> None:
        if keyEvent.key() == Qt.Key.Key_F5:
            self.saveWindowAsPNG(self)
            return
        elif keyEvent.key() == Qt.Key.Key_F6:
            self.saveAllWindowsAsPNG(self)
            return
        super().keyPressEvent(keyEvent)

    def wIcon(self, gui: QPushButton, name: str) -> None:
        icon = svg2icon(f"assets/icon/{name}.svg", self.M_TER)
        gui.setIcon(icon)
        gui.setIconSize(QSize(16, 16))
        gui.setProperty("alignLeft", True)
        gui.style().unpolish(gui)
        gui.style().polish(gui)

    def initUI(self) -> None:
        self.setStyleSheet(self.mw4Style)
        self.setMouseTracking(True)
        self.setWindowIcon(self.mwIcon)

    def prepareFileDialog(self, window: QWidget, enableDir: bool = False) -> QFileDialog:
        dlg = QFileDialog()
        dlg.setOptions(QFileDialog.Option.DontUseNativeDialog)
        dlg.setWindowIcon(self.mwIcon)
        dlg.setStyleSheet(self.mw4Style)
        dlg.setViewMode(QFileDialog.ViewMode.List)
        dlg.setModal(True)
        if enableDir:
            dlg.setFilter(QDir.Filter.Files | QDir.Filter.AllDirs)
        else:
            dlg.setFilter(QDir.Filter.Files)

        width = 600
        height = 400
        ph = window.geometry().height()
        pw = window.geometry().width()
        px = window.geometry().x()
        py = window.geometry().y()

        dlg.setGeometry(
            px + int(0.5 * (pw - width)), py + int(0.5 * (ph - height)), width, height
        )
        return dlg

    @staticmethod
    def runDialog(dlg: QMessageBox | QFileDialog) -> int:
        return dlg.exec()

    def messageDialog(
        self,
        parentWidget: QWidget,
        title: str,
        question: str,
        buttons: list[str] = None,
        iconType: int = 0,
    ) -> int:
        msg = QMessageBox()
        msg.setWindowModality(Qt.WindowModality.ApplicationModal)
        msg.setStyleSheet(self.mw4Style)
        msg.setTextFormat(Qt.TextFormat.AutoText)
        msg.setWindowTitle(title)
        icons = [
            "assets/icon/question.svg",
            "assets/icon/information.svg",
            "assets/icon/warning.svg",
            "assets/icon/question.svg",
        ]
        pixmap = QPixmap(icons[iconType]).scaled(64, 64)
        msg.setIconPixmap(pixmap)
        msg.setText(question)
        if buttons is None:
            msg.setStandardButtons(msg.StandardButton.Yes | msg.StandardButton.No)
            msg.setDefaultButton(msg.StandardButton.No)
        else:
            for button in buttons:
                msg.addButton(button, QMessageBox.ButtonRole.AcceptRole)
            msg.setDefaultButton(QMessageBox.StandardButton.Cancel)
        msg.show()
        x = parentWidget.x() + int((parentWidget.width() - msg.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - msg.height()) / 2)
        msg.move(x, y)
        reply = self.runDialog(msg)

        if buttons is None:
            return reply == msg.StandardButton.Yes
        else:
            return reply

    def openFile(
        self,
        window: QWidget,
        title: str,
        folder: Path,
        filterSet: str,
        enableDir: bool = False,
        multiple: bool = False,
    ):
        dlg = self.prepareFileDialog(window=window, enableDir=enableDir)
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dlg.setWindowTitle(title)
        dlg.setNameFilter(filterSet)
        dlg.setDirectory(str(folder))

        if multiple:
            dlg.setFileMode(QFileDialog.FileMode.ExistingFiles)
        else:
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)

        result = self.runDialog(dlg)
        if not result:
            return [] if multiple else Path("")

        if multiple:
            return [Path(f) for f in dlg.selectedFiles()]
        else:
            return Path(dlg.selectedFiles()[0])

    def saveFile(
        self,
        window: QWidget,
        title: str,
        folder: Path,
        filterSet: str,
        enableDir: bool = False,
    ):
        dlg = self.prepareFileDialog(window, enableDir)
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dlg.setWindowTitle(title)
        dlg.setNameFilter(filterSet)
        dlg.setDirectory(str(folder))
        result = self.runDialog(dlg)
        if not result:
            return Path()

        return Path(dlg.selectedFiles()[0])

    def openDir(self, window: QWidget, title: str, folder: Path) -> Path:
        dlg = self.prepareFileDialog(window=window, enableDir=True)
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dlg.setWindowTitle(title)
        dlg.setDirectory(str(folder))
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        result = self.runDialog(dlg)
        if not result:
            return Path()

        return Path(dlg.selectedFiles()[0])

    def convertTime(self, value: Time, fString: str) -> str:
        isUTC = self.ui.unitTimeUTC.isChecked()
        if isUTC:
            return value.utc_strftime(fString)
        else:
            return value.astimezone(tzlocal()).strftime(fString)

    def timeZoneString(self) -> str:
        if self.ui.unitTimeUTC.isChecked():
            return "(time is UTC)"
        else:
            return "(time is local)"

    def positionWindow(self, config: dict) -> None:
        height = config.get("height", 600)
        width = config.get("width", 800)
        self.resize(width, height)
        x = config.get("winPosX", 0)
        y = config.get("winPosY", 0)
        if x > self.screenSizeX - width:
            x = 0
        if y > self.screenSizeY - height:
            y = 0
        x = max(x, 0)
        y = max(y, 0)
        if x != 0 and y != 0:
            self.move(x, y)
