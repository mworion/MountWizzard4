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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
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
import traceback
import locale
import html
from io import BytesIO
# external packages
import matplotlib
matplotlib.use('Qt5Agg')
import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets
# local import
from mw4 import mainApp
from mw4.gui import splash
import mw4.resource


class QAwesomeTooltipEventFilter(PyQt5.QtCore.QObject):
    """
    Tooltip-specific event filter dramatically improving the tooltips of all
    widgets for which this filter is installed.

    Motivation
    ----------
    **Rich text tooltips** (i.e., tooltips containing one or more HTML-like
    tags) are implicitly wrapped by Qt to the width of their parent windows and
    hence typically behave as expected.

    **Plaintext tooltips** (i.e., tooltips containing no such tags), however,
    are not. For unclear reasons, plaintext tooltips are implicitly truncated to
    the width of their parent windows. The only means of circumventing this
    obscure constraint is to manually inject newlines at the appropriate
    80-character boundaries of such tooltips -- which has the distinct
    disadvantage of failing to scale to edge-case display and device
    environments (e.g., high-DPI). Such tooltips *cannot* be guaranteed to be
    legible in the general case and hence are blatantly broken under *all* Qt
    versions to date. This is a `well-known long-standing issue <issue_>`__ for
    which no official resolution exists.

    This filter globally addresses this issue by implicitly converting *all*
    intercepted plaintext tooltips into rich text tooltips in a general-purpose
    manner, thus wrapping the former exactly like the latter. To do so, this
    filter (in order):

    #. Auto-detects whether the:

       * Current event is a :class:`QEvent.ToolTipChange` event.
       * Current widget has a **non-empty plaintext tooltip**.

    #. When these conditions are satisfied:

       #. Escapes all HTML syntax in this tooltip (e.g., converting all ``&``
          characters to ``&amp;`` substrings).
       #. Embeds this tooltip in the Qt-specific ``<qt>...</qt>`` tag, thus
          implicitly converting this plaintext tooltip into a rich text tooltip.

    .. _issue:
        https://bugreports.qt.io/browse/QTBUG-41051
    """

    logger = logging.getLogger(__name__)

    def eventFilter(self, widget, event):
        """
        Tooltip-specific event filter handling the passed Qt object and event.
        """

        # If this is a tooltip event...
        if event.type() == PyQt5.QtCore.QEvent.ToolTipChange:
            # If the target Qt object containing this tooltip is *NOT* a widget,
            # raise a human-readable exception. While this should *NEVER* be the
            # case, edge cases are edge cases because they sometimes happen.
            if not isinstance(widget, PyQt5.QtWidgets.QWidget):
                self.logger.error('QObject "{}" not a widget.'.format(widget))

            # Tooltip for this widget if any *OR* the empty string otherwise.
            tooltip = widget.toolTip()

            # If this tooltip is both non-empty and not already rich text...
            if tooltip and not PyQt5.QtCore.Qt.mightBeRichText(tooltip):
                # Convert this plaintext tooltip into a rich text tooltip by:
                #
                # * Escaping all HTML syntax in this tooltip.
                # * Embedding this tooltip in the Qt-specific "<qt>...</qt>" tag.
                tooltip = '<qt>{}</qt>'.format(html.escape(tooltip))

                # Replace this widget's non-working plaintext tooltip with this
                # working rich text tooltip.
                widget.setToolTip(tooltip)

                # Notify the parent event handler this event has been handled.
                return True

        # Else, defer to the default superclass handling of this event.
        return super().eventFilter(widget, event)


