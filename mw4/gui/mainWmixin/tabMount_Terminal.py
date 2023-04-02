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
import time
import webbrowser

# external packages
from PyQt5.QtGui import QTextCursor

# local import
from mountcontrol.connection import Connection


class MountTerminal:
    """
    """
    def __init__(self):
        """
        """
        self.ui.commandInput.returnPressed.connect(self.commandRaw)
        self.ui.mountCommandTable.clicked.connect(self.openCommandProtocol)

    def openCommandProtocol(self):
        """
        :return:
        """
        url = 'http://' + self.ui.mountHost.text() + '/manuals/command-protocol.pdf'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'Mount', 'Browser failed')
        else:
            self.msg.emit(0, 'System', 'Mount', '10micron opened')
        return True

    def commandRaw(self):
        """
        :return:
        """
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
            t = 'Command OK\n'
            self.ui.commandStatus.insertPlainText(t)
        if sucRec:
            t = f'Receive OK, took {delta:2.3f}s'
            self.ui.commandStatus.insertPlainText(t)
        else:
            t = f'Receive ERROR, took {delta:2.3f}s'
            self.ui.commandStatus.insertPlainText(t)

        self.ui.commandOutput.insertPlainText(val + '\n')
        self.ui.commandOutput.moveCursor(QTextCursor.End)
        return True
