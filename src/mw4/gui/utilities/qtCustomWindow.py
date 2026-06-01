from PySide6.QtCore import QPoint, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QWidget


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.initial_pos: QPoint | None = None

        titleBarLayout = QHBoxLayout(self)
        titleFrame = QFrame()
        titleFrame.setProperty("title", True)
        titleFrame.setFixedHeight(31)
        frameLayout = QHBoxLayout(titleFrame)
        frameLayout.setContentsMargins(0, 0, 0, 0)
        self.title = QLabel()
        self.title.setProperty("title", True)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frameLayout.addWidget(self.title)

        # Min button
        self.min_button = QToolButton(self)
        pm = QPixmap(20, 20)
        pm.fill(QColor("yellow"))
        min_icon = QIcon(pm)
        self.min_button.setIcon(min_icon)
        self.min_button.clicked.connect(self.window().showMinimized)

        # Max button
        self.max_button = QToolButton(self)
        pm = QPixmap(20, 20)
        pm.fill(QColor("green"))
        max_icon = QIcon(pm)
        self.max_button.setIcon(max_icon)
        self.max_button.clicked.connect(self.window().showMaximized)

        # Close button
        self.close_button = QToolButton(self)
        pm = QPixmap(20, 20)
        pm.fill(QColor("red"))
        close_icon = QIcon(pm)
        self.close_button.setIcon(close_icon)
        self.close_button.clicked.connect(self.window().close)

        # Normal button
        self.normal_button = QToolButton(self)
        pm = QPixmap(20, 20)
        pm.fill(QColor("white"))
        normal_icon = QIcon(pm)
        self.normal_button.setIcon(normal_icon)
        self.normal_button.clicked.connect(self.window().showNormal)
        self.normal_button.setVisible(False)
        # Add buttons
        buttons = [
            self.min_button,
            self.normal_button,
            self.max_button,
            self.close_button,
        ]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(20, 20))
            button.setStyleSheet(
                """QToolButton {
                        border: none;
                        padding: 2px;
                    }
                """
            )
            frameLayout.addWidget(button)
            titleBarLayout.addWidget(titleFrame)
            titleBarLayout.setContentsMargins(0, 0, 8, 0)
            titleBarLayout.setSpacing(5)

    def windowStateChanged(self, state):
        if state == Qt.WindowState.WindowMaximized:
            self.normal_button.setVisible(True)
            self.max_button.setVisible(False)
        else:
            self.normal_button.setVisible(False)
            self.max_button.setVisible(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.position().toPoint()
        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.initial_pos is not None:
            delta = event.position().toPoint() - self.initial_pos
            self.window().move(
                self.window().x() + delta.x(),
                self.window().y() + delta.y(),
            )
        super().mouseMoveEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event):
        self.initial_pos = None
        super().mouseReleaseEvent(event)
        event.accept()
