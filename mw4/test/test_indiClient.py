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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import sys
import logging
from unittest import mock
# external packages
import PyQt5
import PyQt5.QtWidgets
# local import
from mw4.indi import indiBaseClient
from mw4.indi.INDI import *


class TestQtIndi(PyQt5.QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        qbtn = PyQt5.QtWidgets.QPushButton('Quit', self)
        qbtn.clicked.connect(self.quit)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 50)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Test IndiBaseClient')
        self.show()

    def quit(self):
        self.close()
        PyQt5.QtWidgets.QApplication.instance().quit()


logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s.%(msecs)03d]'
                           '[%(levelname)7s]'
                           '[%(filename)15s]'
                           '[%(lineno)5s]'
                           '[%(funcName)25s]'
                           '[%(threadName)10s]'
                           ' > %(message)s',
                    handlers=[logging.FileHandler('test_indi.log')],
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )

logging.info('start')


app = PyQt5.QtWidgets.QApplication(sys.argv)
widget = TestQtIndi()
client = indiBaseClient.IndiBaseClient('192.168.2.57')
client.connect()
client.setBlobMode(INDI.BLOBHandling.B_ALSO, 'CCD Simulator', None)
rc = app.exec_()
for devs in client.devices:
    print(devs, devs.)
client.disconnect()
sys.exit(rc)
