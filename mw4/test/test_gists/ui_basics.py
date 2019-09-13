
import logging
import logging.config
import os
import sys
import platform
import socket
import datetime
import warnings
import traceback
import shutil
import json
import gc
from io import BytesIO
# external packages
import matplotlib
matplotlib.use('Qt5Agg')
import PyQt5.QtCore
import PyQt5.QtWidgets
import skyfield.iokit
# local import
from mw4 import mainApp
from mw4.gui import splash

from PyQt5.QtWidgets import QApplication, QLabel

app = QApplication([])
label = QLabel('Hello World')
label.show()
app.exec_()