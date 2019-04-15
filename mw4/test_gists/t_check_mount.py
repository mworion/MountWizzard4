import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import PyQt5.QtNetwork
import PyQt5
import sys
import mw4.gui.widget as widget
import numpy as np
from mw4.gui.media import resources


class HelloWindow(QtWidgets.QMainWindow, widget.MWidget):
    def __init__(self):
        super().__init__()

        self.barry = b''
        # tcp handling
        self.socket = PyQt5.QtNetwork.QTcpSocket()
        self.socket.readyRead.connect(self._handleReadyRead)
        self.socket.error.connect(self._handleError)
        self.socket.connectToHost('192.168.2.15', 3491)
        print(self.socket.waitForConnected())

    def _handleReadyRead(self):
        """
        _handleReadyRead gets the date in buffer signal and starts to read data from the
        network. as long as data is streaming, it feeds to the xml parser. with this
        construct you don't have to put the whole data set into the parser at once, but
        doing the work step be step.

        :return: nothing
        """

        buf = self.socket.readAll()

        line = b''
        for i in range(0, len(buf)):
            if buf[i] == b'\x02':
                if line != b'':
                    lineNp = np.frombuffer(line, dtype=np.uint8)
                    if lineNp[1] == 129:
                        print(lineNp[2:-1])
                line = b''
            else:
                line += buf[i]

    def _handleError(self, socketError):
        """
        _handleError log all network errors in case of problems.

        :param socketError: the error from socket library
        :return: nothing
        """
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = HelloWindow()
    mainWin.show()

    sys.exit(app.exec_())
