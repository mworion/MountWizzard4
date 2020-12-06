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
# written in python3 , (c) 2019, 2020 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import socket
# external packages
import PyQt5.QtCore
# local import
import indibase.indiBase


class WorkerSignals(PyQt5.QtCore.QObject):
    """
    The WorkerSignals class offers a list of signals to be used and instantiated by the
    Worker class to get signals for error, finished and result to be transferred to the
    caller back
    """

    __all__ = ['WorkerSignals']

    finished = PyQt5.QtCore.pyqtSignal()
    error = PyQt5.QtCore.pyqtSignal(object)
    result = PyQt5.QtCore.pyqtSignal(object)


class Worker(PyQt5.QtCore.QRunnable):
    """
    The Worker class offers a generic interface to allow any function to be executed as a
    thread in an threadpool
    """

    __all__ = ['Worker',
               'run']

    log = logging.getLogger(__name__)

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        """
        runs an arbitrary methods with it's parameters and catches the result

        :return: nothing, but sends results and status as signals
        """

        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.signals.error.emit(e)

        else:
            self.signals.result.emit(result)

        finally:
            self.signals.finished.emit()


class Client(indibase.indiBase.Client):
    """
    Client implements an INDI Base Client for INDI servers. it rely on PyQt5 and it's
    signalling scheme. there might be not all capabilities implemented right now. all
    the data, properties and attributes are stored in a the devices dict.
    The reading and parsing of the XML data is done in a streaming way, so for xml the
    xml.parse.feed() mechanism is used.

        >>> indiClient = Client(
        >>>                     host=host
        >>>                     )

    """

    __all__ = ['Client',
               ]

    log = logging.getLogger(__name__)

    SOCKET_TIMEOUT = 1
    CYCLE_SERVER_UP = 5000

    def __init__(self,
                 host=None,
                 threadPool=None
                 ):
        super().__init__(host=host)

        if threadPool is None:
            self.threadPool = PyQt5.QtCore.QThreadPool()

        else:
            self.threadPool = threadPool

        self.threadPool.setExpiryTimeout(300000)
        self.mutexServerUp = PyQt5.QtCore.QMutex()

        self.timerServerUp = PyQt5.QtCore.QTimer()
        self.timerServerUp.setSingleShot(False)
        self.timerServerUp.timeout.connect(self.cycleCheckServerUp)

    def checkServerUp(self):
        """
        checkServerUp polls the host/port of the mount computer and set the state and
        signals for the status accordingly.

        :return: nothing
        """

        client = socket.socket()
        client.settimeout(self.SOCKET_TIMEOUT)
        try:
            client.connect(self.host)

        except Exception:
            suc = False

        else:
            suc = True

        finally:
            client.shutdown(socket.SHUT_RDWR)
            client.close()

        return suc

    def checkServerUpResult(self, result):
        """

        :param result:
        :return:
        """

        if result and not self.connected:
            suc = self.connectServer()
            self.log.info(f'Connect to server, result: {suc}')
            return suc

        else:
            return False

    def errorCycleCheckServerUp(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """
        self.log.error(f'Cycle error: {e}')

    def clearCycleCheckServerUp(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """

        self.mutexServerUp.unlock()

    def cycleCheckServerUp(self):
        """
        cycleCheckServerUp prepares the worker thread and the signals for getting the settings
        data.

        :return: nothing
        """

        if self.host is None:
            return False

        if not self.mutexServerUp.tryLock():
            return

        worker = Worker(self.checkServerUp)
        worker.signals.finished.connect(self.clearCycleCheckServerUp)
        worker.signals.result.connect(self.checkServerUpResult)
        worker.signals.error.connect(self.errorCycleCheckServerUp)
        self.threadPool.start(worker)

    def startTimers(self):
        """
        startTimers enables the cyclic timers for polling necessary mount data.

        :return: nothing
        """

        self.timerServerUp.start(self.CYCLE_SERVER_UP)

    def stopTimers(self):
        """
        stopTimers disables the cyclic timers for polling necessary mount data.


        :return: nothing
        """

        self.timerServerUp.stop()
