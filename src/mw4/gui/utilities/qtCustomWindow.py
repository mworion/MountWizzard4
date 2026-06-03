from mw4.gui.utilities.qtHelpers import svg2icon
from PySide6.QtCore import QPoint, QSize, Qt
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
        titleFrame.setFixedHeight(30)
        titleFrame.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        frameLayout = QHBoxLayout(titleFrame)
        frameLayout.setContentsMargins(0, 0, 0, 0)
        self.title = QLabel()
        self.title.setProperty("title", True)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frameLayout.addWidget(self.title)

        buttons = {
            "min": {
                "widget": self.minButton,
                "icon": "min.svg",
                "func": self.window().showMinimized,
                "col": "#D0D000",
            },
            "max": {
                "widget": self.maxButton,
                "icon": "max.svg",
                "func": self.window().showMaximized,
                "col": "#00C000",
            },
            "norm": {
                "widget": self.normButton,
                "icon": "norm.svg",
                "func": self.window().showNormal,
                "col": "#00C000",
            },
            "close": {
                "widget": self.closeButton,
                "icon": "close.svg",
                "func": self.window().close,
                "col": "#D03030",
            },
        }

        for button in buttons:
            buttons[button]["widget"].setIcon(
                svg2icon(f"assets/icon/{buttons[button]['icon']}", "black")
            )
            buttons[button]["widget"].setFixedSize(QSize(16, 16))
            buttons[button]["widget"].setFocusPolicy(Qt.FocusPolicy.NoFocus)
            buttons[button]["widget"].clicked.connect(buttons[button]["func"])
            style = f"border: none; padding: 2px; background-color: {buttons[button]['col']};"
            buttons[button]["widget"].setStyleSheet(style)
            frameLayout.addWidget(buttons[button]["widget"])

        titleBarLayout.addWidget(titleFrame)
        titleBarLayout.setContentsMargins(10, 0, 10, 0)

    def windowStateChanged(self, state) -> None:
        if state == Qt.WindowState.WindowMaximized:
            self.normButton.setVisible(True)
            self.maxButton.setVisible(False)
        else:
            self.normButton.setVisible(False)
            self.maxButton.setVisible(True)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.initialPos = event.position().toPoint()
        super().mousePressEvent(event)
        event.accept()

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
