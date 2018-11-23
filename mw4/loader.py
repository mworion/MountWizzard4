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
import logging.config
import os
import sys
import platform
import socket
import datetime
import warnings
import traceback
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
# local import
from mw4 import mainApp
from mw4.gui.media import resources


class SplashScreen(PyQt5.QtCore.QObject):
    """
    Splash screen show an icon with a progress bar and could send messages to the text
    set in the progress bar. Need the app and the icon as parameter

    Part from Maurizio D'Addona <mauritiusdadd@gmail.com> under license APL2.0
    Ported from PYQT4 to PYQT5
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

    def __init__(self, pix=None, qapp=None):
        super().__init__()
        self._qapp = qapp
        self._pxm = pix
        flags = (PyQt5.QtCore.Qt.WindowStaysOnTopHint
                 | PyQt5.QtCore.Qt.X11BypassWindowManagerHint)
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


def except_hook(typeException, valueException, tbackException):
    """
    except_hook implements a wrapper around except hook to log uncatched exceptions to the
    log file. so during user phase I get all the exceptions and logs catched in the file.

    :param typeException:
    :param valueException:
    :param tbackException:
    :return: nothing
    """

    result = traceback.format_exception(typeException, valueException, tbackException)
    logging.error('----------------------------------------------------')
    logging.error('Logging an uncatched Exception')
    logging.error('----------------------------------------------------')
    for i in range(0, len(result)):
        logging.error(result[i].replace('\n', ''))
    logging.error('----------------------------------------------------')
    sys.__excepthook__(typeException, valueException, tbackException)


def main():
    """
    main prepares the loading of mountwizzard application. it prepares a splash screen
    and handler the setup of the logger, bundle handling etc. in addition some information
    about the system are written into the logfile to be able to debug in different conditions
    the system environment.

    :return: nothing
    """

    # defining system wide definitions:
    mwGlob = {
        'build': '0.1dev0',
        'frozen': False,
        'bundleDir': '',
        'workDir': '',
        'configDir': '',
        'dataDir': '',
        'imageDir': '',
    }

    # checking workdir and if the system is started from frozen app
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        # noinspection PyProtectedMember
        mwGlob['bundleDir'] = sys._MEIPASS
        # on mac we have to change path of working directory
        if platform.system() == 'Darwin':
            os.chdir(os.path.dirname(sys.executable))
            os.chdir('..')
            os.chdir('..')
            os.chdir('..')
            mwGlob['frozen'] = True
    else:
        # we are running in a normal Python environment
        mwGlob['bundleDir'] = os.path.dirname(os.path.abspath(__file__))
        mwGlob['frozen'] = False

    # now instantiate the application from QApplication
    PyQt5.QtWidgets.QApplication.setAttribute(PyQt5.QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    # setting a splash pixel map for loading
    splash_pix = PyQt5.QtGui.QPixmap(':/mw4.ico')
    splash = SplashScreen(pix=splash_pix, qapp=app)

    # and start with a first splash screen
    splash.showMessage('Start initialising')
    splash.setValue(0)
    # setting work dir:
    mwGlob['workDir'] = os.getcwd()
    mwGlob['configDir'] = os.getcwd() + '/config'
    mwGlob['dataDir'] = os.getcwd() + '/data'
    mwGlob['imageDir'] = os.getcwd() + '/image'
    # now setup the logging environment
    splash.showMessage('Setup logging')
    splash.setValue(20)
    warnings.filterwarnings("ignore")
    name = 'mw4-{0}.log'.format(datetime.datetime.now().strftime("%Y-%m-%d"))
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s.%(msecs)03d]'
                               '[%(levelname)7s]'
                               '[%(filename)15s]'
                               '[%(lineno)5s]'
                               '[%(funcName)20s]'
                               '[%(threadName)10s]'
                               ' > %(message)s',
                        handlers=[logging.FileHandler(name)],
                        datefmt='%Y-%m-%d %H:%M:%S',
                        )

    # setting different log level for imported packages to avoid unnecessary data
    logging.getLogger('PyQt5').setLevel(logging.ERROR)
    logging.getLogger('requests').setLevel(logging.ERROR)
    logging.getLogger('matplotlib').setLevel(logging.ERROR)
    # urllib3 is used by requests, so we have to add this as well
    logging.getLogger('urllib3').setLevel(logging.ERROR)

    # population the working directory with necessary subdir
    splash.showMessage('Checking work directories')
    splash.setValue(30)
    if not os.path.isdir(mwGlob['workDir']):
        os.makedirs(mwGlob['workDir'])
    if not os.access(mwGlob['workDir'], os.W_OK):
        logging.error('no write access to workdir')

    if not os.path.isdir(mwGlob['configDir']):
        os.makedirs(mwGlob['configDir'])
    if not os.access(mwGlob['configDir'], os.W_OK):
        logging.error('no write access to /config')

    if not os.path.isdir(mwGlob['dataDir']):
        os.makedirs(mwGlob['dataDir'])
    if not os.access(mwGlob['dataDir'], os.W_OK):
        logging.error('no write access to /data')

    if not os.path.isdir(mwGlob['imageDir']):
        os.makedirs(mwGlob['imageDir'])
    if not os.access(mwGlob['imageDir'], os.W_OK):
        logging.error('no write access to /image')

    # start logging with basic system data for information
    splash.showMessage('Logging environment')
    splash.setValue(40)
    logging.info('------------------------------------------------------------------------')
    logging.info('')
    logging.info('MountWizzard {0} started !'.format(mwGlob['build']))
    logging.info('')
    logging.info('------------------------------------------------------------------------')
    logging.info('Platform         : {0}'.format(platform.system()))
    logging.info('Release          : {0}'.format(platform.release()))
    logging.info('Machine          : {0}'.format(platform.machine()))
    logging.info('CPU              : {0}'.format(platform.processor()))
    logging.info('Python           : {0}'.format(platform.python_version()))
    logging.info('PyQt5            : {0}'.format(PyQt5.QtCore.PYQT_VERSION_STR))
    logging.info('Qt               : {0}'.format(PyQt5.QtCore.QT_VERSION_STR))
    logging.info('Node             : {0}'.format(platform.node()))

    # in some environments I don't get a fully qualified host name
    try:
        hostSummary = socket.gethostbyname_ex(socket.gethostname())
    except socket.herror:
        logging.warning('Could not read properly host configuration')
    except socket.gaierror:
        logging.warning('Could not read properly host configuration')
    else:
        hostsList = hostSummary[2]
        host = [ip for ip in hostsList if not ip.startswith('127.')][: 1]
        for hostname in host:
            logging.info('IP addr.         : {0}'.format(hostname))
        logging.info('Hosts            : {0}'.format(hostSummary))

    logging.info('Environment is   : {0}'.format('frozen' if mwGlob['frozen'] else 'live'))
    logging.info('Actual workdir   : {0}'.format(mwGlob['workDir']))
    logging.info('Bundle dir       : {0}'.format(mwGlob['bundleDir']))
    logging.info('sys.argv[0]      : {0}'.format(sys.argv[0]))
    logging.info('os.path.basename : {0}'.format(os.path.basename(sys.argv[0])))
    logging.info('sys.executable   : {0}'.format(sys.executable))

    logging.info('------------------------------------------------------------------------')
    logging.info('')

    # and finally starting the application
    splash.showMessage('Preparing application')
    splash.setValue(60)
    sys.excepthook = except_hook
    app.setWindowIcon(PyQt5.QtGui.QIcon(':/mw4.ico'))
    mountApp = mainApp.MountWizzard4(mwGlob)
    mountApp.mainW.show()

    # end of splash screen
    splash.showMessage('Finishing loading')
    splash.setValue(100)
    splash.close()

    # quit app
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
