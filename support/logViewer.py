############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# log viewer for analysing mountwizzard4 lof files
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import sys
import os

# external packages
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QLabel
from PyQt5.QtWidgets import QTextBrowser, QGridLayout, QPushButton, QFileDialog
from PyQt5.QtCore import QDir


class QCustomTextBrowser(QTextBrowser):
    def __init__(self):
        QTextBrowser.__init__(self)
        self.setLineWrapMode(0)
        self.setFontPointSize(12)
        self.setFontFamily('Courier')


class Categories(QTabWidget):
    def __init__(self):
        QTabWidget.__init__(self)
        layout = QVBoxLayout()

        self.tbHeader = QCustomTextBrowser()
        self.tbCritical = QCustomTextBrowser()
        self.tbError = QCustomTextBrowser()
        self.tbWarn = QCustomTextBrowser()
        self.tbInfo = QCustomTextBrowser()
        self.tbDebug = QCustomTextBrowser()
        self.tbUI = QCustomTextBrowser()
        self.tbMount = QCustomTextBrowser()
        self.tbINDI = QCustomTextBrowser()
        self.tbASCOM = QCustomTextBrowser()
        self.tbALPACA = QCustomTextBrowser()
        self.tbRest = QCustomTextBrowser()

        self.addTab(self.tbHeader, 'Header')
        self.addTab(self.tbCritical, 'Critical')
        self.addTab(self.tbError, 'Errors')
        self.addTab(self.tbWarn, 'Warnings')
        self.addTab(self.tbInfo, 'Info')
        self.addTab(self.tbDebug, 'Debug')
        self.addTab(self.tbUI, 'UI Trace')
        self.addTab(self.tbMount, 'Mount Trace')
        self.addTab(self.tbINDI, 'INDI Trace')
        self.addTab(self.tbASCOM, 'ASCOM Trace')
        self.addTab(self.tbALPACA, 'ALPACA Trace')
        self.addTab(self.tbRest, 'Other traces')
        layout.addWidget(self)

    def addEntry(self, line):
        if '[H]' in line:
            self.tbHeader.insertPlainText(line)
        elif '[C]' in line:
            self.tbCritical.insertPlainText(line)
        elif '[E]' in line:
            self.tbError.insertPlainText(line)
        elif '[W]' in line:
            self.tbWarn.insertPlainText(line)
        elif '[I]' in line:
            self.tbInfo.insertPlainText(line)
        elif '[D]' in line:
            self.tbDebug.insertPlainText(line)
        elif '[U]' in line:
            if 'qt_scrollarea_viewport' in line:
                return
            if 'QComboBoxPrivateContainerClassWindow' in line:
                return
            if 'Click Object  : []' in line:
                return
            self.tbUI.insertPlainText(line)
        elif '[T][  connection.py]' in line:
            self.tbMount.insertPlainText(line)
        elif '[T]' in line and 'indi' in line:
            self.tbINDI.insertPlainText(line)
        elif '[T]' in line and 'ascom' in line:
            self.tbASCOM.insertPlainText(line)
        elif '[T]' in line and 'alpaca' in line:
            self.tbALPACA.insertPlainText(line)
        elif '[T]' in line:
            self.tbRest.insertPlainText(line)


class LifeCycle(QTabWidget):
    def __init__(self):
        QTabWidget.__init__(self)
        layout = QVBoxLayout()
        self.actual = None
        self.first = True
        self.numberLifecycles = 0
        layout.addWidget(self)

    def addEntry(self, line):
        if '[H]' in line and self.first:
            self.first = False
            self.numberLifecycles += 1
            val = line.split('][')[0].lstrip('[').split('.')[0]
            categoriesTab = Categories()
            self.actual = categoriesTab
            t = f'[{self.numberLifecycles}] - {val}'
            self.addTab(categoriesTab, t)

        elif '[H]' in line and not self.first:
            pass

        elif '[H]' not in line and not self.first:
            self.first = True


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        self.lifecycleTab = LifeCycle()

        self.loadButt = QPushButton('Load logging file')
        layout.addWidget(self.loadButt)
        self.fileName = QLabel()
        layout.addWidget(self.fileName)
        layout.addWidget(self.lifecycleTab)
        self.loadButt.clicked.connect(self.selectFile)

    def selectFile(self):
        dlg = QFileDialog()
        dlg.setViewMode(QFileDialog.List)
        dlg.setModal(True)
        dlg.setFilter(QDir.Files)
        dlg.setWindowTitle('Please select log file for inspection')
        dlg.setNameFilter('log files (*.log)')
        dlg.setDirectory(os.getcwd())
        dlg.setFileMode(QFileDialog.ExistingFile)

        if not dlg.exec_():
            return

        fileName = dlg.selectedFiles()[0]
        self.fileName.setText(fileName)
        self.processFile(fileName)

    def processFile(self, fileName):
        if not os.path.isfile(fileName):
            return
        numLines = sum(1 for line in open(fileName, 'rb'))
        self.loadButt.setStyleSheet("background-color: rgb(255,255,0);")
        with open(fileName, 'rb') as f:
            for i, line in enumerate(f.readlines()):
                QApplication.processEvents()
                line = line.decode('utf-8', errors='ignore')
                title = 'Load logging file'
                t = title + f'   -   progress: {i +1 } lines loaded from {numLines}'
                t += f'   -   {int((i + 1) / numLines * 100)} %'
                self.loadButt.setText(t)
                self.lifecycleTab.addEntry(line)
                self.lifecycleTab.actual.addEntry(line)
        self.loadButt.setStyleSheet("background-color: rgb(0,255,0);")
        self.loadButt.setText(title)


def main():
    app = QApplication(sys.argv)
    screen = Window()
    screen.resize(1600, 1000)
    screen.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
