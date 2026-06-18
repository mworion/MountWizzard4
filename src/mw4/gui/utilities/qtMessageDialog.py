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
from mw4.gui.utilities.qtHelpers import svg2pixmap
from mw4.gui.utilities.qtMain import MWidget
from PySide6.QtCore import QEventLoop, Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MWMessageDialog(MWidget):
    """
    Lightweight, themed message dialog built on top of the frameless
    :class:`MWidget`. Provides the small subset of features MW4 actually
    needs: a title, a question/text body, an icon (question, information,
    warning) and either default Yes/No buttons or a list of custom button
    labels.

    Like :class:`MWFileDialog`, the dialog is not a :class:`QDialog` –
    :meth:`exec` runs a local :class:`QEventLoop` so the call site can stay
    synchronous, mirroring Qt's own ``QDialog.exec()`` semantics.
    """

    Rejected = -1
    NoIndex = 0
    YesIndex = 1

    ICONS = (
        "assets/icon/question.svg",
        "assets/icon/information.svg",
        "assets/icon/warning.svg",
        "assets/icon/question.svg",
    )

    def __init__(
        self,
        parent: QWidget | None = None,
        title: str = "",
        question: str = "",
        buttons: list[str] | None = None,
        iconType: int = 0,
    ) -> None:
        super().__init__()
        self.useStandardButtons: bool = not buttons
        self.resultCode: int = self.Rejected
        self.eventLoop = QEventLoop()
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)


        iconLabel = QLabel()
        iconLabel.setFixedSize(72, 72)
        iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        iconIndex = iconType if 0 <= iconType < len(self.ICONS) else 0
        pixmap = svg2pixmap(self.ICONS[iconIndex], self.M_PRIM).scaled(64, 64)
        iconLabel.setPixmap(pixmap)

        self.textLabel = QLabel(question)
        self.textLabel.setWordWrap(True)
        self.textLabel.setTextFormat(Qt.TextFormat.AutoText)
        self.textLabel.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        topRow = QHBoxLayout()
        topRow.addWidget(iconLabel)
        topRow.addWidget(self.textLabel, 1)

        buttonRow = QHBoxLayout()
        buttonRow.addStretch(1)
        self.buttonWidgets: list[QPushButton] = []
        if self.useStandardButtons:
            self.buttonNo = QPushButton("No")
            self.buttonNo.clicked.connect(lambda: self.onClick(self.NoIndex))
            self.buttonYes = QPushButton("Yes")
            self.buttonYes.setMinimumSize(80, 25)
            self.buttonYes.clicked.connect(lambda: self.onClick(self.YesIndex))
            self.buttonNo.setDefault(True)
            self.buttonNo.setMinimumSize(80, 25)
            self.buttonNo.setFocus()
            buttonRow.addWidget(self.buttonNo)
            buttonRow.addWidget(self.buttonYes)
            self.buttonWidgets.extend([self.buttonNo, self.buttonYes])
        else:
            for index, label in enumerate(buttons or []):
                btn = QPushButton(label)
                btn.clicked.connect(lambda _checked=False, idx=index: self.onClick(idx))
                buttonRow.addWidget(btn)
                self.buttonWidgets.append(btn)

        contentLayout = QVBoxLayout(self.ws)
        contentLayout.setContentsMargins(12, 12, 12, 12)
        contentLayout.addLayout(topRow, 1)
        contentLayout.addLayout(buttonRow)

        self.adjustSize()
        if parent is not None:
            self.move(
                parent.x() + max(0, (parent.width() - self.width()) // 2),
                parent.y() + max(0, (parent.height() - self.height()) // 2),
            )

    def onClick(self, value: int) -> None:
        self.resultCode = value
        self.finishLoop()
        self.close()

    def finishLoop(self) -> None:
        if self.eventLoop.isRunning():
            self.eventLoop.quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.eventLoop.isRunning():
            self.resultCode = self.Rejected
            self.eventLoop.quit()
        super().closeEvent(event)

    def exec(self) -> int:
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.show()
        self.setMinimumSize(400, 200)
        self.setMaximumSize(400, 200)
        self.titleBar.normButton.setVisible(False)
        self.titleBar.maxButton.setVisible(False)
        self.titleBar.minButton.setVisible(False)
        self.titleBar.windowFixed = True
        self.eventLoop.exec()
        return self.resultCode

    @classmethod
    def question(
        cls,
        parent: QWidget | None,
        title: str,
        question: str,
        buttons: list[str] | None = None,
        iconType: int = 0,
    ) -> bool | int:
        dlg = cls(
            parent=parent,
            title=title,
            question=question,
            buttons=buttons,
            iconType=iconType,
        )
        result = dlg.exec()
        if not buttons:
            return result == cls.YesIndex
        return result
