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
import numpy as np
from mw4.base.tpool import Worker
from mw4.gui.mainWaddon.astroObjects import AstroObjects
from mw4.gui.mainWaddon.satData import SatData
from mw4.gui.utilities.nativeQt.qtCustomTableWidgetItem import QCustomTableWidgetItem
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, positionCursorInTable
from mw4.logic.databaseProcessing.sourceURL import satSourceURLs
from mw4.logic.satellites.satellite_calculations import (
    calcAppMag,
    checkTwilight,
    findRangeRate,
    findSatUp,
    findSunlit,
)
from PySide6.QtCore import QMutex, QObject, QPoint, QRect, Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QTableWidgetItem
from skyfield.api import EarthSatellite, Time
from skyfield.toposlib import GeographicPosition
from typing import Any


class SatSearchSignals(QObject):
    setSatListItem = Signal(int, int, object)
    setSatListRowHidden = Signal(int, bool)
    setSatGroupTitle = Signal(str, bool)


class SatSearch(SatData):
    def __init__(self, mainW: Any) -> None:
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.signals = SatSearchSignals()
        self.dataValid: bool = False
        self.filterStr: str = ""
        self.checkRemoveSO: bool = False
        self.checkRemoveK: bool = False
        self.checkRemoveDQ: bool = False
        self.mutexCalc: QMutex = QMutex()
        self.workerCalcSatList: Worker | None = None
        SatData.satellites = AstroObjects(
            self.mainW,
            "satellite",
            satSourceURLs,
            self.ui.listSats,
            self.ui.satSourceList,
            self.ui.satSourceGroup,
            self.processSatelliteSource,
        )
        self.prepareSatTable()
        self.satellites.signals.dataLoaded.connect(self.fillSatListName)
        self.ui.satFilterText.returnPressed.connect(self.fillSatListName)
        self.ui.satRemoveSO.clicked.connect(self.fillSatListName)
        self.ui.satRemoveK.clicked.connect(self.fillSatListName)
        self.ui.satRemoveDQ.clicked.connect(self.fillSatListName)
        self.ui.satIsSunlit.clicked.connect(self.fillSatListName)
        self.ui.satTwilight.activated.connect(self.fillSatListName)
        self.signals.setSatListItem.connect(self.setListSatsEntry)
        self.signals.setSatGroupTitle.connect(self.updateTitleRunning)
        self.signals.setSatListRowHidden.connect(self.updateVisibilityRow)
        self.ui.progSatFull.clicked.connect(self.satellites.progFull)
        self.ui.progSatFiltered.clicked.connect(self.satellites.progFiltered)
        self.ui.progSatSelected.clicked.connect(self.satellites.progSelected)
        self.app.timeMgr.update3s.connect(self.calcSatListDynamic)

    def initConfig(self) -> None:
        config = self.app.config["WindowMain"]
        self.ui.satFilterText.setText(config.get("satFilterText"))
        self.ui.satTwilight.setCurrentIndex(config.get("satTwilight", 5))
        self.ui.satIsSunlit.setChecked(config.get("satIsSunlit", False))
        self.ui.satRemoveSO.setChecked(config.get("satRemoveSO", False))
        self.ui.satRemoveK.setChecked(config.get("satRemoveK", False))
        self.ui.satRemoveDQ.setChecked(config.get("satRemoveDQ", False))
        self.ui.satAltitudeMin.setValue(config.get("satAltitudeMin", 30))
        self.ui.satSourceList.setCurrentIndex(config.get("satSource", 0))

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        config["satSource"] = self.ui.satSourceList.currentIndex()
        config["satTwilight"] = self.ui.satTwilight.currentIndex()
        config["satFilterText"] = self.ui.satFilterText.text()
        config["satIsSunlit"] = self.ui.satIsSunlit.isChecked()
        config["satRemoveSO"] = self.ui.satRemoveSO.isChecked()
        config["satRemoveK"] = self.ui.satRemoveK.isChecked()
        config["satRemoveDQ"] = self.ui.satRemoveDQ.isChecked()
        config["satAltitudeMin"] = self.ui.satAltitudeMin.value()

    def prepareSatTable(self) -> None:
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
        hSet = [50, 200, 50, 50, 50, 50, 50, 45, 0]
        self.ui.listSats.setColumnCount(len(hSet))
        self.ui.listSats.setHorizontalHeaderLabels(hLabels)
        for i, hs in enumerate(hSet):
            self.ui.listSats.setColumnWidth(i, hs)
        self.ui.listSats.verticalHeader().setDefaultSectionSize(16)
        self.ui.listSats.horizontalHeader().setSortIndicatorShown(False)
        self.ui.listSats.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.listSats.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def processSatelliteSource(self) -> None:
        self.ui.listSats.setRowCount(0)
        loader = self.app.dReg["mount"].obsSite.loader
        satellites = loader.tle_file(str(self.satellites.dest))
        self.satellites.objects.clear()
        for sat in satellites:
            self.satellites.objects[sat.name] = sat

    def setListSatsEntry(self, row: int, col: int, entry: str) -> None:
        self.ui.listSats.setItem(row, col, entry)

    def updateListSats(
        self,
        row: int,
        satParam: tuple[float, float, float, float],
        isUp: list = [],
        isSunlit: bool = False,
        appMag: float= 99,
        twilight: int = 4,
    ) -> None:
        entry = QTableWidgetItem(f"{satParam[0]:5.0f}")
        entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.signals.setSatListItem.emit(row, 2, entry)

        entry = QTableWidgetItem(f"{satParam[1]:+2.2f}")
        entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.signals.setSatListItem.emit(row, 3, entry)

        entry = QTableWidgetItem(f"{satParam[2]:+2.2f}")
        entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.signals.setSatListItem.emit(row, 4, entry)

        entry = QTableWidgetItem(f"{satParam[3]:+2.2f}")
        entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.signals.setSatListItem.emit(row, 5, entry)

        if isUp:
            t = self.app.timeMgr.convertTime(isUp[0], "%H:%M") if len(isUp) else ""
            entry = QTableWidgetItem(t)
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.signals.setSatListItem.emit(row, 6, entry)

        if isSunlit:
            value = f"{appMag:1.1f}" if isSunlit else ""
            entry = QCustomTableWidgetItem(value)
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.signals.setSatListItem.emit(row, 7, entry)

        if twilight is not None:
            entry = QTableWidgetItem(f"{twilight:1.0f}")
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.signals.setSatListItem.emit(row, 8, entry)

    def calcSatListDynamic(self) -> None:
        if self.ui.satTabWidget.currentIndex() != 0 or not self.ui.satTabWidget.isVisible():
            return
        if not self.dataValid:
            return

        satTab = self.ui.listSats
        loc = self.app.dReg["mount"].location
        eph = self.app.ephemeris
        ts = self.app.dReg["mount"].obsSite.ts
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
                appMag = calcAppMag(sat, loc, eph, satRange, timeNow) if isSunlit else 99
            else:
                isSunlit = False
                appMag = 99
            self.updateListSats(row, satParam, isSunlit=isSunlit, appMag=appMag)

    def updateVisibilityRow(self, row: int, hide: bool) -> None:
        self.ui.listSats.setRowHidden(row, hide)

    def updateTitleRunning(self, title: str, running: bool) -> None:
        changeStyleDynamic(self.ui.satFilterGroup, "run", "true" if running else "false")
        self.ui.satFilterGroup.setTitle(title)

    def calcSat(
        self,
        sat: EarthSatellite,
        row: int,
        loc: GeographicPosition,
        timeNow: Time,
        timeNext: Time,
        altMin: float,
        eph: Any,
    ) -> tuple[bool, int]:
        satParam = findRangeRate(sat, loc, timeNow)
        if not np.isnan(satParam).any():
            isSunlit = findSunlit(sat, eph, timeNow)
            isUp = findSatUp(sat, loc, timeNow, timeNext, altMin)
            twilight = checkTwilight(eph, loc, isUp)
            satRange = satParam[0]
            appMag = calcAppMag(sat, loc, eph, satRange, timeNow) if isSunlit else 99
        else:
            twilight = 5
            isSunlit = False
            isUp = []
            appMag = 99
        self.updateListSats(row, satParam, isUp, isSunlit, appMag, twilight)
        return isSunlit, twilight

    def checkSatOk(self, sat: EarthSatellite, tEnd: Time) -> bool:
        msg = sat.at(tEnd).message
        if msg:
            self.mainW.log.warning(f"{sat.name} caused SGP4: [{msg}]")
            return False
        return True

    def runnerCalcSatList(self) -> None:
        self.signals.setSatGroupTitle.emit("Filter - running", True)
        satTab = self.ui.listSats
        checkIsSunlit = self.ui.satIsSunlit.isChecked()
        selectTwilight = self.ui.satTwilight.currentIndex()
        loc = self.app.dReg["mount"].location
        ts = self.app.dReg["mount"].obsSite.ts
        timeNow = ts.now()
        timeNext = ts.tt_jd(timeNow.tt + 0.25)
        altMin = self.ui.satAltitudeMin.value()
        eph = self.app.ephemeris
        numSats = satTab.rowCount()
        for row in range(numSats):
            if not self.dataValid:
                break
            show = not satTab.isRowHidden(row)
            finished = (row + 1) / numSats * 100
            t = f"Filter - processed: {finished:3.0f}%"
            self.signals.setSatGroupTitle.emit(t, True)
            if satTab.isRowHidden(row):
                continue
            name = satTab.model().index(row, 1).data()
            sat = self.satellites.objects[name]
            if not self.checkSatOk(sat, timeNext):
                continue
            isSunlit, twilight = self.calcSat(sat, row, loc, timeNow, timeNext, altMin, eph)
            if checkIsSunlit:
                show = show and isSunlit
            show = show and (twilight <= selectTwilight)
            self.signals.setSatListRowHidden.emit(row, not show)
        self.signals.setSatGroupTitle.emit("Filter - processed - 100%", False)
        self.mutexCalc.unlock()

    def calcSatList(self) -> None:
        if not self.mutexCalc.tryLock(3000):
            return
        self.workerCalcSatList = Worker(self.runnerCalcSatList)
        self.app.threadPool.start(self.workerCalcSatList)

    def checkSatIsHidden(self, name: str, number: int) -> bool:
        name = name.lower()
        show = self.filterStr in f"{number} {name}"
        if self.checkRemoveSO:
            show = show and "starlink" not in name
            show = show and "oneweb" not in name
            show = show and "globalstar" not in name
            show = show and "navstar" not in name
        if self.checkRemoveK:
            show = show and "kuiper" not in name
        if self.checkRemoveDQ:
            show = show and "quianfan" not in name
            show = show and "digui" not in name
        return not show

    def fillSatListName(self) -> None:
        self.dataValid = False
        self.filterStr = self.ui.satFilterText.text().lower()
        self.checkRemoveSO = self.ui.satRemoveSO.isChecked()
        self.checkRemoveK = self.ui.satRemoveK.isChecked()
        self.checkRemoveDQ = self.ui.satRemoveDQ.isChecked()

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
            self.ui.listSats.setRowHidden(row, self.checkSatIsHidden(name, number))
        self.dataValid = True
        self.calcSatList()
