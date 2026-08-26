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
import numpy as np
from mw4.base.tpool import Worker
from mw4.gui.mainWaddon.astroObjects import AstroObjects
from mw4.gui.mainWaddon.satData import SatData
from mw4.gui.utilities.nativeQt.qtCustomTableWidgetItem import QCustomTableWidgetItem
from mw4.gui.utilities.qtHelpers import changeStyleDynamic
from mw4.logic.databaseProcessing.sourceURL import satSourceURLs
from mw4.logic.satellites.satellite_calculations import (
    calcAppMag,
    checkTwilight,
    findRangeRate,
    findSatUp,
    findSunlit,
)
from PySide6.QtCore import QMutex, QObject, Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QTableWidgetItem
from skyfield.api import EarthSatellite, Time
from skyfield.toposlib import GeographicPosition
from typing import Any, ClassVar


class SatSearchSignals(QObject):
    setSatListItem = Signal(int, int, object, int)
    setSatListRowHidden = Signal(int, bool, int)
    setSatGroupTitle = Signal(str, bool, int)


class SatSearch(SatData):
    SATFILTERS: ClassVar = ["Starlink", "Cosmos", "Iridium", "Kuiper", "Qianfan", "Hulianwang"]

    def __init__(self, mainW: Any) -> None:
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.signals = SatSearchSignals()
        self.calcGeneration: int = 0
        self.filterStr: str = ""
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
        for satFilter in self.SATFILTERS:
            ui = getattr(self.ui, f"satRemove{satFilter}")
            ui.clicked.connect(self.fillSatListName)
        self.ui.satIsSunlit.clicked.connect(self.fillSatListName)
        self.ui.satTwilight.activated.connect(self.fillSatListName)
        self.signals.setSatListItem.connect(self.setListSatsEntry)
        self.signals.setSatGroupTitle.connect(self.updateTitleRunning)
        self.signals.setSatListRowHidden.connect(self.updateVisibilityRow)
        self.ui.progSatFull.clicked.connect(self.satellites.progFull)
        self.ui.progSatFiltered.clicked.connect(self.satellites.progFiltered)
        self.ui.progSatSelected.clicked.connect(self.satellites.progSelected)

    def initConfig(self) -> None:
        config = self.app.config["WindowMain"]
        self.ui.satFilterText.setText(config.get("satFilterText"))
        self.ui.satTwilight.setCurrentIndex(config.get("satTwilight", 5))
        self.ui.satIsSunlit.setChecked(config.get("satIsSunlit", False))
        self.ui.satAltitudeMin.setValue(config.get("satAltitudeMin", 30))
        self.ui.satSourceList.setCurrentIndex(config.get("satSource", 0))
        for satFilter in self.SATFILTERS:
            ui = getattr(self.ui, f"satRemove{satFilter}")
            ui.setChecked(config.get(f"satRemove{satFilter}", False))

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        config["satFilterText"] = self.ui.satFilterText.text()
        config["satTwilight"] = self.ui.satTwilight.currentIndex()
        config["satIsSunlit"] = self.ui.satIsSunlit.isChecked()
        config["satAltitudeMin"] = self.ui.satAltitudeMin.value()
        config["satSource"] = self.ui.satSourceList.currentIndex()
        for satFilter in self.SATFILTERS:
            ui = getattr(self.ui, f"satRemove{satFilter}")
            config[f"satRemove{satFilter}"] = ui.isChecked()

    def prepareSatTable(self) -> None:
        self.ui.listSats.setColumnCount(9)
        hLabels = [
            "Num",
            "Satellite Name",
            "Time\n[H:M]",
            "Sat\n[mag]",
            "Dist\n[km]",
            "Rad v\n[km/s]",
            "Lat v\n[deg/s]",
            "Lon v\n[deg/s]",
        ]
        hSet = [55, 180, 85, 40, 50, 50, 50, 50, 0]
        self.ui.listSats.setColumnCount(len(hSet))
        self.ui.listSats.setHorizontalHeaderLabels(hLabels)
        for i, hs in enumerate(hSet):
            self.ui.listSats.setColumnWidth(i, hs)
        self.ui.listSats.verticalHeader().setDefaultSectionSize(16)
        self.ui.listSats.horizontalHeader().setSortIndicatorShown(False)
        self.ui.listSats.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.listSats.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def processLoadTLE(self) -> None:
        loader = self.app.dReg["mount"].obsSite.loader
        satellites = loader.tle_file(str(self.satellites.dest))
        for sat in satellites:
            self.satellites.objects[sat.name] = sat

    def processLoadJsonOMM(self) -> None:
        ts = self.app.dReg["mount"].obsSite.ts
        with open(str(self.satellites.dest)) as f:
            try:
                omm_records = json.load(f)
            except json.JSONDecodeError as e:
                self.mainW.log.error(f"Failed to load OMM file: {e}")
                self.msg.emit(2, "Satellite", "Error", f"Loading: {self.satellites.dest}")
                return
        for record in omm_records:
            sat = EarthSatellite.from_omm(ts, record)
            self.satellites.objects[sat.name] = sat

    def processSatelliteSource(self) -> None:
        self.ui.listSats.setRowCount(0)
        self.satellites.objects.clear()
        if self.satellites.dest.suffix == ".json":
            self.processLoadJsonOMM()
        elif self.satellites.dest.suffix == ".tle":
            self.processLoadTLE()
        else:
            self.msg.emit(2, "Satellite", "Error", "Unsupported file format")
            return

    def setListSatsEntry(self, row: int, col: int, entry: str, generation: int) -> None:
        if generation != self.calcGeneration:
            return
        self.ui.listSats.setItem(row, col, entry)

    def updateListSats(
        self,
        row: int,
        satParam: tuple[float, float, float, float],
        isUp: list,
        isSunlit: bool,
        appMag: float = 99,
        twilight: int = 4,
        generation: int = 0,
    ) -> None:
        if isUp:
            t = self.app.timeMgr.convertTime(isUp[0], "%d.%m  %H:%M") if len(isUp) else ""
            entry = QTableWidgetItem(t)
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.signals.setSatListItem.emit(row, 2, entry, generation)
        if isSunlit:
            value = f"{appMag:1.1f}" if isSunlit else ""
            entry = QCustomTableWidgetItem(value)
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.signals.setSatListItem.emit(row, 3, entry, generation)

        entry = QTableWidgetItem(f"{satParam[0]:5.0f}")
        entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.signals.setSatListItem.emit(row, 4, entry, generation)

        entry = QTableWidgetItem(f"{satParam[1]:+2.2f}")
        entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.signals.setSatListItem.emit(row, 5, entry, generation)

        entry = QTableWidgetItem(f"{satParam[2]:+2.2f}")
        entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.signals.setSatListItem.emit(row, 6, entry, generation)

        entry = QTableWidgetItem(f"{satParam[3]:+2.2f}")
        entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.signals.setSatListItem.emit(row, 7, entry, generation)

        if twilight is not None:
            entry = QTableWidgetItem(f"{twilight:1.0f}")
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.signals.setSatListItem.emit(row, 8, entry, generation)

    def updateVisibilityRow(self, row: int, hide: bool, generation: int) -> None:
        if generation != self.calcGeneration:
            return
        self.ui.listSats.setRowHidden(row, hide)

    def updateTitleRunning(self, title: str, running: bool, generation: int) -> None:
        if generation != self.calcGeneration:
            return
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
        generation: int,
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
        self.updateListSats(row, satParam, isUp, isSunlit, appMag, twilight, generation)
        return isSunlit, twilight

    def satOkSGP4(self, sat: EarthSatellite, tEnd: Time) -> bool:
        msg = sat.at(tEnd).message
        if msg:
            self.mainW.log.warning(f"{sat.name} caused SGP4: [{msg}]")
            return False
        return True

    def runnerCalcSatList(
        self,
        snapshot: list[tuple[int, str, EarthSatellite, bool]],
        generation: int,
        checkIsSunlit: bool,
        selectTwilight: int,
        altMin: float,
    ) -> None:
        try:
            self.signals.setSatGroupTitle.emit("Filter - running", True, generation)
            loc = self.app.dReg["mount"].location
            ts = self.app.dReg["mount"].obsSite.ts
            timeNow = ts.now()
            timeNext = ts.tt_jd(timeNow.tt + 0.25)
            eph = self.app.ephemeris
            numSats = len(snapshot)
            for i, (row, _name, sat, hidden) in enumerate(snapshot):
                if generation != self.calcGeneration:
                    break
                finished = (i + 1) / numSats * 100
                t = f"Filter - processed: {finished:3.0f}%"
                self.signals.setSatGroupTitle.emit(t, True, generation)
                if hidden:
                    continue
                if not self.satOkSGP4(sat, timeNext):
                    continue
                isSunlit, twilight = self.calcSat(
                    sat, row, loc, timeNow, timeNext, altMin, eph, generation
                )
                show = True
                if checkIsSunlit:
                    show = show and isSunlit
                show = show and (twilight <= selectTwilight)
                self.signals.setSatListRowHidden.emit(row, not show, generation)
            self.signals.setSatGroupTitle.emit("Filter - processed - 100%", False, generation)
        finally:
            self.mutexCalc.unlock()

    def calcSatList(
        self, snapshot: list[tuple[int, str, EarthSatellite, bool]], generation: int
    ) -> None:
        if not snapshot:
            self.signals.setSatGroupTitle.emit("Filter - processed - 100%", False, generation)
            return
        checkIsSunlit = self.ui.satIsSunlit.isChecked()
        selectTwilight = self.ui.satTwilight.currentIndex()
        altMin = self.ui.satAltitudeMin.value()
        if not self.mutexCalc.tryLock(3000):
            return
        self.workerCalcSatList = Worker(
            self.runnerCalcSatList, snapshot, generation, checkIsSunlit, selectTwilight, altMin
        )
        self.app.threadPool.start(self.workerCalcSatList)

    def checkSatNameOk(self, name: str, number: int) -> bool:
        name = name.lower()
        show = self.filterStr in f"{number} {name}"
        for satFilter in self.SATFILTERS:
            if getattr(self.ui, f"satRemove{satFilter}").isChecked():
                show = show and satFilter.lower() not in name
        return show

    def fillSatListName(self) -> None:
        self.filterReady = False
        self.calcGeneration += 1
        generation = self.calcGeneration
        self.ui.listSats.setRowCount(0)
        self.filterStr = self.ui.satFilterText.text().lower()
        snapshot: list[tuple[int, str, EarthSatellite, bool]] = []
        for name in self.satellites.objects:
            sat = self.satellites.objects[name]
            number = sat.model.satnum
            row = self.ui.listSats.rowCount()
            self.ui.listSats.insertRow(row)
            entry = QTableWidgetItem(f"{number:5d}")
            entry.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ui.listSats.setItem(row, 0, entry)
            entry = QTableWidgetItem(name)
            entry.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.ui.listSats.setItem(row, 1, entry)
            show = self.checkSatNameOk(name, number)
            self.ui.listSats.setRowHidden(row, not show)
            snapshot.append((row, name, sat, not show))
        self.calcSatList(snapshot, generation)
