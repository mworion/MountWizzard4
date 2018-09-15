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
import logging
import platform
# external packages
import PyQt5.QtWidgets
import PyQt5.QtGui
# local imports
from base import styles

import time


class MwWidget(PyQt5.QtWidgets.QWidget, styles.MWStyles):

    logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()
        self.palette = PyQt5.QtGui.QPalette()
        self.bundle_dir = ''
        self.showStatus = False
        self.initUI()
        self.screenSizeX = PyQt5.QtWidgets.QDesktopWidget().screenGeometry().width()
        self.screenSizeY = PyQt5.QtWidgets.QDesktopWidget().screenGeometry().height()

    def closeEvent(self, closeEvent):
        self.showStatus = False
        if self.windowTitle().startswith('MountWizzard'):
            self.quit()

    @staticmethod
    def widgetIcon(gui, icon):
        gui.setIcon(PyQt5.QtGui.QIcon(icon))
        gui.setProperty('iconset', True)
        gui.style().unpolish(gui)
        gui.style().polish(gui)
        gui.setIconSize(PyQt5.QtCore.QSize(16, 16))

    def initUI(self):
        self.setWindowFlags((self.windowFlags()
                             | PyQt5.QtCore.Qt.CustomizeWindowHint)
                            & ~PyQt5.QtCore.Qt.WindowMaximizeButtonHint)
        self.setMouseTracking(True)
        # sizing in gui should be fixed, because I have a static layout
        self.setFixedSize(800, 600)
        self.setWindowIcon(PyQt5.QtGui.QIcon(':/mw.ico'))
        if platform.system() == 'Darwin':
            self.setStyleSheet(self.MAC_STYLE + self.BASIC_STYLE)
        else:
            self.setStyleSheet(self.NON_MAC_STYLE + self.BASIC_STYLE)

    @staticmethod
    def changeStylesheet(ui, item, value):
        ui.setProperty(item, value)
        ui.style().unpolish(ui)
        ui.style().polish(ui)

    @staticmethod
    def selectFile(window, title, folder, filterSet, openFile=True):
        dlg = PyQt5.QtWidgets.QFileDialog()
        dlg.setWindowIcon(PyQt5.QtGui.QIcon(':/mw.ico'))
        dlg.setStyleSheet('background-color: rgb(32,32,32); color: rgb(192,192,192)')
        dlg.setViewMode(PyQt5.QtWidgets.QFileDialog.List)
        dlg.setFileMode(PyQt5.QtWidgets.QFileDialog.ExistingFile)
        dlg.setNameFilter(filterSet)
        dlg.setModal(True)
        ph = window.geometry().height()
        px = window.geometry().x()
        py = window.geometry().y()
        dw = window.width()
        dh = window.height()
        dlg.setGeometry(px, py + ph - dh, dw, dh)
        ext = ''
        options = PyQt5.QtWidgets.QFileDialog.DontUseNativeDialog
        if openFile:
            value = dlg.getOpenFileName(dlg,
                                        title,
                                        os.getcwd() + folder,
                                        filterSet,
                                        options=options,
                                        )
        else:
            value = dlg.getSaveFileName(dlg,
                                        title,
                                        os.getcwd() + folder,
                                        filterSet,
                                        options=options,
                                        )
        name = value[0]
        if len(name) > 0:
            name, ext = os.path.splitext(name)
        return name, ext

    @staticmethod
    def selectDir(window, title, folder):
        dlg = PyQt5.QtWidgets.QFileDialog()
        dlg.setWindowIcon(PyQt5.QtGui.QIcon(':/mw.ico'))
        dlg.setStyleSheet('background-color: rgb(32,32,32); color: rgb(192,192,192)')
        dlg.setViewMode(PyQt5.QtWidgets.QFileDialog.List)
        dlg.setModal(True)
        ph = window.geometry().height()
        px = window.geometry().x()
        py = window.geometry().y()
        dw = window.width()
        dh = window.height()
        dlg.setGeometry(px, py + ph - dh, dw, dh)
        options = PyQt5.QtWidgets.QFileDialog.DontUseNativeDialog
        value = dlg.getExistingDirectory(dlg,
                                         title,
                                         folder,
                                         options=options,
                                         )
        return value

    def dialogMessageLoadSaveDelete(self, window, title, question):
        dlg = PyQt5.QtWidgets.QMessageBox()
        if platform.system() == 'Darwin':
            dlg.setStyleSheet(self.MAC_STYLE + self.BASIC_STYLE)
        else:
            dlg.setStyleSheet(self.NON_MAC_STYLE + self.BASIC_STYLE)
        dlg.addButton('Load', PyQt5.QtWidgets.QMessageBox.YesRole)
        dlg.addButton('Save', PyQt5.QtWidgets.QMessageBox.YesRole)
        dlg.addButton('Delete', PyQt5.QtWidgets.QMessageBox.YesRole)
        cancel = dlg.addButton('Cancel', PyQt5.QtWidgets.QMessageBox.YesRole)
        dlg.setDefaultButton(cancel)
        dlg.setWindowTitle(title)
        dlg.setText(question)
        dlg.setIcon(PyQt5.QtWidgets.QMessageBox.Warning)
        dlg.setWindowIcon(PyQt5.QtGui.QIcon(':/mw.ico'))
        px = window.geometry().x()
        py = window.geometry().y()
        dw = window.width()
        dh = window.height()
        dx = dlg.width()
        dy = dlg.height()
        dlg.setGeometry(px + (dw - dx), py + (dh - dy), dw, dh)
        return dlg.exec()

    @staticmethod
    def dialogMessage(window, title, question):
        dlg = PyQt5.QtWidgets.QMessageBox()
        dlg.setWindowIcon(PyQt5.QtGui.QIcon(':/mw.ico'))
        dlg.setStyleSheet('background-color: rgb(32,32,32); color: rgb(192,192,192)')
        ph = window.geometry().height()
        px = window.geometry().x()
        py = window.geometry().y()
        dw = window.width()
        dh = window.height()
        dlg.setGeometry(px, py + ph - dh, dw, dh)
        return dlg.question(window,
                            title,
                            question,
                            PyQt5.QtWidgets.QMessageBox.Ok
                            | PyQt5.QtWidgets.QMessageBox.Cancel,
                            PyQt5.QtWidgets.QMessageBox.Cancel,
                            )

    @staticmethod
    def dialogInputText(window, title, text, preset):
        dlg = PyQt5.QtWidgets.QInputDialog()
        dlg.setWindowIcon(PyQt5.QtGui.QIcon(':/mw.ico'))
        dlg.setStyleSheet('background-color: rgb(32,32,32); color: rgb(192,192,192)')
        ph = window.geometry().height()
        px = window.geometry().x()
        py = window.geometry().y()
        dw = window.width()
        dh = window.height()
        dlg.setGeometry(px, py + ph - dh, dw, dh)
        return dlg.getText(window,
                           title,
                           text,
                           PyQt5.QtWidgets.QLineEdit.Normal,
                           preset,
                           )

