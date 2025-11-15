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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from astroquery.simbad import Simbad
from PySide6.QtCore import QMutex, QObject
from skyfield.api import Angle

# local import
from mw4.base.tpool import Worker
from mw4.gui.utilities.toolsQtWidget import changeStyleDynamic


class BuildPoints(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.sortRunning = QMutex()
        self.worker: Worker = None
        self.lastGenerator = "none"
        self.sortedGenerators = {
            "grid": self.genBuildGrid,
            "align": self.genBuildAlign,
            "max": self.genBuildMax,
            "med": self.genBuildMed,
            "norm": self.genBuildNorm,
            "min": self.genBuildMin,
            "dso": self.genBuildDSO,
            "file": self.genBuildFile,
            "model": self.genModel,
        }
        self.simbadRa = None
        self.simbadDec = None

        self.ui.genBuildGrid.clicked.connect(self.genBuildGrid)
        self.ui.genBuildAlign3.clicked.connect(self.genBuildAlign)
        self.ui.numberGridPointsCol.valueChanged.connect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.connect(self.genBuildGrid)
        self.ui.genBuildMax.clicked.connect(self.genBuildMax)
        self.ui.genBuildMed.clicked.connect(self.genBuildMed)
        self.ui.genBuildNorm.clicked.connect(self.genBuildNorm)
        self.ui.genBuildMin.clicked.connect(self.genBuildMin)
        self.ui.genBuildFile.clicked.connect(self.genBuildFile)
        self.ui.genBuildDSO.clicked.connect(self.genBuildDSO)
        self.ui.genModel.clicked.connect(self.genModel)
        self.ui.numberDSOPoints.valueChanged.connect(self.genBuildDSO)
        self.ui.saveBuildPoints.clicked.connect(self.saveBuildFile)
        self.ui.saveBuildPointsAs.clicked.connect(self.saveBuildFileAs)
        self.ui.loadBuildPoints.clicked.connect(self.loadBuildFile)
        self.ui.genBuildSpiral.clicked.connect(self.genBuildGoldenSpiral)
        self.ui.clearBuildP.clicked.connect(self.clearBuildP)
        self.ui.sortNothing.clicked.connect(self.rebuildPoints)
        self.ui.sortEW.clicked.connect(self.rebuildPoints)
        self.ui.sortHL.clicked.connect(self.rebuildPoints)
        self.ui.ditherBuildPoints.clicked.connect(self.rebuildPoints)
        self.ui.avoidFlip.clicked.connect(self.rebuildPoints)
        self.ui.autoDeleteMeridian.clicked.connect(self.rebuildPoints)
        self.ui.autoDeleteHorizon.clicked.connect(self.rebuildPoints)
        self.app.buildPointsChanged.connect(self.buildPointsChanged)
        self.ui.generateQuery.editingFinished.connect(self.querySimbad)
        self.ui.isOnline.stateChanged.connect(self.setupDsoGui)

    def initConfig(self):
        """ """
        config = self.app.config["mainW"]

        self.ui.numberGridPointsCol.valueChanged.disconnect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.disconnect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.disconnect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.disconnect(self.genBuildGrid)
        self.ui.numberDSOPoints.valueChanged.disconnect(self.genBuildDSO)

        self.ui.buildPFileName.setText(config.get("buildPFileName", ""))
        self.ui.numberGridPointsRow.setValue(config.get("numberGridPointsRow", 5))
        self.ui.numberGridPointsCol.setValue(config.get("numberGridPointsCol", 6))
        self.ui.altitudeMin.setValue(config.get("altitudeMin", 30))
        self.ui.altitudeMax.setValue(config.get("altitudeMax", 75))
        self.ui.numberDSOPoints.setValue(config.get("numberDSOPoints", 15))
        self.ui.numberSpiral.setValue(config.get("numberSpiral", 30))

        self.ui.autoDeleteMeridian.setChecked(config.get("autoDeleteMeridian", False))
        self.ui.autoDeleteHorizon.setChecked(config.get("autoDeleteHorizon", True))
        self.ui.useSafetyMargin.setChecked(config.get("useSafetyMargin", False))
        self.ui.safetyMarginValue.setValue(config.get("safetyMarginValue", 0))
        self.ui.avoidFlip.setChecked(config.get("avoidFlip", False))
        self.ui.sortNothing.setChecked(config.get("sortNothing", True))
        self.ui.sortEW.setChecked(config.get("sortEW", False))
        self.ui.useDomeAz.setChecked(config.get("useDomeAz", False))
        self.ui.sortHL.setChecked(config.get("sortHL", False))
        self.ui.keepGeneratedPoints.setChecked(config.get("keepGeneratedPoints", False))
        self.ui.ditherBuildPoints.setChecked(config.get("ditherBuildPoints", False))

        self.ui.numberGridPointsCol.valueChanged.connect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.connect(self.genBuildGrid)
        self.ui.numberDSOPoints.valueChanged.connect(self.genBuildDSO)

    def storeConfig(self):
        """ """
        config = self.app.config["mainW"]
        config["buildPFileName"] = self.ui.buildPFileName.text()
        config["numberGridPointsRow"] = self.ui.numberGridPointsRow.value()
        config["numberGridPointsCol"] = self.ui.numberGridPointsCol.value()
        config["altitudeMin"] = self.ui.altitudeMin.value()
        config["altitudeMax"] = self.ui.altitudeMax.value()
        config["numberDSOPoints"] = self.ui.numberDSOPoints.value()
        config["numberSpiral"] = self.ui.numberSpiral.value()
        config["autoDeleteMeridian"] = self.ui.autoDeleteMeridian.isChecked()
        config["autoDeleteHorizon"] = self.ui.autoDeleteHorizon.isChecked()
        config["useSafetyMargin"] = self.ui.useSafetyMargin.isChecked()
        config["safetyMarginValue"] = self.ui.safetyMarginValue.value()
        config["avoidFlip"] = self.ui.avoidFlip.isChecked()
        config["sortNothing"] = self.ui.sortNothing.isChecked()
        config["sortEW"] = self.ui.sortEW.isChecked()
        config["useDomeAz"] = self.ui.useDomeAz.isChecked()
        config["sortHL"] = self.ui.sortHL.isChecked()
        config["keepGeneratedPoints"] = self.ui.keepGeneratedPoints.isChecked()
        config["ditherBuildPoints"] = self.ui.ditherBuildPoints.isChecked()

    def setupIcons(self):
        self.mainW.wIcon(self.ui.loadBuildPoints, "load")
        self.mainW.wIcon(self.ui.saveBuildPoints, "save")
        self.mainW.wIcon(self.ui.saveBuildPointsAs, "save")
        self.mainW.wIcon(self.ui.clearBuildP, "trash")

    def genBuildGrid(self):
        """ """
        self.lastGenerator = "grid"
        self.ui.numberGridPointsRow.setEnabled(False)
        self.ui.numberGridPointsCol.setEnabled(False)
        self.ui.altitudeMin.setEnabled(False)
        self.ui.altitudeMax.setEnabled(False)

        numbRows = int(self.ui.numberGridPointsRow.value())
        numbCols = int(self.ui.numberGridPointsCol.value())
        # we only have equal cols
        col = 2 * int(numbCols / 2)
        self.ui.numberGridPointsCol.setValue(col)
        minAlt = int(self.ui.altitudeMin.value())
        maxAlt = int(self.ui.altitudeMax.value())
        keep = self.ui.keepGeneratedPoints.isChecked()

        suc = self.app.data.genGrid(minAlt, maxAlt, numbRows, numbCols, keep)

        if not suc:
            self.ui.numberGridPointsRow.setEnabled(True)
            self.ui.numberGridPointsCol.setEnabled(True)
            self.ui.altitudeMin.setEnabled(True)
            self.ui.altitudeMax.setEnabled(True)
            self.msg.emit(2, "Model", "Buildpoints", "Could not generate grid")
            return False

        self.processPoints()
        self.ui.numberGridPointsRow.setEnabled(True)
        self.ui.numberGridPointsCol.setEnabled(True)
        self.ui.altitudeMin.setEnabled(True)
        self.ui.altitudeMax.setEnabled(True)
        return True

    def genBuildAlign(self):
        """ """
        self.lastGenerator = "align"
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genAlign(altBase=55, azBase=10, numberBase=3, keep=keep)
        if not suc:
            self.msg.emit(2, "Model", "Buildpoints", "Could not generate 3 align stars")
            return False

        self.processPoints()
        return True

    def genBuildMax(self) -> None:
        """ """
        self.lastGenerator = "max"
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genGreaterCircle(selection="max", keep=keep)
        if not suc:
            self.msg.emit(2, "Model", "Buildpoints", "Build points [max] cannot be generated")
            return

        if self.ui.ditherBuildPoints.isChecked():
            self.app.data.ditherPoints()
        self.processPoints()

    def genBuildMed(self) -> None:
        """ """
        self.lastGenerator = "med"
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genGreaterCircle(selection="med", keep=keep)
        if not suc:
            self.msg.emit(2, "Model", "Buildpoints", "Build points [med] cannot be generated")
            return

        if self.ui.ditherBuildPoints.isChecked():
            self.app.data.ditherPoints()
        self.processPoints()

    def genBuildNorm(self) -> None:
        """ """
        self.lastGenerator = "norm"
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genGreaterCircle(selection="norm", keep=keep)
        if not suc:
            self.msg.emit(2, "Model", "Buildpoints", "Build points [norm] cannot be generated")
            return

        if self.ui.ditherBuildPoints.isChecked():
            self.app.data.ditherPoints()
        self.processPoints()

    def genBuildMin(self) -> None:
        """ """
        self.lastGenerator = "min"
        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.genGreaterCircle(selection="min", keep=keep)
        if not suc:
            self.msg.emit(2, "Model", "Buildpoints", "Build points [min] cannot be generated")
            return

        if self.ui.ditherBuildPoints.isChecked():
            self.app.data.ditherPoints()
        self.processPoints()

    def genBuildDSO(self) -> None:
        """ """
        self.lastGenerator = "dso"
        ha = self.app.mount.obsSite.raJNow
        dec = self.app.mount.obsSite.decJNow
        lst = self.app.mount.obsSite.timeSidereal
        timeJD = self.app.mount.obsSite.timeJD
        location = self.app.mount.obsSite.location

        if ha is None or dec is None or location is None or lst is None:
            self.msg.emit(
                2, "Model", "Buildpoints", "DSO Path cannot be generated - mount off"
            )
            return

        if self.simbadRa and self.simbadDec:
            ha = self.simbadRa
            dec = self.simbadDec

        self.ui.numberDSOPoints.setEnabled(False)
        self.ui.genBuildDSO.setEnabled(False)
        changeStyleDynamic(self.ui.genBuildDSO, "run", True)
        numberTarget = int(self.ui.numberDSOPoints.value())
        keep = self.ui.keepGeneratedPoints.isChecked()
        numberPoints = 0
        numberFilter = 0
        iteration = 20
        while numberFilter < numberTarget:
            numberPoints = numberPoints + numberTarget - numberFilter
            iteration -= 1
            if iteration <= 0:
                break
            self.app.data.generateDSOPath(ha, dec, timeJD, location, numberPoints, keep)
            self.autoDeletePoints()
            numberFilter = len(self.app.data.buildP)

        if self.ui.ditherBuildPoints.isChecked():
            self.app.data.ditherPoints()
        self.processPoints()
        self.ui.genBuildDSO.setEnabled(True)
        self.ui.numberDSOPoints.setEnabled(True)
        changeStyleDynamic(self.ui.genBuildDSO, "run", False)

    def genBuildGoldenSpiral(self) -> None:
        """ """
        self.lastGenerator = "spiral"
        numberTarget = int(self.ui.numberSpiral.value())
        changeStyleDynamic(self.ui.genBuildSpiral, "run", True)
        numberPoints = 0
        numberFilter = 0
        iteration = 20
        while numberFilter < numberTarget:
            numberPoints = numberPoints + numberTarget - numberFilter
            iteration -= 1
            if iteration <= 0:
                break
            self.app.data.generateGoldenSpiral(numberPoints=numberPoints)
            self.autoDeletePoints()
            numberFilter = len(self.app.data.buildP)
        self.processPoints()
        changeStyleDynamic(self.ui.genBuildSpiral, "run", False)

    def genModel(self) -> None:
        """ """
        self.lastGenerator = "model"

        keep = self.ui.keepGeneratedPoints.isChecked()
        if not keep:
            self.app.data.clearBuildP()

        model = self.app.mount.model
        for star in model.starList:
            self.app.data.addBuildP((star.alt.degrees, star.az.degrees, True))
        self.processPoints()

    def genBuildFile(self) -> None:
        """
        """
        self.lastGenerator = "file"
        fileName = self.ui.buildPFileName.text()
        if not fileName:
            self.msg.emit(2, "Model", "Buildpoints", "Build points file name not given")
            return

        keep = self.ui.keepGeneratedPoints.isChecked()
        fullFileName = self.app.mwGlob["configDir"] / fileName
        suc = self.app.data.loadBuildP(fullFileName, keep=keep)

        if not suc:
            text = f"Build points file [{fileName}] could not be loaded"
            self.msg.emit(2, "Model", "Buildpoints", text)
            return
        self.processPoints()

    def loadBuildFile(self) -> None:
        """ """
        folder = self.app.mwGlob["configDir"]
        fileTypes = "Build Point Files (*.bpts)"
        fileTypes += ";; CSV Files (*.csv)"
        fileTypes += ";; Model Files (*.model)"
        fullFileName = self.mainW.openFile(
            self.mainW, "Open build point file", folder, fileTypes
        )
        if not fullFileName.is_file():
            return

        keep = self.ui.keepGeneratedPoints.isChecked()
        suc = self.app.data.loadBuildP(fullFileName, ext=fullFileName.suffix, keep=keep)
        if suc:
            self.ui.buildPFileName.setText(fullFileName.name)
            self.msg.emit(
                0, "Model", "Buildpoints", f"Build file [{fullFileName.name}] loaded"
            )
        else:
            self.msg.emit(
                2,
                "Model",
                "Buildpoints",
                f"Build file [{fullFileName.name}] cannot be loaded",
            )
        self.genBuildFile()

    def saveBuildFile(self) -> None:
        """ """
        fileName = self.ui.buildPFileName.text()
        if not fileName:
            self.msg.emit(0, "Model", "Buildpoints", "Build points file name not given")
            return

        self.app.data.saveBuildP(fileName)
        self.msg.emit(0, "Model", "Buildpoints", f"Build file [{fileName}] saved")

    def saveBuildFileAs(self) -> None:
        """ """
        folder = self.app.mwGlob["configDir"]
        saveFilePath = self.mainW.saveFile(
            self.mainW, "Save build point file", folder, "Build point files (*.bpts)"
        )
        if saveFilePath.is_dir():
            return

        self.app.data.saveBuildP(saveFilePath.stem)
        self.ui.buildPFileName.setText(saveFilePath.stem)
        self.msg.emit(0, "Model", "Buildpoints", f"Build file [{saveFilePath.stem}] saved")

    def clearBuildP(self) -> None:
        """ """
        self.app.data.clearBuildP()
        self.app.drawBuildPoints.emit()
        self.app.redrawHemisphere.emit()

    def autoDeletePoints(self) -> None:
        """ """
        if self.ui.autoDeleteHorizon.isChecked():
            self.app.data.deleteBelowHorizon()
        if self.ui.autoDeleteMeridian.isChecked():
            self.app.data.deleteCloseMeridian()
        if self.ui.useSafetyMargin.isChecked():
            value = int(self.ui.safetyMarginValue.value())
            self.app.data.deleteCloseHorizonLine(value)

    def doSortDomeAzData(self, result: tuple) -> None:
        """ """
        points, pierside = result
        self.app.data.sort(points, sortDomeAz=True, pierside=pierside)
        self.sortRunning.unlock()
        self.app.redrawHemisphere.emit()
        self.app.drawBuildPoints.emit()

    def sortDomeAzWorker(self, points: list, pierside: str) -> tuple[list[tuple[int, int]], str]:
        """ """
        pointsNew = []
        numbAll = len(points)
        ui = self.ui.autoSortGroup
        changeStyleDynamic(ui, "run", True)
        for i, point in enumerate(points):
            t = f"Auto sort points: progress {(i + 1) / numbAll * 100:3.0f}%"
            ui.setTitle(t)
            alt = point[0]
            az = point[1]
            _, domeAz = self.app.mount.calcMountAltAzToDomeAltAz(alt, az)
            if domeAz is None:
                continue
            pointsNew.append((alt, az, True, domeAz.degrees))
        points = pointsNew
        ui.setTitle("Auto sort points")
        changeStyleDynamic(ui, "run", False)
        return points, pierside

    def sortDomeAz(self, points: list, pierside: str) -> None:
        """ """
        if not self.sortRunning.tryLock():
            return
        self.worker = Worker(self.sortDomeAzWorker, points, pierside)
        self.worker.signals.result.connect(self.doSortDomeAzData)
        self.app.threadPool.start(self.worker)

    def sortMountAz(self, points: list, eastwest: bool, highlow: bool, pierside: str) -> None:
        """ """
        points = [(x[0], x[1], x[2], 0) for x in points]
        self.app.data.sort(points, eastwest, highlow, pierside)
        self.app.redrawHemisphere.emit()
        self.app.drawBuildPoints.emit()

    def autoSortPoints(self) -> None:
        """ """
        eastwest = self.ui.sortEW.isChecked()
        highlow = self.ui.sortHL.isChecked()
        avoidFlip = self.ui.avoidFlip.isChecked()
        useDomeAz = self.ui.useDomeAz.isChecked()
        enableDomeAz = self.ui.useDomeAz.isEnabled()
        noSort = self.ui.sortNothing.isChecked()
        pierside = self.app.mount.obsSite.pierside

        if not avoidFlip:
            pierside = None

        points = self.app.data.buildP
        if noSort and not avoidFlip:
            self.app.redrawHemisphere.emit()
            self.app.drawBuildPoints.emit()
            return

        if useDomeAz and enableDomeAz and eastwest:
            self.sortDomeAz(points, pierside)
        else:
            self.sortMountAz(points, eastwest, highlow, pierside)

    def buildPointsChanged(self) -> None:
        """ """
        self.lastGenerator = "none"

    def rebuildPoints(self) -> None:
        """ """
        if self.lastGenerator in self.sortedGenerators:
            self.sortedGenerators[self.lastGenerator]()
        self.processPoints()

    def processPoints(self) -> None:
        """ """
        self.autoDeletePoints()
        self.autoSortPoints()

    def setupDsoGui(self) -> None:
        """ """
        isOnline = self.ui.isOnline.isChecked()
        self.ui.generateQuery.setEnabled(isOnline)
        self.ui.generateRa.setEnabled(isOnline)
        self.ui.generateDec.setEnabled(isOnline)
        self.ui.generateQueryText.setEnabled(isOnline)
        self.ui.generateRaText.setEnabled(isOnline)
        self.ui.generateDecText.setEnabled(isOnline)

    def querySimbad(self) -> None:
        """ """
        if not self.ui.isOnline.isChecked():
            self.msg.emit(2, "Model", "Buildpoints", "MW4 is offline")
            return

        ident = self.ui.generateQuery.text().strip()
        if not ident:
            self.msg.emit(2, "Model", "Buildpoints", "No query data given")
            self.ui.generateRa.setText("")
            self.ui.generateDec.setText("")
            self.simbadRa = None
            self.simbadDec = None
            return

        result = Simbad.query_object(ident)

        if not result:
            self.msg.emit(2, "Model", "Buildpoints", f"Nox response from SIMBAD for {ident}")
            self.ui.generateRa.setText("")
            self.ui.generateDec.setText("")
            self.simbadRa = None
            self.simbadDec = None
            return

        self.simbadRa = Angle(degrees=float(result["ra"]))
        self.ui.generateRa.setText(f"{self.simbadRa.degrees:.6f}")

        self.simbadDec = Angle(degrees=float(result["dec"]))
        self.ui.generateDec.setText(f"{self.simbadDec.degrees:.6f}")
