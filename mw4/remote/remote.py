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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
# external packages
from PyQt5.QtCore import QObject
from PyQt5 import QtNetwork
# local imports
from mw4.base.loggerMW import CustomLogger


class Remote(QObject):
    """
    The class Remote inherits all information and handling of remotely controlling
    mountwizzard 4.

        >>> remote = Remote(app=None)

    """

    __all__ = ['Remote',
               'startCommunication',
               'stopCommunication',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    def __init__(self,
                 app=None,
                 ):
        super().__init__()

        self.app = app

        self.data = {}
        self.framework = None
        self.run = {
            'built-in': self
        }
        self.name = ''

        self.clientConnection = None
        self.tcpServer = None

    def startCommunication(self, loadConfig=False):
        """
        startCommunication prepares the remote listening by starting a tcp server listening
        on localhost and port 3490.

        :param loadConfig:
        :return: success
        """

        if self.tcpServer is not None:
            return False

        self.tcpServer = QtNetwork.QTcpServer(self)
        hostAddress = QtNetwork.QHostAddress('127.0.0.1')

        if not self.tcpServer.listen(hostAddress, 3490):
            self.log.warning('Port already in use')
            self.tcpServer = None
            return False
        else:
            self.log.info('Remote access enabled')
            self.tcpServer.newConnection.connect(self.addConnection)
            return True

    def stopCommunication(self):
        """
        stopCommunication kills all connections and stops the tcpServer

        :return: true for test purpose
        """

        if self.clientConnection is not None:
            self.clientConnection.close()

        if self.tcpServer is not None:
            self.tcpServer = None

        return True

    def addConnection(self):
        """
        addConnection allows a new connection for remote access to mw4 only one connection
        is allowed.

        :return: success
        """

        if self.tcpServer is None:
            return False

        self.clientConnection = self.tcpServer.nextPendingConnection()

        if self.clientConnection == 0:
            self.log.error('Cannot establish incoming connection')
            return False

        self.clientConnection.nextBlockSize = 0
        self.clientConnection.readyRead.connect(self.receiveMessage)
        self.clientConnection.disconnected.connect(self.removeConnection)
        self.clientConnection.error.connect(self.handleError)
        connection = self.clientConnection.peerAddress().toString()
        self.log.info(f'Connection to MountWizzard from {connection}')

        return True

    def receiveMessage(self):
        """
        receiveMessage is the command dispatcher for remote access

        :return: success
        """

        if self.clientConnection.bytesAvailable() == 0:
            return False

        validCommands = ['shutdown',
                         'shutdown mount',
                         'boot mount',
                         ]

        connection = self.clientConnection.peerAddress().toString()
        command = str(self.clientConnection.read(100), "ascii")
        command = command.replace('\n', '')
        command = command.replace('\r', '')

        self.log.info(f'Command {command} from {connection} received')

        if command in validCommands:
            self.app.remoteCommand.emit(command)
        else:
            self.log.error(f'Unknown command {command} from {connection} received')

        return True

    def removeConnection(self):
        """
        removeConnection clear the existing connection

        :return: true for test purpose
        """

        connection = self.clientConnection.peerAddress().toString()
        self.clientConnection.close()
        self.log.info(f'Connection from {connection} closed')

        return True

    def handleError(self, socketError):
        """
        handleError does error handling -> writing to log

        :param socketError:
        :return: true for test purpose
        """

        connection = self.clientConnection.peerAddress().toString()
        self.log.critical(f'Connection from {connection} failed, error: {socketError}')

        return True
