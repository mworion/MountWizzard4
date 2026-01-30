############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################
import logging
from mw4.base.signalsDevices import Signals
from PySide6.QtNetwork import QTcpServer, QHostAddress, QTcpSocket, QAbstractSocket


class Remote:
    """ """
    log = logging.getLogger("MW4")

    def __init__(self, app):
        self.signals = Signals()
        self.app = app
        self.data = {}
        self.defaultConfig = {
            "framework": "",
            "frameworks": {"tcp": {"deviceName": "TCP"}},
        }
        self.framework: str = ""
        self.run: dict = {"tcp": self}
        self.deviceName: str = ""
        self.clientConnection: QTcpSocket | None = None
        self.tcpServer: QTcpServer | None = None

    def startCommunication(self) -> bool:
        """ """
        self.tcpServer = QTcpServer()
        hostAddress = QHostAddress("localhost")
        if not self.tcpServer.listen(hostAddress, 3490):
            self.log.info("Port already in use")
            self.tcpServer = None
            return False
        else:
            self.log.info("Remote access enabled")
            self.tcpServer.newConnection.connect(self.addConnection)
            self.signals.deviceConnected.emit("TCP")
            return True

    def stopCommunication(self) -> None:
        """ """
        if self.tcpServer.isListening():
            self.tcpServer.close()
        self.signals.deviceDisconnected.emit("TCP")

    def addConnection(self) -> None:
        """ """
        if self.tcpServer is None:
            return

        self.clientConnection = self.tcpServer.nextPendingConnection()
        if not self.clientConnection:
            self.log.warning("Cannot establish incoming connection")
            return

        self.clientConnection.nextBlockSize = 0
        self.clientConnection.readyRead.connect(self.receiveMessage)
        self.clientConnection.disconnected.connect(self.removeConnection)
        self.clientConnection.errorOccurred.connect(self.handleError)
        connection = self.clientConnection.peerAddress().toString()
        self.log.info(f"Connection to MountWizzard from {connection}")

    def receiveMessage(self) -> bool:
        """ """
        if self.clientConnection.bytesAvailable() == 0:
            return False

        validCommands = [
            "shutdown",
            "shutdown mount",
            "boot mount",
        ]

        connection = self.clientConnection.peerAddress().toString()
        command = self.clientConnection.read(100).toStdString()
        command = command.replace("\n", "")
        command = command.replace("\r", "")

        self.log.debug(f"Command {command} from {connection} received")
        if command in validCommands:
            self.app.remoteCommand.emit(command)
        else:
            self.log.warning(f"Unknown command {command} from {connection} received")

        return True

    def removeConnection(self) -> None:
        """ """
        connection = self.clientConnection.peerAddress().toString()
        self.clientConnection.close()
        self.log.debug(f"Connection from {connection} closed")

    def handleError(self, socketError: QAbstractSocket.SocketError) -> None:
        """ """
        connection = self.clientConnection.peerAddress().toString()
        self.log.critical(f"Connection from {connection} failed, error: {socketError}")
