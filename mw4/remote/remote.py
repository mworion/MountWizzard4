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
import logging
# external packages
import PyQt5
# local imports


class Remote(PyQt5.QtCore.QObject):
    """
    The class Remote inherits all information and handling of remotely controlling
    mountwizzard 4.

        >>> fw = Remote( app=None,
        >>>              )
    """

    __all__ = ['Remote',
               'startRemote',
               'stopRemote',
               ]

    version = '0.2'
    logger = logging.getLogger(__name__)

    def __init__(self,
                 app=None,
                 ):
        super().__init__()

        self.app = app
        self.clientConnection = None
        self.tcpServer = None

    def startRemote(self):
        """
        startRemote prepares the remote listening by starting a tcp server listening
        on localhost and port 3490.

        :return: success
        """

        if self.tcpServer is not None:
            return False

        self.tcpServer = PyQt5.QtNetwork.QTcpServer(self)
        hostAddress = PyQt5.QtNetwork.QHostAddress('127.0.0.1')

        if not self.tcpServer.listen(hostAddress, 3490):
            self.logger.warning('Port already in use')
            self.tcpServer = None
            return False
        else:
            self.logger.info('Remote access enabled')
            self.tcpServer.newConnection.connect(self.addConnection)
            return True

    def stopRemote(self):
        """
        stopRemote kills all connections and stops the tcpServer

        :return: success
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
            self.logger.error('Cannot establish incoming connection')
            return False

        self.clientConnection.nextBlockSize = 0
        self.clientConnection.readyRead.connect(self.receiveMessage)
        self.clientConnection.disconnected.connect(self.removeConnection)
        self.clientConnection.error.connect(self.handleError)
        connection = self.clientConnection.peerAddress().toString()
        self.logger.info(f'Connection to MountWizzard from {connection}')

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

        self.logger.info(f'Command {command} from {connection} received')

        if command in validCommands:
            self.app.remoteCommand.emit(command)
        else:
            self.logger.error(f'Unknown command {command} from {connection} received')

        return True

    def removeConnection(self):
        """
        removeConnection clear the existing connection

        :return: true for test purpose
        """

        connection = self.clientConnection.peerAddress().toString()
        self.clientConnection.close()
        self.logger.info(f'Connection from {connection} closed')

        return True

    def handleError(self, socketError):
        """
        handleError does error handling -> writing to log

        :param socketError:
        :return: true for test purpose
        """

        connection = self.clientConnection.peerAddress().toString()
        self.logger.error(f'Connection from {connection} failed, error: {socketError}')

        return True
