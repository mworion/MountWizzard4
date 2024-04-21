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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import sys
import os

# external packages
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel, QLineEdit
from PyQt5.QtWidgets import QGridLayout, QPushButton, QFileDialog
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QApplication
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import QDir, Qt
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
            'Startup': None,
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
            'NINA Trace': None,
            'SGPro Trace': None,
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
        res = self.qLists['Full Log'].findItems(item.data(),
                                                Qt.MatchFlag.MatchExactly)
        if len(res) == 0:
            return
        mode = (QAbstractItemView.ScrollHint.PositionAtCenter |
                QAbstractItemView.ScrollHint.EnsureVisible)
        self.qLists['Full Log'].setCurrentItem(res[0])
        self.qLists['Full Log'].scrollToItem(res[0], mode)
        self.setCurrentIndex(0)

    def swapDetail(self, item):
        key = self.getListKey(item.data())
        if key is None:
            return

        qList = self.qLists[key]
        res = qList.findItems(item.data(), Qt.MatchFlag.MatchExactly)
        if len(res) == 0:
            return

        mode = (QAbstractItemView.ScrollHint.PositionAtCenter |
                QAbstractItemView.ScrollHint.EnsureVisible)
        qList.setCurrentItem(res[0])
        qList.scrollToItem(res[0], mode)
        self.setCurrentIndex(list(self.qLists.keys()).index(key))

    @staticmethod
    def getListKey(line):
        if '[H]' in line and 'startup' not in line:
            listKey = 'Header'
        elif 'startup' in line:
            listKey = 'Startup'
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
        elif '[T]' in line and 'nina' in line:
            listKey = 'NINA Trace'
        elif '[T]' in line and 'sgpro' in line:
            listKey = 'SGPro Trace'
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
        if 'imagearray' in line:
            return False
        if key is not None:
            qList = self.qLists[key]
            qList.insertItem(qList.count(), item)

        resetFirst = 'qtmount' in line and '[H]' in line
        return resetFirst


class LifeCycle(QTabWidget):
    def __init__(self):
        QTabWidget.__init__(self)
        layout = QVBoxLayout()
        self.actual = None
        self.first = True
        self.numberLifecycles = 0
        layout.addWidget(self)

    def addEntry(self, line):
        if '[H]' in line and 'loader' in line and self.first:
            # if first line for new header occurs, start a new cat tab
            self.first = False
            self.numberLifecycles += 1
            val = line.split('][')[0].lstrip('[').split('.')[0]
            categoriesTab = Categories()
            categoriesTab.currentChanged.connect(self.setTabsPosition)
            self.actual = categoriesTab
            t = f'[{self.numberLifecycles}] - {val}'
            self.addTab(categoriesTab, t)

    def setTabsPosition(self, actPosition):
        # if changing the tab in a category, all others will be changed, too
        for children in self.children()[0].children():
            children.setCurrentIndex(actPosition)


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        self.lifecycleTab = LifeCycle()

        self.loadButt = QPushButton('Load logging file')
        layout.addWidget(self.loadButt)

        self.filter = QLineEdit()
        self.filter.editingFinished.connect(self.setFilter)
        layout.addWidget(self.filter)

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
        self.lifecycleTab.clear()
        self.lifecycleTab.actual = None
        self.lifecycleTab.numberLifecycles = 0
        numLines = sum(1 for line in open(fileName, 'rb'))
        self.loadButt.setStyleSheet("background-color: rgb(255,255,0);")
        title = 'Load logging file'
        with open(fileName, 'rb') as f:
            for i, line in enumerate(f.readlines()):
                line = line.decode('utf-8', errors='ignore')
                t = title + f'   -   progress: {i +1 } lines loaded from {numLines}'
                t += f'   -   {int((i + 1) / numLines * 100)} %'
                self.loadButt.setText(t)
                self.lifecycleTab.addEntry(line)
                if self.lifecycleTab.actual:
                    if self.lifecycleTab.actual.addEntry(line):
                        self.lifecycleTab.first = True
        self.loadButt.setStyleSheet("background-color: rgb(0,255,0);")
        self.loadButt.setText(title)

    def setFilter(self):
        for i_lifecycle in range(self.lifecycleTab.count()):
            lifecycle = self.lifecycleTab.widget(i_lifecycle)
            for i_category in range(lifecycle.count()):
                category = lifecycle.widget(i_category)
                for i in range(category.count()):
                    item = category.item(i)
                    for filterText in self.filter.text().split(';'):
                        if filterText in item.text() or self.filter.text() == '':
                            item.setHidden(False)
                            break
                        else:
                            item.setHidden(True)


def main():
    app = QApplication(sys.argv)
    screen = Window()
    screen.resize(1600, 1000)
    screen.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
