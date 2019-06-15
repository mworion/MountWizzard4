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
# Python  v3.7.3
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
from PyQt5.QtCore import Qt
import numpy as np
# local import
from mw4.gui.media import resources


class SplashScreen(PyQt5.QtCore.QObject):
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

    __all__ = ['SplashScreen',
               'close',
               'setValue',
               'showMessage',
               'finish',
               ]

    def __init__(self, application=None):
        super().__init__()
        self._qapp = application
        self._pxm = PyQt5.QtGui.QPixmap(':/mw4.ico')

        flags = (Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        self._qss = PyQt5.QtWidgets.QSplashScreen(self._pxm, flags)
        self._msg = ''
        self._maxv = 100.0
        self._minv = 0.0
        self._cval = 0.0
        self._qss.__drawContents__ = self._qss.drawContents
        self._qss.drawContents = self._drawContents
        self._qss.show()
        self._qss.raise_()
        self.processEvents()

    def close(self):
        self.update()
        self._qss.close()

    def setValue(self, val):
        for i in np.arange(self._cval, val, self._maxv / 5.0):
            self._cval = i
            self.update()

    def showMessage(self, msg):
        self._msg = msg
        self.update()

    def update(self):
        self._qss.update()
        self.processEvents()

    def _drawContents(self, painter):
        view_port = painter.viewport()
        w = view_port.right()
        h = view_port.bottom()

        painter.setPen(PyQt5.QtGui.QColor(55, 55, 55, 255))
        painter.setBrush(PyQt5.QtGui.QColor(0, 0, 0, 255))
        painter.drawRect(10, h - 64, w - 20, 19)

        redlg = PyQt5.QtGui.QLinearGradient(0, h - 63, 0, h)
        redlg.setColorAt(0.3, PyQt5.QtGui.QColor(8, 36, 48))
        redlg.setColorAt(0, PyQt5.QtGui.QColor(32, 144, 192))

        painter.setPen(PyQt5.QtCore.Qt.NoPen)
        painter.setBrush(redlg)
        painter.drawRect(13, h - 61, (w - 24) * self._cval / self._maxv, 14)

        painter.setPen(PyQt5.QtCore.Qt.white)

        rect = PyQt5.QtCore.QRectF(10, h - 61, w - 20, 15)
        painter.drawText(rect, PyQt5.QtCore.Qt.AlignCenter, str(self._msg))

    def finish(self, qwid):
        self._qss.finish(qwid)

    def processEvents(self):
        if self._qapp is not None:
            self._qapp.processEvents()
