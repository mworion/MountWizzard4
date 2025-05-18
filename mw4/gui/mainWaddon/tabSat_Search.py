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

# external packages
from PySide6.QtCore import Qt, Signal, QRect, QPoint, QObject
from PySide6.QtWidgets import QTableWidgetItem, QAbstractItemView
import numpy as np

# local import
from gui.mainWaddon.astroObjects import AstroObjects
from gui.mainWaddon.satData import SatData
from gui.utilities.qCustomTableWidgetItem import QCustomTableWidgetItem
from logic.databaseProcessing.sourceURL import satSourceURLs
from base.tpool import Worker
from logic.satellites.satellite_calculations import findSunlit, findSatUp
from logic.satellites.satellite_calculations import checkTwilight, calcAppMag
from logic.satellites.satellite_calculations import findRangeRate
from gui.utilities.toolsQtWidget import changeStyleDynamic


class SatSearch(QObject, SatData):
    """ """

    setSatListItem = Signal(int, int, object)

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.worker: Worker = None

        SatData.satellites = AstroObjects(
            self.mainW,
            "satellite",
            satSourceURLs,
            self.ui.listSats,
            self.ui.satSourceList,
            self.ui.satSourceGroup,
            self.prepareSatTable,
            self.processSatelliteSource,
        )

        self.satellites.dataLoaded.connect(self.fillSatListName)
        self.ui.satFilterText.textChanged.connect(self.filterListSats)
        self.ui.satIsSunlit.clicked.connect(self.filterListSats)
        self.ui.satIsUp.clicked.connect(self.filterListSats)
        self.ui.satRemoveSO.clicked.connect(self.filterListSats)
        self.ui.satTwilight.activated.connect(self.filterListSats)
        self.ui.satUpTimeWindow.valueChanged.connect(self.filterListSats)
        self.setSatListItem.connect(self.setListSatsEntry)
        self.app.update1s.connect(self.calcSatListDynamic)
        self.ui.progSatFull.clicked.connect(self.satellites.progFull)
        self.ui.progSatFiltered.clicked.connect(self.satellites.progFiltered)
        self.ui.progSatSelected.clicked.connect(self.satellites.progSelected)

    def initConfig(self):
        """ """
        config = self.app.config["mainW"]
        self.ui.satFilterText.setText(config.get("satFilterText"))
        self.ui.satTwilight.setCurrentIndex(config.get("satTwilight", 4))
        self.ui.autoSwitchTrack.setChecked(config.get("autoSwitchTrack", False))
        self.ui.satCyclicUpdates.setChecked(config.get("satCyclicUpdates", False))
        self.ui.satIsSunlit.setChecked(config.get("satIsSunlit", False))
        self.ui.satRemoveSO.setChecked(config.get("satRemoveSO", False))
        self.ui.satIsUp.setChecked(config.get("satIsUp", False))
        self.ui.satUpTimeWindow.setValue(config.get("satUpTimeWindow", 2))
        self.ui.satAltitudeMin.setValue(config.get("satAltitudeMin", 30))
        self.ui.satSourceList.setCurrentIndex(config.get("satSource", 0))

    def storeConfig(self):
        """ """
        config = self.app.config["mainW"]
        config["satSource"] = self.ui.satSourceList.currentIndex()
        config["satTwilight"] = self.ui.satTwilight.currentIndex()
        config["satFilterText"] = self.ui.satFilterText.text()
        config["autoSwitchTrack"] = self.ui.autoSwitchTrack.isChecked()
        config["satCyclicUpdates"] = self.ui.satCyclicUpdates.isChecked()
        config["satIsSunlit"] = self.ui.satIsSunlit.isChecked()
        config["satRemoveSO"] = self.ui.satRemoveSO.isChecked()
        config["satIsUp"] = self.ui.satIsUp.isChecked()
        config["satUpTimeWindow"] = self.ui.satUpTimeWindow.value()
        config["satAltitudeMin"] = self.ui.satAltitudeMin.value()

    def prepareSatTable(self):
        """ """
        self.ui.listSats.setColumnCount(9)
        hLabels = [
            "Num",
            "Satellite Name",
            "Dist\n[km]",
            "Rad v\n[km/s]",
            "Lat v\n[deg/s]",
            "Lon v\n[deg/s]",
            "Time\n[H:M]",
            "Sat\n[mag]",
        ]
        hSet = [50, 205, 50, 50, 45, 45, 50, 45, 0]
        self.ui.listSats.setColumnCount(len(hSet))
        self.ui.listSats.setHorizontalHeaderLabels(hLabels)
        for i, hs in enumerate(hSet):
            self.ui.listSats.setColumnWidth(i, hs)
        self.ui.listSats.verticalHeader().setDefaultSectionSize(16)
        self.ui.listSats.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.listSats.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def processSatelliteSource(self):
        """ """
        self.ui.listSats.setRowCount(0)
        loader = self.app.mount.obsSite.loader
        satellites = loader.tle_file(str(self.satellites.dest))
        self.satellites.objects.clear()
        for sat in satellites:
            self.satellites.objects[sat.name] = sat

    def filterListSats(self):
        """ """
        filterStr = self.ui.satFilterText.text().lower()
        satIsUp = self.ui.satIsUp
        satIsSunlit = self.ui.satIsSunlit

        checkIsUp = satIsUp.isChecked() and satIsUp.isEnabled()
        checkIsSunlit = satIsSunlit.isChecked() and satIsSunlit.isEnabled()
        checkRemoveSO = self.ui.satRemoveSO.isChecked()
        selectTwilight = self.ui.satTwilight.currentIndex()

        for row in range(self.ui.listSats.model().rowCount()):
            name = self.ui.listSats.model().index(row, 1).data().lower()
            number = self.ui.listSats.model().index(row, 0).data().lower()
            show = filterStr in number + name
            if checkIsUp:
                show = show and self.ui.listSats.model().index(row, 6).data()
            if checkIsSunlit:
                show = show and self.ui.listSats.model().index(row, 7).data()
            if checkRemoveSO:
                show = show and "starlink" not in name
                show = show and "oneweb" not in name
                show = show and "globalstar" not in name
                show = show and "navstar" not in name
            if selectTwilight < 4:
                value = self.ui.listSats.model().index(row, 8).data()
                actTwilight = int(value) if value is not None else 5
                show = show and actTwilight <= selectTwilight

            self.ui.listSats.setRowHidden(row, not show)
        satName = self.ui.satelliteName.text()
        self.mainW.positionCursorInTable(self.ui.listSats, satName)

    def setListSatsEntry(self, row, col, entry):
        """ """
        self.ui.listSats.setItem(row, col, entry)

    def updateListSats(
        self, row, satParam, isUp=None, isSunlit=None, appMag=None, twilight=None
    ):
        """ """
        entry = QTableWidgetItem(f"{satParam[0]:5.0f}")
        entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setSatListItem.emit(row, 2, entry)

        entry = QTableWidgetItem(f"{satParam[1]:+2.2f}")
        entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setSatListItem.emit(row, 3, entry)

        entry = QTableWidgetItem(f"{satParam[2]:+2.2f}")
        entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setSatListItem.emit(row, 4, entry)

        entry = QTableWidgetItem(f"{satParam[3]:+2.2f}")
        entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setSatListItem.emit(row, 5, entry)

        if isUp is not None:
            if isUp[0]:
                t = self.mainW.convertTime(isUp[1][0], "%H:%M")
            else:
                t = ""

            entry = QTableWidgetItem(t)
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.setSatListItem.emit(row, 6, entry)

        if isSunlit is not None:
            if isSunlit:
                value = f"{appMag:1.1f}"
            else:
                value = ""

            entry = QCustomTableWidgetItem(value)
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.setSatListItem.emit(row, 7, entry)

        if twilight is not None:
            entry = QTableWidgetItem(f"{twilight:1.0f}")
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.setSatListItem.emit(row, 8, entry)

    def calcSatListDynamic(self):
        """ """
        if self.ui.satTabWidget.currentIndex() != 0:
            return
        if self.ui.mainTabWidget.currentIndex() != 5:
            return
        if not self.satellites.dataValid:
            return

        satTab = self.ui.listSats
        loc = self.app.mount.obsSite.location
        eph = self.app.ephemeris
        ts = self.app.mount.obsSite.ts
        timeNow = ts.now()
        viewPortRect = QRect(QPoint(0, 0), satTab.viewport().size())

        for row in range(satTab.rowCount()):
            rect = satTab.visualRect(satTab.model().index(row, 0))
            if not viewPortRect.intersects(rect):
                continue
            if satTab.isRowHidden(row):
                continue

            name = satTab.model().index(row, 1).data()
            sat = self.satellites.objects[name]
            satParam = findRangeRate(sat, loc, timeNow)
            if not np.isnan(satParam[0]) and sat:
                isSunlit = findSunlit(sat, eph, timeNow)
                satRange = satParam[0]
                if isSunlit:
                    appMag = calcAppMag(sat, loc, eph, satRange, timeNow)
                else:
                    appMag = 99
            else:
                isSunlit = False
                appMag = 99
            self.updateListSats(row, satParam, isSunlit=isSunlit, appMag=appMag)

    def checkSatOk(self, sat, tEnd):
        """ """
        msg = sat.at(tEnd).message
        if msg:
            self.mainW.log.warning(f"{sat.name} caused SGP4: [{msg}]")
            return False
        return True

    def calcSat(self, sat, row, loc, timeNow, timeNext, altMin, eph):
        """ """
        satParam = findRangeRate(sat, loc, timeNow)
        if not np.isnan(satParam).any():
            isSunlit = findSunlit(sat, eph, timeNow)
            isUp = findSatUp(sat, loc, timeNow, timeNext, altMin)
            fitTwilight = checkTwilight(eph, loc, isUp)
            satRange = satParam[0]
            if isSunlit:
                appMag = calcAppMag(sat, loc, eph, satRange, timeNow)
            else:
                appMag = 99
        else:
            fitTwilight = 4
            isSunlit = False
            isUp = False, []
            appMag = 99
        self.updateListSats(row, satParam, isUp, isSunlit, appMag, fitTwilight)

    def workerCalcSatList(self):
        """ """
        satTab = self.ui.listSats
        loc = self.app.mount.obsSite.location
        ts = self.app.mount.obsSite.ts
        timeNow = ts.now()
        timeWin = self.ui.satUpTimeWindow.value()
        timeNext = ts.tt_jd(timeNow.tt + timeWin * 3600 / 86400)
        altMin = self.ui.satAltitudeMin.value()
        eph = self.app.ephemeris
        numSats = satTab.rowCount()

        for row in range(numSats):
            finished = (row + 1) / numSats * 100
            t = f"Filter - processed: {finished:3.0f}%"
            self.ui.satFilterGroup.setTitle(t)
            name = satTab.model().index(row, 1).data()
            sat = self.satellites.objects[name]
            if not self.checkSatOk(sat, timeNext):
                continue
            self.calcSat(sat, row, loc, timeNow, timeNext, altMin, eph)

        t = "Filter - processed: 100%"
        self.ui.satFilterGroup.setTitle(t)
        changeStyleDynamic(self.ui.satFilterGroup, "running", False)

    def calcSatList(self):
        """ """
        title = "Setup " + self.mainW.timeZoneString()
        self.ui.satSetupGroup.setTitle(title)
        self.worker = Worker(self.workerCalcSatList)
        self.worker.signals.finished.connect(self.filterListSats)
        changeStyleDynamic(self.ui.satFilterGroup, "running", True)
        self.app.threadPool.start(self.worker)

    def fillSatListName(self):
        """ """
        self.ui.listSats.setRowCount(0)
        for name in self.satellites.objects:
            number = self.satellites.objects[name].model.satnum
            row = self.ui.listSats.rowCount()
            self.ui.listSats.insertRow(row)
            entry = QTableWidgetItem(f"{number:5d}")
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ui.listSats.setItem(row, 0, entry)
            entry = QTableWidgetItem(name)
            entry.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.ui.listSats.setItem(row, 1, entry)
        self.satellites.dataValid = True
        self.calcSatList()
