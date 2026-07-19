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
from mw4.gui.utilities.qtHelpers import svg2icon
from PySide6.QtCore import QPoint, QSize, Qt, QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QWidget


class CustomTitleBar(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.windowFixed: bool = False
        self.minButton: QToolButton = QToolButton(self)
        self.maxButton: QToolButton = QToolButton(self)
        self.closeButton: QToolButton = QToolButton(self)
        self.normButton: QToolButton = QToolButton(self)
        self.normButton.setVisible(False)
        self.initialPos: QPoint | None = None
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

        buttons = {
            "min": {
                "widget": self.minButton,
                "icon": "min.svg",
                "func": self.window().showMinimized,
            },
            "max": {
                "widget": self.maxButton,
                "icon": "max.svg",
                "func": self.window().showMaximized,
            },
            "norm": {
                "widget": self.normButton,
                "icon": "norm.svg",
                "func": self.window().showNormal,
            },
            "close": {
                "widget": self.closeButton,
                "icon": "close.svg",
                "func": self.window().close,
            },
        }
        for button in buttons:
            buttons[button]["widget"].setIcon(
                svg2icon(f"assets/icon/{buttons[button]['icon']}", [0, 0, 0, 255])
            )
            buttons[button]["widget"].setFixedSize(QSize(16, 16))
            buttons[button]["widget"].setFocusPolicy(Qt.FocusPolicy.NoFocus)
            buttons[button]["widget"].clicked.connect(buttons[button]["func"])
            buttons[button]["widget"].setProperty(button, True)
            frameLayout.addWidget(buttons[button]["widget"])

        titleBarLayout.addWidget(titleFrame)
        titleBarLayout.setContentsMargins(4, 4, 4, 5)

    def windowStateChanged(self, state) -> None:
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
                return

    def mouseMoveEvent(self, event) -> None:
        if self.initialPos is not None:
            delta = event.position().toPoint() - self.initialPos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        super().mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self.initialPos = None
        super().mouseReleaseEvent(event)
        event.accept()
