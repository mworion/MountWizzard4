# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from dataclasses import dataclass, field
from mw4.base.appProtocol import AppProtocol
from mw4.base.signalsDevices import Signals
from PySide6.QtNetwork import QAbstractSocket, QHostAddress, QTcpServer
from typing import Any


@dataclass
class DeviceConfigRemote:
    deviceName: str = field(default="TCP")


class Remote:
    DEVICE_TYPE = "misc"
    log = logging.getLogger("MW4")

    def __init__(self, app: AppProtocol) -> None:
        self.signals = Signals()
        self.app = app
        self.data: dict[str, Any] = {}
        self.config = DeviceConfigRemote()
        self.framework: str = ""
        self.run: dict[str, Any] = {"tcp": self}
        self.clientConnection: Any = None
        self.tcpServer: QTcpServer | None = None

    def startCommunication(self) -> bool:
        self.tcpServer = QTcpServer()
        hostAddress = QHostAddress("localhost")
        if not self.tcpServer.listen(hostAddress, 3490):
            self.log.info("Port already in use")
            return False
        else:
            self.log.info("Remote access enabled")
            self.tcpServer.newConnection.connect(self.addConnection)
            self.signals.deviceConnected.emit(self.config.deviceName)
            return True

    def stopCommunication(self) -> None:
        if self.tcpServer is not None and self.tcpServer.isListening():
            self.tcpServer.close()
        self.signals.deviceDisconnected.emit(self.config.deviceName)

    def addConnection(self) -> None:
        if self.tcpServer is None:
            return

        self.clientConnection = self.tcpServer.nextPendingConnection()
        if not self.clientConnection:
            self.log.warning("Cannot establish incoming connection")
            return

        self.clientConnection.readyRead.connect(self.receiveMessage)
        self.clientConnection.disconnected.connect(self.removeConnection)
        self.clientConnection.errorOccurred.connect(self.handleError)
        connection = self.clientConnection.peerAddress().toString()
        self.log.info("Connection to MountWizzard from %s", connection)

    def receiveMessage(self) -> bool:
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

        self.log.debug("Command %s from %s received", command, connection)
        if command in validCommands:
            self.app.remoteCommand.emit(command)
        else:
            self.log.warning("Unknown command %s from %s received", command, connection)

        return True

    def removeConnection(self) -> None:
        connection = self.clientConnection.peerAddress().toString()
        self.clientConnection.close()
        self.log.debug("Connection from %s closed", connection)

    def handleError(self, socketError: QAbstractSocket.SocketError) -> None:
        connection = self.clientConnection.peerAddress().toString()
        self.log.critical("Connection from %s failed, error: %s", connection, socketError)