class MyApp(PyQt5.QtWidgets.QApplication):
    """
    MyApp implements a custom notify handler to log errors, when C++ classes and python
    wrapper in PyQt5 environment mismatch. mostly this relates to the situation when a
    C++ object is already deleted, but the python wrapper still exists. so far I know
    that's the only chance to log this issues.

    in addition it writes mouse pressed and key pressed events in debug level to log
    including event and object name to be analyse the input methods.
    """

    def notify(self, obj, event):
        try:
            returnValue = PyQt5.QtWidgets.QApplication.notify(self, obj, event)
        except Exception as e:
            logging.error('----------------------------------------------------')
            logging.error('Event: {0}'.format(event))
            logging.error('EventType: {0}'.format(event.type()))
            logging.error('Exception error in event loop: {0}'.format(e))
            logging.error('----------------------------------------------------')
            returnValue = False
        finally:
            if isinstance(event, PyQt5.QtGui.QMouseEvent):
                if event.button():
                    logging.debug(f'Mouse: {obj.objectName()}, {event.button()}')
        return returnValue


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


def setupWorkDirs(mwGlob):
    """
    setupWorkDirs defines the necessary work dirs and checks if they are writable

    :param mwGlob:
    :return: mwGlob
    """

    mwGlob['modeldata'] = '4.0'
    mwGlob['bundleDir'] = ''
    mwGlob['frozen'] = False
    mwGlob['workDir'] = os.getcwd()
    mwGlob['configDir'] = mwGlob['workDir'] + '/config'
    mwGlob['dataDir'] = mwGlob['workDir'] + '/data'
    mwGlob['imageDir'] = mwGlob['workDir'] + '/image'
    mwGlob['tempDir'] = mwGlob['workDir'] + '/temp'
    mwGlob['modelDir'] = mwGlob['workDir'] + '/model'

    for dirPath in ['workDir', 'configDir', 'imageDir', 'dataDir', 'tempDir', 'modelDir']:
        if not os.path.isdir(mwGlob[dirPath]):
            os.makedirs(mwGlob[dirPath])
        if not os.access(mwGlob[dirPath], os.W_OK):
            logging.error('no write access to {0}'.format(dirPath))

    for file in os.scandir(mwGlob['tempDir']):
        os.remove(file)

    return mwGlob


def checkFrozen():
    """
    checkFrozen extracts data needed to distinguish between real python running setup and
    bundled version of pyinstaller

    :return:
    """

    mwGlob = dict()

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

    return mwGlob


def setupLogging():
    """
    setupLogging defines the logger and formats and disables unnecessary library logging

    :return: true for test purpose
    """
    warnings.filterwarnings('ignore')
    name = 'mw4-{0}.log'.format(datetime.datetime.now().strftime("%Y-%m-%d"))
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s.%(msecs)03d]'
                               '[%(levelname)8s]'
                               '[%(filename)20s]'
                               '[%(lineno)5s]'
                               '[%(funcName)20s]'
                               '[%(threadName)10s]'
                               ' > %(message)s',
                        handlers=[logging.FileHandler(name)],
                        datefmt='%Y-%m-%d %H:%M:%S',
                        )

    # setting different log level for imported packages to avoid unnecessary data
    logging.getLogger('mountcontrol').setLevel(logging.DEBUG)
    logging.getLogger('indibase').setLevel(logging.WARNING)
    logging.getLogger('PyQt5').setLevel(logging.ERROR)
    logging.getLogger('requests').setLevel(logging.ERROR)
    # urllib3 is used by requests, so we have to add this as well
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('matplotlib').setLevel(logging.ERROR)
    logging.getLogger('astropy').setLevel(logging.ERROR)
    return True


