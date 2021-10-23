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
from PyQt5.QtWidgets import QGridLayout, QPushButton, QFileDialog
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import QDir, QSize, Qt
from PyQt5.QtGui import QFont


class QCustomListWidget(QListWidget):
    def __init__(self):
        QListWidget.__init__(self)
        self.setSizeAdjustPolicy(QListWidget.AdjustToContents)


class QCustomListWidgetItem(QListWidgetItem):
    def __init__(self):
        QListWidgetItem.__init__(self)
        font = QFont()
        font.setFamily('Courier')
        font.setPointSize(12)
        self.setFont(font)


class Categories(QTabWidget):
    def __init__(self):
        QTabWidget.__init__(self)
        layout = QVBoxLayout()
        self.qLists = {
            'Full Log': None,
            'Header': None,
            'Critical': None,
            'Errors': None,
            'Warnings': None,
            'Info': None,
            'Debug': None,
            'UI Trace': None,
            'Mount Trace': None,
            'INDI Trace': None,
            'ASCOM Trace': None,
            'ALPACA Trace': None,
            'Other traces': None,
        }

        for listN in self.qLists:
            self.qLists[listN] = QCustomListWidget()
            if listN == 'Full Log':
                self.qLists[listN].doubleClicked.connect(self.swapDetail)
            else:
                self.qLists[listN].doubleClicked.connect(self.swapFull)
            self.addTab(self.qLists[listN], listN)
        layout.addWidget(self)

    def swapFull(self, item):
        res = self.qLists['Full Log'].findItems(item.data(), Qt.MatchExactly)
        if len(res) == 0:
            return
        mode = QCustomListWidget.PositionAtCenter | QCustomListWidget.EnsureVisible
        self.qLists['Full Log'].setCurrentItem(res[0])
        self.qLists['Full Log'].scrollToItem(res[0], mode)
        self.setCurrentIndex(0)

    def swapDetail(self, item):
        key = self.getListKey(item.data())
        if key is None:
            return

        qList = self.qLists[key]
        res = qList.findItems(item.data(), Qt.MatchExactly)
        if len(res) == 0:
            return

        mode = QCustomListWidget.PositionAtCenter | QCustomListWidget.EnsureVisible
        qList.setCurrentItem(res[0])
        qList.scrollToItem(res[0], mode)
        self.setCurrentIndex(list(self.qLists.keys()).index(key))

    @staticmethod
    def getListKey(line):
        if '[H]' in line:
            listKey = 'Header'
        elif '[C]' in line:
            listKey = 'Critical'
        elif '[E]' in line:
            listKey = 'Errors'
        elif '[W]' in line:
            listKey = 'Warnings'
        elif '[I]' in line:
            listKey = 'Info'
        elif '[D]' in line:
            listKey = 'Debug'
        elif '[U]' in line:
            if 'qt_scrollarea_viewport' in line:
                return None
            if 'QComboBoxPrivateContainerClassWindow' in line:
                return None
            if 'Click Object  : []' in line:
                return None
            listKey = 'UI Trace'
        elif '[T][  connection.py]' in line:
            listKey = 'Mount Trace'
        elif '[T]' in line and 'indi' in line:
            listKey = 'INDI Trace'
        elif '[T]' in line and 'ascom' in line:
            listKey = 'ASCOM Trace'
        elif '[T]' in line and 'alpaca' in line:
            listKey = 'ALPACA Trace'
        elif '[T]' in line:
            listKey = 'Other traces'
        else:
            listKey = None
        return listKey

    def addEntry(self, line):
        itemF = QCustomListWidgetItem()
        itemF.setText(line.strip('\n'))
        self.qLists['Full Log'].insertItem(self.qLists['Full Log'].count(), itemF)

        item = QCustomListWidgetItem()
        item.setText(line.strip('\n'))
        key = self.getListKey(line)
        if key is not None:
            qList = self.qLists[key]
            qList.insertItem(qList.count(), item)


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
