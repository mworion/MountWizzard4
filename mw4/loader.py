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
# Python  v3.6.7
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
import skyfield.iokit
# local import
from mw4 import mainApp
from mw4.gui import splash


class MyApp(PyQt5.QtWidgets.QApplication):
    """
    MyApp implements a custom notify handler to log errors, when C++ classes and python
    wrapper in PyQt5 environment mismatch. mostly this relates to the situation when a
    C++ object is already deleted, but the python wrapper still exists. so far I know
    that's the only chance to log this issues.

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
            pass
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


def setDirectories(logging, mwGlob):
    """

    :param logging:
    :param mwGlob:
    :return:
    """

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


def checkFrozen(mwGlob):
    """

    :param mwGlob:
    :return:
    """

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
        'modeldata': mainApp.MountWizzard4.version,
        'frozen': False,
        'bundleDir': '',
        'workDir': '',
        'configDir': '',
        'dataDir': '',
        'imageDir': '',
    }

    # checking workdir and if the system is started from frozen app
    checkFrozen(mwGlob)

    # now instantiate the application from QApplication
    PyQt5.QtWidgets.QApplication.setAttribute(PyQt5.QtCore.Qt.AA_EnableHighDpiScaling, True)

    # implement notify different to catch exception from event handler
    app = MyApp(sys.argv)
    # app = PyQt5.QtWidgets.QApplication(sys.argv)
    # setting a splash pixel map for loading
    splash_pix = PyQt5.QtGui.QPixmap(':/mw4.ico')
    splashW = splash.SplashScreen(pix=splash_pix, qapp=app)

    # and start with a first splash screen
    splashW.showMessage('Start initialising')
    splashW.setValue(0)
    # setting work dir:
    mwGlob['workDir'] = os.getcwd()
    mwGlob['configDir'] = os.getcwd() + '/config'
    mwGlob['dataDir'] = os.getcwd() + '/data'
    mwGlob['imageDir'] = os.getcwd() + '/image'
    # now setup the logging environment
    splashW.showMessage('Setup logging')
    splashW.setValue(20)
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
    splashW.showMessage('Checking work directories')
    splashW.setValue(30)
    setDirectories(logging, mwGlob)

    # start logging with basic system data for information
    splashW.showMessage('Logging environment')
    splashW.setValue(40)
    logging.info('------------------------------------------------------------------------')
    logging.info('')
    logging.info('MountWizzard {0} started !'.format(mwGlob['modeldata']))
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

    # loading leap seconds, spice kernel and hipparcos catalogue
    splashW.showMessage('Loading star and time data')
    splashW.setValue(60)
    urls = [
        'https://hpiers.obspm.fr/iers/bul/bulc/Leap_Second.dat',
        'http://maia.usno.navy.mil/ser7/deltat.data',
        'http://maia.usno.navy.mil/ser7/deltat.preds',
        'ftp://ssd.jpl.nasa.gov/pub/eph/planets/bsp/de421.bsp',
        'ftp://cdsarc.u-strasbg.fr/cats/I/239/hip_main.dat.gz',
    ]
    files = [
        'Leap_Second.dat',
        'deltat.data',
        'deltat.preds',
        'de421.bsp',
        'hip_main.dat.gz',
    ]
    for url, file in zip(urls, files):
        splashW.showMessage('Loading {0}'.format(file))
        filePath = mwGlob['dataDir'] + '/' + file
        if os.path.isfile(filePath):
            continue
        skyfield.iokit.download(url,
                                filePath,
                                verbose=True)
    # and finally starting the application
    splashW.showMessage('Preparing application')
    splashW.setValue(80)
    sys.excepthook = except_hook
    app.setWindowIcon(PyQt5.QtGui.QIcon(':/mw4.ico'))
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
