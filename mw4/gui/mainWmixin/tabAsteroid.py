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
from logic.databaseProcessing.sourceURL import asteroidSourceURLs


class Asteroid:
    """
    """

    def __init__(self):
        self.prepareAsteroidTable()
        self.asteroids = AstroObjects(self,
                                      self.app,
                                      'Asteroids',
                                      asteroidSourceURLs,
                                      self.ui.listAsteroids,
                                      self.ui.asteroidSourceList,
                                      self.ui.asteroidSourceGroup,
                                      self.processAsteroids)

        self.asteroids.dataLoaded.connect(self.fillAsteroidListName)
        self.ui.asteroidFilterText.textChanged.connect(self.filterlistAsteroids)

        # self.ui.progAsteroidsSelected.clicked.connect(self.progAsteroidsSelected)
        # self.ui.progAsteroidsFull.clicked.connect(self.progAsteroidsFull)
        # self.ui.progAsteroidsFiltered.clicked.connect(self.progAsteroidsFiltered)

    def initConfig(self):
        """
        """
        config = self.app.config['mainW']
        self.ui.asteroidFilterText.setText(config.get('asteroidFilterText'))
        self.ui.asteroidSourceList.setCurrentIndex(config.get('asteroidSource', 0))

    def storeConfig(self):
        """
        """
        config = self.app.config['mainW']
        config['asteroidSource'] = self.ui.asteroidSourceList.currentIndex()
        config['asteroidFilterText'] = self.ui.asteroidFilterText.text()
        return True

    def prepareAsteroidTable(self):
        """
        """
        self.ui.listAsteroids.setRowCount(0)
        hLabels = ['Num', 'As Name', 'Test\n[km]']
        hSet = [50, 205, 20]
        self.ui.listAsteroids.setColumnCount(len(hSet))
        self.ui.listAsteroids.setHorizontalHeaderLabels(hLabels)
        for i, hs in enumerate(hSet):
            self.ui.listAsteroids.setColumnWidth(i, hs)
        self.ui.listAsteroids.verticalHeader().setDefaultSectionSize(16)
        self.ui.listAsteroids.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.listAsteroids.setSelectionMode(QAbstractItemView.ExtendedSelection)

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

    def processAsteroids(self):
        """
        """
        with open(self.asteroids.dest) as inFile:
            try:
                comets = json.load(inFile)
            except Exception:
                comets = None
        self.asteroids.objects = {}

        for comet in comets:
            text = self.generateName(comet)
            if not text:
                continue
            self.asteroids.objects[text] = comet

    def filterlistAsteroids(self):
        """
        """
        filterStr = self.ui.cometFilterText.text().lower()

        for row in range(self.ui.listAsteroids.model().rowCount()):
            name = self.ui.listAsteroids.model().index(row, 1).data().lower()
            number = self.ui.listAsteroids.model().index(row, 0).data().lower()
            show = filterStr in number + name
            self.ui.listAsteroids.setRowHidden(row, not show)

    def fillAsteroidListName(self):
        """
        """
        self.ui.listAsteroids.setRowCount(0)
        for number, name in enumerate(self.asteroids.objects):
            row = self.ui.listAsteroids.rowCount()
            self.ui.listAsteroids.insertRow(row)
            entry = QTableWidgetItem(f'{number:5d}')
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight |
                                   Qt.AlignmentFlag.AlignVCenter)
            self.ui.listAsteroids.setItem(row, 0, entry)
            entry = QTableWidgetItem(name)
            entry.setTextAlignment(Qt.AlignmentFlag.AlignLeft |
                                   Qt.AlignmentFlag.AlignVCenter)
            self.ui.listAsteroids.setItem(row, 1, entry)
