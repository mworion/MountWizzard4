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
from gui.utilities.toolsQtWidget import MWidget
from logic.databaseProcessing.sourceURL import cometSourceURLs


class Comet(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.ui = mainW.ui

        self.comets = AstroObjects(
            self.mainW,
            "comet",
            cometSourceURLs,
            self.ui.listComets,
            self.ui.cometSourceList,
            self.ui.cometSourceGroup,
            self.prepareCometTable,
            self.processCometSource,
        )

        self.comets.dataLoaded.connect(self.fillCometListName)
        self.ui.cometFilterText.textChanged.connect(self.filterListComets)
        self.ui.progCometSelected.clicked.connect(self.comets.progSelected)
        self.ui.progCometFiltered.clicked.connect(self.comets.progFiltered)
        self.ui.progCometFull.clicked.connect(self.comets.progFull)
        self.app.start3s.connect(self.initConfigDelayedComet)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.ui.cometFilterText.setText(config.get("cometFilterText"))
        self.ui.mpcTabWidget.setCurrentIndex(config.get("mpcTab", 0))

    def initConfigDelayedComet(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.ui.cometSourceList.setCurrentIndex(config.get("cometSource", 0))

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["cometSource"] = self.ui.cometSourceList.currentIndex()
        config["cometFilterText"] = self.ui.cometFilterText.text()
        config["mpcTab"] = self.ui.mpcTabWidget.currentIndex()

    def setupIcons(self) -> None:
        """ """
        MWidget.wIcon(self.ui.progCometFull, "run")
        MWidget.wIcon(self.ui.progCometFiltered, "run")
        MWidget.wIcon(self.ui.progCometSelected, "run")

    def prepareCometTable(self) -> None:
        """ """
        self.ui.listComets.setRowCount(0)
        hLabels = [
            "Num",
            "Comet Name",
            "Orbit\nType",
            "Perihelion\nDate",
            "Perihelion\nDist [AU]",
            "Eccentr.",
        ]
        hSet = [50, 205, 50, 85, 85, 65]
        self.ui.listComets.setColumnCount(len(hSet))
        self.ui.listComets.setHorizontalHeaderLabels(hLabels)
        for i, hs in enumerate(hSet):
            self.ui.listComets.setColumnWidth(i, hs)
        self.ui.listComets.verticalHeader().setDefaultSectionSize(16)
        self.ui.listComets.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.listComets.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

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

    def processCometSource(self) -> None:
        """ """
        self.ui.listComets.setRowCount(0)
        with open(self.comets.dest) as inFile:
            try:
                comets = json.load(inFile)
            except Exception as e:
                self.mainW.log.error(f"Error {e} loading from {self.comets.dest}")
                os.remove(self.comets.dest)
                comets = []

        self.comets.objects.clear()
        for comet in comets:
            text = self.generateName(comet)
            if not text:
                continue
            self.comets.objects[text] = comet

    def filterListComets(self) -> None:
        """ """
        filterStr = self.ui.cometFilterText.text().lower()
        model = self.ui.listComets.model()

        for row in range(model.rowCount()):
            name = model.index(row, 1).data().lower()
            number = model.index(row, 0).data().lower()
            show = filterStr in number + name
            self.ui.listComets.setRowHidden(row, not show)

    def fillCometListName(self) -> None:
        """ """
        self.ui.listComets.setRowCount(0)
        for number, name in enumerate(self.comets.objects):
            row = self.ui.listComets.rowCount()
            self.ui.listComets.insertRow(row)

            entry = QTableWidgetItem(f"{number:5d}")
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ui.listComets.setItem(row, 0, entry)

            entry = QTableWidgetItem(name)
            entry.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.ui.listComets.setItem(row, 1, entry)

            if "Orbit_type" in self.comets.objects[name]:
                entry = QTableWidgetItem(self.comets.objects[name]["Orbit_type"])
                entry.setTextAlignment(
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                )
                self.ui.listComets.setItem(row, 2, entry)

            if "Year_of_perihelion" in self.comets.objects[name]:
                y = self.comets.objects[name]["Year_of_perihelion"]
                m = self.comets.objects[name]["Month_of_perihelion"]
                d = self.comets.objects[name]["Day_of_perihelion"]
                date = f"{y:4d}-{m:02d}-{d:02.0f}"
                entry = QTableWidgetItem(date)
                entry.setTextAlignment(
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                )
                self.ui.listComets.setItem(row, 3, entry)

            if "Perihelion_dist" in self.comets.objects[name]:
                dist = f"{self.comets.objects[name]['Perihelion_dist']:8.6f}"
                entry = QTableWidgetItem(dist)
                entry.setTextAlignment(
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                )
                self.ui.listComets.setItem(row, 4, entry)

            if "e" in self.comets.objects[name]:
                e = f"{self.comets.objects[name]['e']:8.5f}"
                entry = QTableWidgetItem(e)
                entry.setTextAlignment(
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                )
                self.ui.listComets.setItem(row, 5, entry)

        self.comets.dataValid = True
        self.filterListComets()
