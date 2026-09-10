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
import platform
from mw4.gui.styles.styles import Styles
from mw4.gui.utilities.qtCustomWindow import CustomTitleBar
from mw4.gui.utilities.qtHelpers import svg2icon
from PySide6.QtCore import QEvent, QPoint, QSize, Qt
from PySide6.QtGui import (
    QGuiApplication,
    QKeyEvent,
)
from PySide6.QtWidgets import (
    QComboBox,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from typing import ClassVar


class MWidget(QMainWindow, Styles):
    log = logging.getLogger("MW4")
    FULL_WIDTH = 800
    FULL_HEIGHT = 620
    HALF_WIDTH = 400
    HALF_HEIGHT = 310
    POPUP_HEIGHT = 150
    RESIZE_MARGIN = 8
    CURSOR_MAP: ClassVar[dict[Qt.Edge, Qt.CursorShape]] = {
        Qt.Edge.BottomEdge | Qt.Edge.RightEdge: Qt.CursorShape.SizeFDiagCursor,
        Qt.Edge.RightEdge: Qt.CursorShape.SizeHorCursor,
        Qt.Edge.BottomEdge: Qt.CursorShape.SizeVerCursor,
    }

    def __init__(self) -> None:
        super().__init__()
        self.cursorHasResizeShape: bool = False
        self.setWindowIcon(self.mwIcon)
        self.setStyleSheet(self.mw4Style)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.titleBar = CustomTitleBar(self)
        self.isResizing = False
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
        self.installEventFilter(self)
        centralWidget.installEventFilter(self)
        centralWidget.setMouseTracking(True)
        centralWidget.raise_()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.WindowStateChange:
            self.titleBar.windowStateChanged(self.windowState())
        super().changeEvent(event)
        event.accept()

    def eventFilter(self, watched, event) -> bool:
        etype = event.type()
        if etype in (QEvent.Type.Leave, QEvent.Type.HoverLeave):
            self.unsetCursor()
            return False
        if etype in (
            QEvent.Type.MouseMove,
            QEvent.Type.HoverMove,
            QEvent.Type.MouseButtonPress,
        ):
            localPos = self.mapFromGlobal(event.globalPosition().toPoint())
            edges = self.getEdges(localPos)
            if (
                etype == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
                and edges
            ):
                self.windowHandle().startSystemResize(edges)
                return True
            if self.rect().contains(localPos):
                self.setResizeCursorShape(edges)
        return super().eventFilter(watched, event)

    def getEdges(self, pos: QPoint) -> Qt.Edge:
        edges = Qt.Edge(0)
        if pos.x() >= self.width() - self.RESIZE_MARGIN:
            edges |= Qt.Edge.RightEdge
        if pos.y() >= self.height() - self.RESIZE_MARGIN:
            edges |= Qt.Edge.BottomEdge
        return edges

    def setResizeCursorShape(self, edges: Qt.Edge) -> None:
        shape = self.CURSOR_MAP.get(edges)
        if shape is None:
            if self.cursorHasResizeShape:
                self.cursorHasResizeShape = False
                self.unsetCursor()
            return
        self.cursorHasResizeShape = True
        self.setCursor(shape)

    def setWindowTitle(self, title: str) -> None:
        if hasattr(self, "titleBar"):
            self.titleBar.title.setText(title)

    @staticmethod
    def setNoFocus(ui) -> None:
        for widget in ui.findChildren(QWidget):
            if not isinstance(widget, (QLineEdit, QComboBox)):
                widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

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
        for windowKey in windows:
            if windows[windowKey]["classObj"]:
                self.saveWindowAsPNG(windows[windowKey]["classObj"])

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

    def setPositionWindow(self, config: dict) -> None:
        height = config.get("height", self.minimumHeight())
        width = config.get("width", self.minimumWidth())
        if height == self.maximumHeight() and width == self.maximumWidth():
            if platform.system() not in ["Linux", "Windows"]:
                self.setWindowState(Qt.WindowState.WindowMaximized)
            else:
                self.setWindowState(Qt.WindowState.WindowNoState)
        self.resize(width, height)
        geo = QGuiApplication.primaryScreen().availableGeometry()
        x = config.get("winPosX", geo.width() // 2 - width // 2)
        y = config.get("winPosY", geo.height() // 2 - height // 2)
        self.move(x, y)

    def getPositionWindow(self, config: dict[str, int]) -> dict[str, int]:
        config["winPosX"] = self.pos().x()
        config["winPosY"] = self.pos().y()
        config["height"] = self.frameGeometry().height()
        config["width"] = self.frameGeometry().width()
        return config
