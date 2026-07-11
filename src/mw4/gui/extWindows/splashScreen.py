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
"""Splash screen with progress bar shown during application startup."""

from importlib.resources import as_file, files
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen, QWidget


class SplashScreen:
    """
    Splash screen shows an icon with a progress bar and could send messages to the text
    set in the progress bar. Need the app and the icon as parameter

    Part from Maurizio D'Addona <mauritiusdadd@gmail.com> under license APL2.0
    Ported from PyQt4 to PySide6

    Agreement for License (email from 04.07.2018):
    Hi Michel,
    sure, there is no problem for me. I'm glad you have found it useful.
    Best regards,
    Maurizio
    """

    def __init__(self, application: QApplication | None = None) -> None:
        self._qapp = application
        with as_file(files("mw4").joinpath("assets/icon/mw4.png")) as imageFile:
            self._pxm = QPixmap(str(imageFile))

        flags = Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.X11BypassWindowManagerHint
        self.qss = QSplashScreen(self._pxm, flags)
        self.msg = ""
        self.maxv = 100.0
        self.minv = 0.0
        self.cval = 0.0
        self.qss.drawContents = self.drawContents
        self.qss.show()
        self.qss.raise_()
        QApplication.processEvents()

    def close(self) -> None:
        self.update()
        self.qss.close()

    def setValue(self, val: float) -> None:
        step = self.maxv / 5.0
        v = self.cval
        while v < val:
            self.cval = v
            self.update()
            v += step
        self.cval = val
        self.update()

    def showMessage(self, msg: str) -> None:
        self.msg = msg
        self.update()

    def update(self) -> None:
        self.qss.update()
        QApplication.processEvents()

    def drawContents(self, painter: QPainter) -> None:
        viewPort = painter.viewport()
        w = viewPort.right()
        h = viewPort.bottom()

        painter.setPen(QColor(43, 192, 255, 255))
        painter.setBrush(QColor(0, 0, 0, 128))
        painter.drawRect(10, h - 64, w - 20, 19)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(32, 144, 192, 128))
        painter.drawRect(13, h - 61, int((w - 24) * self.cval / self.maxv), 14)

        painter.setPen(Qt.GlobalColor.white)
        rect = QRectF(10, h - 61, w - 20, 15)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(self.msg))
        painter.setPen(QColor(43, 192, 255, 255))
        painter.drawLine(0, 0, w, 0)
        painter.drawLine(0, h, 0, 0)
        painter.setPen(QColor(32, 144, 192, 255))
        painter.drawLine(w, 0, w, h)
        painter.drawLine(w, h, 0, h)

    def finish(self, qwid: QWidget) -> None:
        self.qss.finish(qwid)
