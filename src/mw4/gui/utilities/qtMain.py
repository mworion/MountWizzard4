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
# License APL2.0
#
###########################################################
import datetime
import logging
from mw4.gui.styles.styles import Styles
from mw4.gui.utilities.qtCustomWindow import CustomTitleBar
from mw4.gui.utilities.qtHelpers import svg2icon
from pathlib import Path
from PySide6.QtCore import QDir, QEvent, QSize, Qt
from PySide6.QtGui import (
    QGuiApplication,
    QKeyEvent,
    QPixmap,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MWidget(QMainWindow, Styles):
    log = logging.getLogger("MW4")
    FULL_WIDTH = 800
    FULL_HEIGHT = 620
    HALF_WIDTH = 400
    HALF_HEIGHT = 310

    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        self.screenSizeX = QGuiApplication.primaryScreen().geometry().width()
        self.screenSizeY = QGuiApplication.primaryScreen().geometry().height()
        self.setWindowIcon(self.mwIcon)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.titleBar = CustomTitleBar(self)

        self.ws = QWidget()
        self.ws.setObjectName("ContainerContent")
        workSpaceLayout = QVBoxLayout()
        workSpaceLayout.setContentsMargins(0, 0, 0, 0)
        workSpaceLayout.addWidget(self.ws)
        centralWidgetLayout = QVBoxLayout()
        centralWidgetLayout.setContentsMargins(0, 0, 0, 0)
        centralWidgetLayout.addWidget(self.titleBar)
        centralWidgetLayout.addLayout(workSpaceLayout)
        centralWidgetLayout.setSpacing(4)
        centralWidget = QWidget()
        centralWidget.setObjectName("ContainerCentral")
        centralWidget.setLayout(centralWidgetLayout)
        self.setCentralWidget(centralWidget)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.WindowStateChange:
            self.titleBar.windowStateChanged(self.windowState())
        super().changeEvent(event)
        event.accept()

    def setWindowTitle(self, title: str) -> None:
        if hasattr(self, "titleBar"):
            self.titleBar.title.setText(title)

    @staticmethod
    def saveWindowAsPNG(window: QWidget) -> None:
        name = window.windowTitle().replace(" ", "_")
        timeTrigger = datetime.datetime.now(datetime.UTC)
        timeTag = timeTrigger.strftime("%Y-%m-%d-%H-%M-%S")
        path = window.app.mwGlob["logDir"]
        fullFileName = f"{path}/{timeTag}-{name}.png"
        window.log.info(f"Screenshot: [{fullFileName}]")
        window.grab().save(fullFileName)

    def saveAllWindowsAsPNG(self, window: QWidget) -> None:
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
        dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint)
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
        buttons: list[str] = [],
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
        if not buttons:
            msg.setStandardButtons(msg.StandardButton.Yes | msg.StandardButton.No)
            msg.setDefaultButton(msg.StandardButton.No)
        else:
            for button in buttons:
                msg.addButton(button, QMessageBox.ButtonRole.AcceptRole)
            msg.setDefaultButton(QMessageBox.StandardButton.Cancel)
        msg.adjustSize()
        x = parentWidget.x() + int((parentWidget.width() - msg.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - msg.height()) / 2)
        msg.move(x, y)
        reply = self.runDialog(msg)

        if not buttons:
            return reply == msg.StandardButton.Yes
        else:
            return reply

    def openFileBase(
        self, window: QWidget, title: str, folder: Path, filterSet: str, multiple: bool = False
    ) -> list[str]:
        dlg = self.prepareFileDialog(window=window)
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dlg.setWindowTitle(title)
        dlg.setNameFilter(filterSet)
        dlg.setDirectory(str(folder))
        fileMode = (
            QFileDialog.FileMode.ExistingFiles
            if multiple
            else QFileDialog.FileMode.ExistingFile
        )
        dlg.setFileMode(fileMode)
        self.runDialog(dlg)
        return dlg.selectedFiles()

    def openMultipleFiles(
        self, window: QWidget, title: str, folder: Path, filterSet: str
    ) -> list[Path]:
        files = self.openFileBase(window, title, folder, filterSet, multiple=True)
        return [Path(f) for f in files]

    def openFile(self, window: QWidget, title: str, folder: Path, filterSet: str) -> Path:
        files = self.openFileBase(window, title, folder, filterSet)
        file = files[0] if files else ""
        return Path(file)

    def saveFile(
        self,
        window: QWidget,
        title: str,
        folder: Path,
        filterSet: str,
        enableDir: bool = False,
    ) -> Path:
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
