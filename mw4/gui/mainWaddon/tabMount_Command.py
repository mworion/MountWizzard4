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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import webbrowser
import time

# external packages
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import QObject

# local import
from mountcontrol.connection import Connection


class MountCommand(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()

        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.ui.mountCommandTable.clicked.connect(self.openCommandProtocol)
        self.ui.commandInput.returnPressed.connect(self.commandRaw)
        self.ui.mountUpdateTimeDelta.clicked.connect(self.openUpdateTimeDelta)
        self.ui.mountUpdateFirmware.clicked.connect(self.openUpdateFirmware)
        self.ui.mountDocumentation.clicked.connect(self.openMountDocumentation)

    def openCommandProtocol(self) -> None:
        """ """
        url = "http://" + self.ui.mountHost.text() + "/manuals/command-protocol.pdf"
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, "System", "Mount", "Browser failed")
        else:
            self.msg.emit(0, "System", "Mount", "command protocol opened")

    def openUpdateTimeDelta(self) -> None:
        """ """
        url = "http://" + self.ui.mountHost.text() + "/updatetime.html"
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, "System", "Mount", "Browser failed")
        else:
            self.msg.emit(0, "System", "Mount", "update time delta opened")

    def openUpdateFirmware(self) -> None:
        """ """
        url = "http://" + self.ui.mountHost.text() + "/updatefirmware.html"
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, "System", "Mount", "Browser failed")
        else:
            self.msg.emit(0, "System", "Mount", "update firmware opened")

    def openMountDocumentation(self) -> None:
        """ """
        mountStrings = self.app.mount.firmware.product.split()
        if len(mountStrings) != 2:
            self.msg.emit(2, "System", "Mount", "Browser failed")
            return
        mountType = mountStrings[1]
        host = self.ui.mountHost.text()
        url = f"http://{host}/manuals/{mountType}-en.pdf"
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, "System", "Mount", "Browser failed")
        else:
            self.msg.emit(0, "System", "Mount", "mount manual opened")

    def commandRaw(self) -> None:
        """ """
        host = self.app.mount.host
        conn = Connection(host)
        cmd = self.ui.commandInput.text()
        self.ui.commandStatus.clear()
        self.ui.commandOutput.clear()
        startTime = time.time()
        sucSend, sucRec, val = conn.communicateRaw(cmd)
        endTime = time.time()
        delta = endTime - startTime
        self.ui.commandOutput.clear()
        if sucSend:
            t = "Command OK\n"
            self.ui.commandStatus.insertPlainText(t)
        if sucRec:
            t = f"Receive OK, took {delta:2.3f}s"
            self.ui.commandStatus.insertPlainText(t)
        else:
            t = f"Receive {val}, took {delta:2.3f}s"
            self.ui.commandStatus.insertPlainText(t)

        self.ui.commandOutput.insertPlainText(val + "\n")
        self.ui.commandOutput.moveCursor(QTextCursor.MoveOperation.End)
