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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import socket

# external packages
from PyQt5.QtCore import QMutex, QTimer, QThreadPool

# local import
from base.tpool import Worker
from indibase.indiBase import Client


class Client(Client):
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

    SOCKET_TIMEOUT = 3
    CYCLE_SERVER_UP = 5000

    def __init__(self, host=None, threadPool=None):
        super().__init__(host=host)
        if threadPool is None:
            self.threadPool = QThreadPool()

        else:
            self.threadPool = threadPool

        self.mutexServerUp = QMutex()
        self.timerServerUp = QTimer()
        self.timerServerUp.setSingleShot(False)
        self.timerServerUp.timeout.connect(self.cycleCheckServerUp)

    def checkServerUp(self):
        """
        checkServerUp polls the host/port of the mount computer and set the state and
        signals for the status accordingly.

        :return: nothing
        """
        with socket.socket() as client:
            client.settimeout(self.SOCKET_TIMEOUT)
            try:
                client.connect(self.host)

            except Exception:
                return False

            else:
                return True

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
        :return: nothing
        """
        self.log.error(f'Cycle error: {e}')
        return True

    def clearCycleCheckServerUp(self):
        """
        :return: nothing
        """
        self.mutexServerUp.unlock()
        return True

    def cycleCheckServerUp(self):
        """
        :return: nothing
        """
        if self.host is None:
            return False

        if not self.mutexServerUp.tryLock():
            return False

        worker = Worker(self.checkServerUp)
        worker.signals.finished.connect(self.clearCycleCheckServerUp)
        worker.signals.result.connect(self.checkServerUpResult)
        worker.signals.error.connect(self.errorCycleCheckServerUp)
        self.threadPool.start(worker)
        return True

    def startTimers(self):
        """
        :return: nothing
        """
        self.timerServerUp.start(self.CYCLE_SERVER_UP)
        return True

    def stopTimers(self):
        """
        :return: nothing
        """
        self.timerServerUp.stop()
        self.threadPool.waitForDone()
        return True
