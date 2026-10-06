# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
import os
from mw4.gui.mainWaddon.astroObjects import AstroObjects
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.logic.databaseProcessing.sourceURL import asteroidSourceURLs
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QTableWidgetItem
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mw4.gui.mainWindow.mainWindow import MainWindow


class Asteroid(TabAddon):
    def __init__(self, mainW: "MainWindow") -> None:
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
            self.processAsteroidSource,
        )

        self.asteroids.signals.dataLoaded.connect(self.fillAsteroidListName)
        self.prepareAsteroidTable()
        self.ui.asteroidFilterText.returnPressed.connect(self.filterListAsteroids)
        self.ui.progAsteroidSelected.clicked.connect(self.asteroids.progSelected)
        self.ui.progAsteroidFiltered.clicked.connect(self.asteroids.progFiltered)
        self.ui.progAsteroidFull.clicked.connect(self.asteroids.progFull)

    def initConfig(self) -> None:
        config = self.app.config["WindowMain"]
        self.ui.asteroidFilterText.setText(config.get("asteroidFilterText"))
        self.ui.asteroidSourceList.setCurrentIndex(config.get("asteroidSource", 0))

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        config["asteroidSource"] = self.ui.asteroidSourceList.currentIndex()
        config["asteroidFilterText"] = self.ui.asteroidFilterText.text()

    def setupIcons(self) -> None:
        self.mainW.wIcon(self.ui.progAsteroidFull, "run")
        self.mainW.wIcon(self.ui.progAsteroidFiltered, "run")
        self.mainW.wIcon(self.ui.progAsteroidSelected, "run")

    def prepareAsteroidTable(self) -> None:
        self.ui.listAsteroids.setRowCount(0)
        hLabels = [
            "Num",
            "Asteroid Name",
            "Orbit\nType",
            "Perihelion\nDist [AU]",
            "Aphelion\nDist [AU]",
            "Eccentr.",
        ]
        hSet = [50, 205, 70, 75, 75, 75]

        self.ui.listAsteroids.setColumnCount(len(hSet))
        self.ui.listAsteroids.horizontalHeader().setSortIndicatorShown(False)
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
        self.ui.listAsteroids.setRowCount(0)
        with open(self.asteroids.dest) as inFile:
            try:
                asteroids = json.load(inFile)
            except json.JSONDecodeError as e:
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
        filterStr = self.ui.asteroidFilterText.text().lower()
        table = self.ui.listAsteroids
        model = table.model()
        table.setUpdatesEnabled(False)
        try:
            for row in range(model.rowCount()):
                name = model.index(row, 1).data().lower()
                number = model.index(row, 0).data().lower()
                show = filterStr in number + name
                table.setRowHidden(row, not show)
        finally:
            table.setUpdatesEnabled(True)

    def fillAsteroidListName(self) -> None:
        table = self.ui.listAsteroids
        alignRight = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        alignLeft = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        alignCenter = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        table.setUpdatesEnabled(False)
        try:
            table.setRowCount(0)
            table.setRowCount(len(self.asteroids.objects))
            for row, (name, mp) in enumerate(self.asteroids.objects.items()):
                cells = {0: (f"{row:5d}", alignRight), 1: (name, alignLeft)}
                if "Orbit_type" in mp:
                    cells[2] = (mp["Orbit_type"], alignCenter)
                if "Perihelion_dist" in mp:
                    cells[3] = (f"{mp['Perihelion_dist']:8.4f}", alignCenter)
                if "Aphelion_dist" in mp:
                    cells[4] = (f"{mp['Aphelion_dist']:8.4f}", alignCenter)
                if "e" in mp:
                    cells[5] = (f"{mp['e']:8.4f}", alignCenter)
                for column, (text, alignment) in cells.items():
                    entry = QTableWidgetItem(text)
                    entry.setTextAlignment(alignment)
                    table.setItem(row, column, entry)
        finally:
            table.setUpdatesEnabled(True)

        self.asteroids.dataValid = True
        self.filterListAsteroids()
