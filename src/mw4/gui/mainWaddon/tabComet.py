############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import json
import os
from mw4.gui.mainWaddon.astroObjects import AstroObjects
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.logic.databaseProcessing.sourceURL import cometSourceURLs
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QTableWidgetItem
from typing import Any


class Comet(TabAddon):
    def __init__(self, mainW: Any) -> None:
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
            self.processCometSource,
        )
        self.prepareCometTable()
        self.comets.signals.dataLoaded.connect(self.fillCometListName)
        self.ui.cometFilterText.returnPressed.connect(self.filterListComets)
        self.ui.progCometSelected.clicked.connect(self.comets.progSelected)
        self.ui.progCometFiltered.clicked.connect(self.comets.progFiltered)
        self.ui.progCometFull.clicked.connect(self.comets.progFull)

    def initConfig(self) -> None:
        config = self.app.config["WindowMain"]
        self.ui.cometFilterText.setText(config.get("cometFilterText"))
        self.ui.mpcTabWidget.setCurrentIndex(config.get("mpcTab", 0))
        self.ui.cometSourceList.setCurrentIndex(config.get("cometSource", 0))

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        config["cometSource"] = self.ui.cometSourceList.currentIndex()
        config["cometFilterText"] = self.ui.cometFilterText.text()
        config["mpcTab"] = self.ui.mpcTabWidget.currentIndex()

    def setupIcons(self) -> None:
        self.mainW.wIcon(self.ui.progCometFull, "run")
        self.mainW.wIcon(self.ui.progCometFiltered, "run")
        self.mainW.wIcon(self.ui.progCometSelected, "run")

    def prepareCometTable(self) -> None:
        self.ui.listComets.setRowCount(0)
        hLabels = [
            "Num",
            "Comet Name",
            "Orbit\nType",
            "Perihelion\nDate",
            "Perihelion\nDist [AU]",
            "Eccentr.",
        ]
        hSet = [50, 205, 50, 95, 75, 75]
        self.ui.listComets.setColumnCount(len(hSet))
        self.ui.listComets.setHorizontalHeaderLabels(hLabels)
        self.ui.listComets.horizontalHeader().setSortIndicatorShown(False)
        for i, hs in enumerate(hSet):
            self.ui.listComets.setColumnWidth(i, hs)
        self.ui.listComets.verticalHeader().setDefaultSectionSize(16)
        self.ui.listComets.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.listComets.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

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

    def processCometSource(self) -> None:
        self.ui.listComets.setRowCount(0)
        with open(self.comets.dest) as inFile:
            try:
                comets = json.load(inFile)
            except json.JSONDecodeError as e:
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
        filterStr = self.ui.cometFilterText.text().lower()
        table = self.ui.listComets
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

    def fillCometListName(self) -> None:
        table = self.ui.listComets
        alignRight = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        alignLeft = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        alignCenter = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        table.setUpdatesEnabled(False)
        try:
            table.setRowCount(0)
            table.setRowCount(len(self.comets.objects))
            for row, (name, mp) in enumerate(self.comets.objects.items()):
                cells = {0: (f"{row:5d}", alignRight), 1: (name, alignLeft)}
                if "Orbit_type" in mp:
                    cells[2] = (mp["Orbit_type"], alignCenter)
                if "Year_of_perihelion" in mp:
                    y = mp["Year_of_perihelion"]
                    m = mp["Month_of_perihelion"]
                    d = mp["Day_of_perihelion"]
                    cells[3] = (f"{y:4d}-{m:02d}-{d:02.0f}", alignCenter)
                if "Perihelion_dist" in mp:
                    cells[4] = (f"{mp['Perihelion_dist']:8.4f}", alignCenter)
                if "e" in mp:
                    cells[5] = (f"{mp['e']:8.4f}", alignCenter)
                for column, (text, alignment) in cells.items():
                    entry = QTableWidgetItem(text)
                    entry.setTextAlignment(alignment)
                    table.setItem(row, column, entry)
        finally:
            table.setUpdatesEnabled(True)

        self.comets.dataValid = True
        self.filterListComets()
