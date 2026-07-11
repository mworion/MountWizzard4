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
from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtGui import (
    QGuiApplication,
    QKeyEvent,
)
from PySide6.QtWidgets import (
    QMainWindow,
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
    POPUP_HEIGHT = 150
    RESIZE_MARGIN = 20

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
        self.is_resizing = False

        self.ws = QWidget()
        self.ws.setObjectName("ContainerContent")
        workSpaceLayout = QVBoxLayout()
        workSpaceLayout.setContentsMargins(2, 0, 2, 2)
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

    def mouseMoveEvent(self, event):
        pos = event.position()
        on_right = pos.x() >= self.width() - self.RESIZE_MARGIN
        on_bottom = pos.y() >= self.height() - self.RESIZE_MARGIN

        if on_right and on_bottom:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif on_right:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif on_bottom:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            if not self.is_resizing:
                self.setCursor(Qt.CursorShape.ArrowCursor)

        # Actively resize if mouse button is held down
        if self.is_resizing:
            new_width = max(100, int(pos.x()))
            new_height = max(100, int(pos.y()))
            self.resize(new_width, new_height)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            if (
                pos.x() >= self.width() - self.RESIZE_MARGIN
                or pos.y() >= self.height() - self.RESIZE_MARGIN
            ):
                self.is_resizing = True

    def mouseReleaseEvent(self, event):
        self.is_resizing = False

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

    def setPositionWindow(self, config: dict) -> None:
        height = config.get("height", self.minimumHeight())
        width = config.get("width", self.minimumWidth())
        self.resize(width, height)
        if height == self.maximumHeight() and width == self.maximumWidth():
            self.setWindowState(Qt.WindowState.WindowMaximized)
        x = config.get("winPosX", 0)
        y = config.get("winPosY", 0)
        self.move(x, y)

    def getPositionWindow(self, config: dict[str, int]) -> dict[str, int]:
        config["winPosX"] = self.pos().x()
        config["winPosY"] = self.pos().y()
        config["height"] = self.frameGeometry().height()
        config["width"] = self.frameGeometry().width()
        return config
