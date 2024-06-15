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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import json

# external packages
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QTableWidgetItem

# local import
from gui.mainWmixin.astroObjects import AstroObjects
from logic.databaseProcessing.sourceURL import cometSourceURLs


class Comet:
    """
    """

    def __init__(self):
        self.prepareCometTable()
        self.comets = AstroObjects(self,
                                   self.app,
                                   'comet',
                                   cometSourceURLs,
                                   self.ui.listComets,
                                   self.ui.cometSourceList,
                                   self.ui.cometSourceGroup,
                                   self.processComets)

        self.comets.dataLoaded.connect(self.fillCometListName)
        self.ui.cometFilterText.textChanged.connect(self.filterListComets)

        self.ui.progCometSelected.clicked.connect(self.comets.progSelected)
        self.ui.progCometFiltered.clicked.connect(self.comets.progFiltered)
        self.ui.progCometFull.clicked.connect(self.comets.progFull)

    def initConfig(self):
        """
        """
        config = self.app.config['mainW']
        self.ui.cometFilterText.setText(config.get('cometFilterText'))
        self.ui.cometSourceList.setCurrentIndex(config.get('cometSource', 0))
        self.ui.mpcTabWidget.setCurrentIndex(config.get('mpcTab', 0))

    def storeConfig(self):
        """
        """
        config = self.app.config['mainW']
        config['cometSource'] = self.ui.cometSourceList.currentIndex()
        config['cometFilterText'] = self.ui.cometFilterText.text()
        config['mpcTab'] = self.ui.mpcTabWidget.currentIndex()
        return True

    def prepareCometTable(self):
        """
        """
        self.ui.listComets.setRowCount(0)
        hLabels = ['Num', 'Comet Name', 'Test\n[km]']
        hSet = [50, 205, 20]
        self.ui.listComets.setColumnCount(len(hSet))
        self.ui.listComets.setHorizontalHeaderLabels(hLabels)
        for i, hs in enumerate(hSet):
            self.ui.listComets.setColumnWidth(i, hs)
        self.ui.listComets.verticalHeader().setDefaultSectionSize(16)
        self.ui.listComets.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.listComets.setSelectionMode(QAbstractItemView.ExtendedSelection)

    @staticmethod
    def generateName(mp):
        """
        """
        if 'Designation_and_name' in mp:
            name = f'{mp["Designation_and_name"]}'
        elif 'Name' in mp and 'Principal_desig' in mp:
            name = f'{mp["Principal_desig"]} - {mp["Name"]} {mp["Number"]}'
        elif 'Principal_desig' in mp:
            name = f'{mp["Principal_desig"]}'
        elif 'Name' in mp:
            name = f'{mp["Name"]} {mp["Number"]}'
        else:
            name = ''
        return name

    def processComets(self):
        """
        """
        with open(self.comets.dest) as inFile:
            try:
                comets = json.load(inFile)
            except Exception:
                comets = None
        self.comets.objects = {}

        for comet in comets:
            text = self.generateName(comet)
            if not text:
                continue
            self.comets.objects[text] = comet

    def filterListComets(self):
        """
        """
        filterStr = self.ui.cometFilterText.text().lower()

        for row in range(self.ui.listComets.model().rowCount()):
            name = self.ui.listComets.model().index(row, 1).data().lower()
            number = self.ui.listComets.model().index(row, 0).data().lower()
            show = filterStr in number + name
            self.ui.listComets.setRowHidden(row, not show)

    def fillCometListName(self):
        """
        """
        self.ui.listComets.setRowCount(0)
        for number, name in enumerate(self.comets.objects):
            row = self.ui.listComets.rowCount()
            self.ui.listComets.insertRow(row)
            entry = QTableWidgetItem(f'{number:5d}')
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight |
                                   Qt.AlignmentFlag.AlignVCenter)
            self.ui.listComets.setItem(row, 0, entry)
            entry = QTableWidgetItem(name)
            entry.setTextAlignment(Qt.AlignmentFlag.AlignLeft |
                                   Qt.AlignmentFlag.AlignVCenter)
            self.ui.listComets.setItem(row, 1, entry)
        self.filterListComets()
