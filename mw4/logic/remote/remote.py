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
import logging
# external packages
from PyQt5.QtCore import QObject
from PyQt5 import QtNetwork
# local imports


class Remote(QObject):
    """
    """

    __all__ = ['Remote']
    log = logging.getLogger(__name__)

    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {'internal': {'deviceName': 'TCP'}}}
        self.framework = ''
        self.run = {
            'internal': self
        }
        self.deviceName = ''
        self.clientConnection = None
        self.tcpServer = None

    def startCommunication(self):
        """
        :return: success
        """
        if self.tcpServer is not None:
            return False

        self.tcpServer = QtNetwork.QTcpServer(self)
        hostAddress = QtNetwork.QHostAddress('127.0.0.1')
        if not self.tcpServer.listen(hostAddress, 3490):
            self.log.info('Port already in use')
            self.tcpServer = None
            return False
        else:
            self.log.info('Remote access enabled')
            self.tcpServer.newConnection.connect(self.addConnection)
            return True

    def stopCommunication(self):
        """
        :return: true for test purpose
        """
        if self.clientConnection is not None:
            self.clientConnection.close()
        if self.tcpServer is not None:
            self.tcpServer = None
        return True

    def addConnection(self):
        """
        :return: success
        """
        if self.tcpServer is None:
            return False

        self.clientConnection = self.tcpServer.nextPendingConnection()
        if self.clientConnection == 0:
            self.log.warning('Cannot establish incoming connection')
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

        self.log.debug(f'Command {command} from {connection} received')
        if command in validCommands:
            self.app.remoteCommand.emit(command)
        else:
            self.log.warning(f'Unknown command {command} from {connection} received')

        return True

    def removeConnection(self):
        """
        :return: true for test purpose
        """
        connection = self.clientConnection.peerAddress().toString()
        self.clientConnection.close()
        self.log.debug(f'Connection from {connection} closed')
        return True

    def handleError(self, socketError):
        """
        :param socketError:
        :return: true for test purpose
        """
        connection = self.clientConnection.peerAddress().toString()
        self.log.critical(f'Connection from {connection} failed, error: {socketError}')
        return True