def writeSystemInfo(mwGlob=None):
    """
    writeSystemInfo print overview data to the log file at the beginning of the start

    :return: true for test purpose
    """

    logging.info('----------------------------------------------------')
    logging.info('')
    logging.info(f' MountWizzard {mwGlob["modeldata"]} started !')
    logging.info('')
    logging.info('----------------------------------------------------')
    logging.info(f' Platform         : {platform.system()}')
    logging.info(f' Release          : {platform.release()}')
    logging.info(f' Machine          : {platform.machine()}')
    logging.info(f' CPU              : {platform.processor()}')
    logging.info(f' Python           : {platform.python_version()}')
    logging.info(f' PyQt5            : {PyQt5.QtCore.PYQT_VERSION_STR}')
    logging.info(f' Qt               : {PyQt5.QtCore.QT_VERSION_STR}')
    logging.info(f' Node             : {platform.node()}')

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
            logging.info(f' IP addr.         : {hostname}')
        logging.info(f' Hosts            : {hostSummary}')

    logging.info(f' Environment is   : {"frozen" if mwGlob["frozen"] else "live"}')
    logging.info(f' Actual workdir   : {mwGlob["workDir"]}')
    logging.info(f' Bundle dir       : {mwGlob["bundleDir"]}')
    logging.info(f' sys.argv[0]      : {sys.argv[0]}')
    logging.info(f' os.path.basename : {os.path.basename(sys.argv[0])}')
    logging.info(f' sys.executable   : {sys.executable}')

    logging.info('----------------------------------------------------')
    logging.info('')
    return True


def extractDataFiles(mwGlob=None, splashW=None):
    """
    we have the necessary files for leap second, ephemerides and satellite already stored
    in the files system of the app. we bring them to the file system of the user, if they
    do not exist.

    :return: True fpr test purpose
    """

    if mwGlob is None:
        return False

    files = [
        'Leap_Second.dat',
        'deltat.data',
        'deltat.preds',
        'de421_23.bsp',
        'active.txt',
    ]
    for file in files:
        if splashW is not None:
            splashW.showMessage('Loading {0}'.format(file))
        filePath = mwGlob['dataDir'] + '/' + file
        if os.path.isfile(filePath):
            continue
        # as we cannot access data from Qt resource system, we have to convert it to
        # ByteIO first
        stream = PyQt5.QtCore.QFile(f':/{file}')
        stream.open(PyQt5.QtCore.QFile.ReadOnly)
        with open(filePath, 'wb') as outFile:
            outFile.write(stream.readAll())
        stream.close()
    return True


def main():
    """
    main prepares the loading of mountwizzard application. it prepares a splash screen
    and handler the setup of the logger, bundle handling etc. in addition some information
    about the system are written into the logfile to be able to debug in different conditions
    the system environment.

    :return: nothing
    """
    # setting locale
    locale.setlocale(locale.LC_ALL, '')

    # initiating the main app
    app = MyApp(sys.argv)
    # app = PyQt5.QtWidgets.QApplication(sys.argv)

    # generating splash screen
    splashW = splash.SplashScreen(application=app)

    # and start with a first splash screen
    splashW.showMessage('Start initialising')
    splashW.setValue(0)

    # checking workdir and if the system is started from frozen app
    mwGlob = checkFrozen()
    mwGlob = setupWorkDirs(mwGlob)

    # now setup the logging environment
    splashW.showMessage('Setup logging')
    splashW.setValue(20)
    setupLogging()

    # start logging with basic system data for information
    splashW.showMessage('Write system info to log')
    splashW.setValue(40)
    writeSystemInfo(mwGlob=mwGlob)

    # loading leap seconds, spice kernel and hipparcos catalogue
    splashW.showMessage('Loading star and time data')
    splashW.setValue(60)
    extractDataFiles(mwGlob=mwGlob, splashW=splashW)

    # and finally starting the application
    splashW.showMessage('Loading Data')
    splashW.setValue(80)

    # setting except hook for saving some data of errors
    sys.excepthook = except_hook

    # adding a icon
    app.setWindowIcon(PyQt5.QtGui.QIcon(':/mw4.ico'))

    # adding event filter for formatting the tooltips nicely
    app.installEventFilter(QAwesomeTooltipEventFilter(app))

    mountApp = mainApp.MountWizzard4(mwGlob)
    mountApp.mainW.show()

    # end of splash screen
    splashW.showMessage('Finishing loading')
    splashW.setValue(100)
    splashW.close()

    # quit app
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
