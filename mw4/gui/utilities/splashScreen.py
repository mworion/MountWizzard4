############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import numpy as np
from PyQt5.QtCore import QObject, Qt, QRectF
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QSplashScreen

# local import


class SplashScreen(QObject):
    """
    Splash screen show an icon with a progress bar and could send messages to the text
    set in the progress bar. Need the app and the icon as parameter

    Part from Maurizio D'Addona <mauritiusdadd@gmail.com> under license APL2.0
    Ported from PyQt4 to PyQt5

    Agreement for License (email from 04.07.2018):
    Hi Michel,
    sure, there is no problem for me. I'm glad you have found it useful.
    Best regards,
    Maurizio
    """

    __all__ = ['SplashScreen']

    def __init__(self, application=None, x=0, y=0):
        super().__init__()

        self._qapp = application
        self.x = x
        self.y = y
        self._pxm = QPixmap(':/icon/mw4.png')

        flags = (Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        self.qss = QSplashScreen(self._pxm, flags)
        h = self.qss.height()
        w = self.qss.width()
        if x != 0 and y != 0:
            self.qss.move(int(x + (800 - w) / 2), int(y + (600 - h) / 2))
        self.msg = ''
        self.maxv = 100.0
        self.minv = 0.0
        self.cval = 0.0
        self.qss.__drawContents__ = self.qss.drawContents
        self.qss.drawContents = self.drawContents
        self.qss.show()
        self.qss.raise_()
        QApplication.processEvents()

    def close(self):
        self.update()
        self.qss.close()

    def setValue(self, val):
        for i in np.arange(self.cval, val, self.maxv / 5.0):
            self.cval = i
            self.update()

    def showMessage(self, msg):
        self.msg = msg
        self.update()

    def update(self):
        self.qss.update()
        QApplication.processEvents()

    def drawContents(self, painter):
        view_port = painter.viewport()
        w = view_port.right()
        h = view_port.bottom()

        painter.setPen(QColor(43, 192, 255))
        painter.setBrush(QColor(0, 0, 0, 128))
        painter.drawRect(10, h - 64, w - 20, 19)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(32, 144, 192, 128))
        painter.drawRect(13, h - 61, int((w - 24) * self.cval / self.maxv), 14)

        painter.setPen(Qt.white)
        rect = QRectF(10, h - 61, w - 20, 15)
        painter.drawText(rect, Qt.AlignCenter, str(self.msg))
        painter.setPen(QColor(43, 192, 255))
        painter.drawLine(0, 0, w, 0)
        painter.drawLine(0, h, 0, 0)
        painter.setPen(QColor(32, 144, 192))
        painter.drawLine(w, 0, w, h)
        painter.drawLine(w, h, 0, h)

    def finish(self, qwid):
        self.qss.finish(qwid)
