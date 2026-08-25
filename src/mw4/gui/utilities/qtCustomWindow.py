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
from collections.abc import Callable
from dataclasses import dataclass
from mw4.gui.utilities.qtHelpers import svg2icon
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QWidget


@dataclass
class TitleButton:
    widget: QToolButton
    icon: str
    func: Callable
    prop: str


class CustomTitleBar(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.windowFixed: bool = False
        self.minButton: QToolButton = QToolButton(self)
        self.maxButton: QToolButton = QToolButton(self)
        self.closeButton: QToolButton = QToolButton(self)
        self.normButton: QToolButton = QToolButton(self)
        self.normButton.setVisible(False)
        titleBarLayout = QHBoxLayout(self)
        titleBarLayout.setContentsMargins(0, 0, 0, 0)
        titleFrame = QFrame()
        titleFrame.setProperty("title", True)
        titleFrame.setFixedHeight(25)
        titleFrame.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        frameLayout = QHBoxLayout(titleFrame)
        frameLayout.setContentsMargins(60, 0, 10, 0)
        self.title = QLabel()
        self.title.setProperty("title", True)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frameLayout.addWidget(self.title)

        for button in self.buildButtons():
            button.widget.setIcon(svg2icon(f"assets/icon/{button.icon}", [0, 0, 0, 255]))
            button.widget.setFixedSize(QSize(16, 16))
            button.widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.widget.clicked.connect(button.func)
            button.widget.setProperty(button.prop, True)
            frameLayout.addWidget(button.widget)

        titleBarLayout.addWidget(titleFrame)
        titleBarLayout.setContentsMargins(4, 4, 4, 5)

    def buildButtons(self) -> list[TitleButton]:
        return [
            TitleButton(self.minButton, "min.svg", self.window().showMinimized, "min"),
            TitleButton(self.maxButton, "max.svg", self.window().showMaximized, "max"),
            TitleButton(self.normButton, "norm.svg", self.window().showNormal, "norm"),
            TitleButton(self.closeButton, "close.svg", self.window().close, "close"),
        ]

    def windowStateChanged(self, state: Qt.WindowState) -> None:
        if self.windowFixed:
            self.maxButton.setVisible(False)
            self.normButton.setVisible(False)
            return
        if state == Qt.WindowState.WindowMaximized:
            self.normButton.setVisible(True)
            self.maxButton.setVisible(False)
        else:
            self.normButton.setVisible(False)
            self.maxButton.setVisible(True)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            if window and window.windowHandle():
                event.accept()
                QTimer.singleShot(0, window.windowHandle().startSystemMove)
