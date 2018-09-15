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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import os
import sys
import platform
import socket
import datetime
import warnings
import numpy as np
# external packages
import PyQt5
import PyQt5.QtCore
import PyQt5.QtWidgets
import skyfield.api
import mountcontrol
# local import
from base import widget
from media import resources


BUILD = '0.1.dev0'


class MountWizzard4(widget.MwWidget):
    logger = logging.getLogger(__name__)


class SplashScreen(PyQt5.QtCore.QObject):

    # Part from Maurizio D'Addona <mauritiusdadd@gmail.com> under license APL2.0
    # Ported from PYQT4 to PYQT5
    # Agreement for License (email from 04.07.2018):
    # Hi Michel,
    # sure, there is no problem for me. I'm glad you have found it useful.
    # Best regards,
    # Maurizio

    def __init__(self, pix, qapp=None):
        super().__init__()
        self._qapp = qapp
        self._pxm = pix
        self._qss = PyQt5.QtWidgets.QSplashScreen(self._pxm,
                                                  (PyQt5.QtCore.Qt.WindowStaysOnTopHint
                                                   | PyQt5.QtCore.Qt.X11BypassWindowManagerHint))

        self._msg = ''
        self._maxv = 100.0
        self._minv = 0.0
        self._cval = 0.0

        self._qss.__drawContents__ = self._qss.drawContents
        self._qss.drawContents = self._drawContents

        self._qss.show()

        self.processEvents()

    def close(self):
        self.update()
        self._qss.close()

    def setMaximum(self, val):
        self._maxv = val
        self.update()

    def setMinimum(self, val):
        self._minv = val
        self.update()

    def setValue(self, val):
        for i in np.arange(self._cval, val, self._maxv / 100.0):
            self._cval = i
            self.update()

    def maximum(self):
        return self._maxv

    def minimum(self):
        return self._minv

    def value(self):
        return self._cval

    def message(self):
        return self._msg

    def showMessage(self, msg):
        self._msg = msg
        # self._qss.showMessage(msg,QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeft,QtCore.Qt.white)
        self.update()

    def update(self):
        self._qss.update()
        self.processEvents()

    def _drawContents(self, painter):
        # self._qss.__drawContents__(painter)

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


# setting except hook to get stack traces into the log files
def except_hook(typeException, valueException, tbackException):
    result = traceback.format_exception(typeException, valueException, tbackException)
    logging.error('----------------------------------------------------------------------------------')
    logging.error('Logging an uncatched Exception')
    logging.error('----------------------------------------------------------------------------------')
    for i in range(0, len(result)):
        logging.error(result[i].replace('\n', ''))
    logging.error('----------------------------------------------------------------------------------')
    sys.__excepthook__(typeException, valueException, tbackException)


def main():
    # checking workdir and if the system is started from frozen app
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        # noinspection PyProtectedMember
        bundle_dir = sys._MEIPASS
        # on mac we have to change path of working directory
        if platform.system() == 'Darwin':
            os.chdir(os.path.dirname(sys.executable))
            os.chdir('..')
            os.chdir('..')
            os.chdir('..')
        frozen = True
    else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
        frozen = False

    # implement notify different to catch exception from event handler
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    splash_pix = PyQt5.QtGui.QPixmap(':/mw4.ico')
    splash = SplashScreen(splash_pix, app)
    splash.showMessage('Start initialising')
    splash.setValue(10)

    warnings.filterwarnings("ignore")
    name = 'mount.{0}.log'.format(datetime.datetime.now().strftime("%Y-%m-%d"))
    handler = logging.FileHandler(name)
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s.%(msecs)03d]'
                               '[%(levelname)7s]'
                               '[%(filename)22s]'
                               '[%(lineno)5s]'
                               '[%(funcName)20s]'
                               '[%(threadName)10s] - %(message)s',
                        handlers=[handler],
                        datefmt='%Y-%m-%d %H:%M:%S',
                        )
    splash.showMessage('Checking work directories')
    splash.setValue(20)

    # population the working directory with necessary subdir

    if not os.path.isdir(os.getcwd() + '/config'):
        os.makedirs(os.getcwd() + '/config')

    splash.showMessage('Starting logging')
    splash.setValue(30)

    # start logging with basic system data for information
    hostSummary = socket.gethostbyname_ex(socket.gethostname())
    logging.info('------------------------------------------------------------------------')
    logging.info('')
    logging.info('MountWizzard ' + BUILD + ' started !')
    logging.info('')
    logging.info('------------------------------------------------------------------------')
    logging.info('Platform        : ' + platform.system())
    logging.info('Release         : ' + platform.release())
    logging.info('Version         : ' + platform.version())
    logging.info('Machine         : ' + platform.machine())
    logging.info('CPU             : ' + platform.processor())
    logging.info('Python          : ' + platform.python_version())
    logging.info('PyQt5           : ' + PyQt5.QtCore.PYQT_VERSION_STR)
    logging.info('Qt              : ' + PyQt5.QtCore.QT_VERSION_STR)
    host = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith('127.')][: 1]
    for i in range(0, len(host)):
        logging.info('IP addr. : ' + host[i])
    logging.info('Node            : ' + platform.node())
    logging.info('Hosts....       : {0}'.format(hostSummary))
    if frozen:
        logging.info('MountWizzard3 is running in a frozen environment')
    else:
        logging.info('MountWizzard3 is running in a live environment')
    logging.info('Actual workdir  : {0}'.format(os.getcwd()))
    logging.info('Bundle dir      : {0}'.format(bundle_dir))
    logging.info('sys.argv[0]     : {0}'.format(sys.argv[0]))
    logging.info('sys.executable  : {0}'.format(sys.executable))
    logging.info('os.path.basename: {0}'.format(os.path.basename(sys.argv[0])))

    logging.info('------------------------------------------------------------------------')
    logging.info('')

    splash.showMessage('Checking work directories')
    splash.setValue(40)

    # checking if writable
    if not os.access(os.getcwd(), os.W_OK):
        logging.error('no write access to workdir')
    if not os.access(os.getcwd() + '/config', os.W_OK):
        logging.error('no write access to /config')

    splash.showMessage('Preparing application')
    splash.setValue(50)

    # and finally starting the application
    sys.excepthook = except_hook
    app.setWindowIcon(PyQt5.QtGui.QIcon('mw.ico'))
    mountApp = MountWizzard4()

    splash.showMessage('Launching GUI')
    splash.setValue(80)

    mountApp.show()

    # end of splash screen
    splash.showMessage('Finishing loading')
    splash.setValue(100)
    splash.close()
    # quit app
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
