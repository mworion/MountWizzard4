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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import json
import os

# external packages
from PySide6.QtCore import Qt, QObject
from PySide6.QtWidgets import QAbstractItemView, QTableWidgetItem

# local import
from gui.mainWaddon.astroObjects import AstroObjects
from logic.databaseProcessing.sourceURL import asteroidSourceURLs


class Asteroid(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.ui = mainW.ui

        self.asteroids = AstroObjects(
            self.mainW,
            "asteroid",
            asteroidSourceURLs,
            self.ui.listAsteroids,
            self.ui.asteroidSourceList,
            self.ui.asteroidSourceGroup,
            self.prepareAsteroidTable,
            self.processAsteroidSource,
        )

        self.asteroids.dataLoaded.connect(self.fillAsteroidListName)
        self.ui.asteroidFilterText.textChanged.connect(self.filterListAsteroids)
        self.ui.progAsteroidSelected.clicked.connect(self.asteroids.progSelected)
        self.ui.progAsteroidFiltered.clicked.connect(self.asteroids.progFiltered)
        self.ui.progAsteroidFull.clicked.connect(self.asteroids.progFull)
        self.app.start3s.connect(self.initConfigDelayedAsteroid)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.ui.asteroidFilterText.setText(config.get("asteroidFilterText"))

    def initConfigDelayedAsteroid(self):
        """ """
        config = self.app.config["mainW"]
        self.ui.asteroidSourceList.setCurrentIndex(config.get("asteroidSource", 0))

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["asteroidSource"] = self.ui.asteroidSourceList.currentIndex()
        config["asteroidFilterText"] = self.ui.asteroidFilterText.text()
        return True

    def setupIcons(self) -> None:
        """ """
        self.mainW.wIcon(self.ui.progAsteroidFull, "run")
        self.mainW.wIcon(self.ui.progAsteroidFiltered, "run")
        self.mainW.wIcon(self.ui.progAsteroidSelected, "run")

    def prepareAsteroidTable(self) -> None:
        """ """
        self.ui.listAsteroids.setRowCount(0)
        hLabels = [
            "Num",
            "Asteroid Name",
            "Orbit\nType",
            "Perihelion\nDist [AU]",
            "Aphelion\nDist [AU]",
            "Eccentr.",
        ]
        hSet = [50, 205, 50, 85, 85, 65]

        self.ui.listAsteroids.setColumnCount(len(hSet))
        self.ui.listAsteroids.setHorizontalHeaderLabels(hLabels)
        for i, hs in enumerate(hSet):
            self.ui.listAsteroids.setColumnWidth(i, hs)
        self.ui.listAsteroids.verticalHeader().setDefaultSectionSize(16)
        self.ui.listAsteroids.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.ui.listAsteroids.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )

    @staticmethod
    def generateName(mp: dict) -> str:
        """ """
        if "Designation_and_name" in mp:
            name = f"{mp['Designation_and_name']}"
        elif "Name" in mp and "Principal_desig" in mp:
            name = f"{mp['Principal_desig']} - {mp['Name']} {mp['Number']}"
        elif "Principal_desig" in mp:
            name = f"{mp['Principal_desig']}"
        elif "Name" in mp:
            name = f"{mp['Name']} {mp['Number']}"
        else:
            name = ""
        return name

    def processAsteroidSource(self) -> None:
        """ """
        self.ui.listAsteroids.setRowCount(0)
        with open(self.asteroids.dest) as inFile:
            try:
                asteroids = json.load(inFile)
            except Exception as e:
                self.mainW.log.error(f"Error {e} loading from {self.asteroids.dest}")
                os.remove(self.asteroids.dest)
                asteroids = []

        self.asteroids.objects.clear()
        for asteroid in asteroids:
            text = self.generateName(asteroid)
            if not text:
                continue
            self.asteroids.objects[text] = asteroid

    def filterListAsteroids(self) -> None:
        """ """
        filterStr = self.ui.asteroidFilterText.text().lower()

        for row in range(self.ui.listAsteroids.model().rowCount()):
            name = self.ui.listAsteroids.model().index(row, 1).data().lower()
            number = self.ui.listAsteroids.model().index(row, 0).data().lower()
            show = filterStr in number + name
            self.ui.listAsteroids.setRowHidden(row, not show)

    def fillAsteroidListName(self) -> None:
        """ """
        self.ui.listAsteroids.setRowCount(0)
        for number, name in enumerate(self.asteroids.objects):
            row = self.ui.listAsteroids.rowCount()
            self.ui.listAsteroids.insertRow(row)

            entry = QTableWidgetItem(f"{number:5d}")
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ui.listAsteroids.setItem(row, 0, entry)
            entry = QTableWidgetItem(name)
            entry.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.ui.listAsteroids.setItem(row, 1, entry)

            if "Orbit_type" in self.asteroids.objects[name]:
                entry = QTableWidgetItem(self.asteroids.objects[name]["Orbit_type"])
                entry.setTextAlignment(
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                )
                self.ui.listAsteroids.setItem(row, 2, entry)

            if "Perihelion_dist" in self.asteroids.objects[name]:
                pdist = f"{self.asteroids.objects[name]['Perihelion_dist']:8.6f}"
                entry = QTableWidgetItem(pdist)
                entry.setTextAlignment(
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                )
                self.ui.listAsteroids.setItem(row, 3, entry)

            if "Aphelion_dist" in self.asteroids.objects[name]:
                adist = f"{self.asteroids.objects[name]['Aphelion_dist']:8.6f}"
                entry = QTableWidgetItem(adist)
                entry.setTextAlignment(
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                )
                self.ui.listAsteroids.setItem(row, 4, entry)

            if "e" in self.asteroids.objects[name]:
                e = f"{self.asteroids.objects[name]['e']:8.5f}"
                entry = QTableWidgetItem(e)
                entry.setTextAlignment(
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                )
                self.ui.listAsteroids.setItem(row, 5, entry)

        self.asteroids.dataValid = True
        self.filterListAsteroids()
