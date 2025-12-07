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

from astroquery.simbad import Simbad
from PySide6.QtCore import QMutex, QObject
from skyfield.api import Angle
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
        self.lastGenerator: str = "none"
        self.sortedGenerators: dict = {
            "grid": self.genBuildGrid,
            "align": self.genBuildAlign,
            "celestial": self.genBuildCelestial,
            "dso": self.genBuildDSO,
            "file": self.genBuildFile,
            "model": self.genModel,
        }
        self.simbadRa: Angle = Angle(hours=0)
        self.simbadDec: Angle = Angle(degrees=0)

        self.ui.genBuildGrid.clicked.connect(self.genBuildGrid)
        self.ui.genBuildAlign3.clicked.connect(self.genBuildAlign)
        self.ui.numberGridPointsCol.valueChanged.connect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.connect(self.genBuildGrid)
        self.ui.genBuildCelestial.clicked.connect(self.genBuildCelestial)
        self.ui.numberCelestialStepHA.valueChanged.connect(self.genBuildCelestial)
        self.ui.numberCelestialStepDEC.valueChanged.connect(self.genBuildCelestial)
        self.ui.meridianDistanceFlip.valueChanged.connect(self.genBuildCelestial)
        self.ui.genBuildFile.clicked.connect(self.genBuildFile)
        self.ui.genBuildDSO.clicked.connect(self.genBuildDSO)
        self.ui.genModel.clicked.connect(self.genModel)
        self.ui.numberDSOPoints.valueChanged.connect(self.genBuildDSO)
        self.ui.saveBuildPoints.clicked.connect(self.saveBuildFile)
        self.ui.saveBuildPointsAs.clicked.connect(self.saveBuildFileAs)
        self.ui.loadBuildPoints.clicked.connect(self.loadBuildFile)
        self.ui.genBuildSpiral.clicked.connect(self.genBuildGoldenSpiral)
        self.ui.clearBuildP.clicked.connect(self.clearBuildP)
        self.ui.noSort.clicked.connect(self.rebuildPoints)
        self.ui.sortAZ.clicked.connect(self.rebuildPoints)
        self.ui.sortDomeAZ.clicked.connect(self.rebuildPoints)
        self.ui.sortALT.clicked.connect(self.rebuildPoints)
        self.ui.ditherBuildPoints.clicked.connect(self.rebuildPoints)
        self.ui.avoidFlip.clicked.connect(self.rebuildPoints)
        self.ui.autoDeleteMeridian.clicked.connect(self.rebuildPoints)
        self.ui.autoDeleteHorizon.clicked.connect(self.rebuildPoints)
        self.ui.useSafetyMargin.clicked.connect(self.rebuildPoints)
        self.app.buildPointsChanged.connect(self.buildPointsChanged)
        self.ui.generateQuery.editingFinished.connect(self.querySimbad)
        self.ui.isOnline.stateChanged.connect(self.setupDsoGui)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]

        self.ui.numberGridPointsCol.valueChanged.disconnect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.disconnect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.disconnect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.disconnect(self.genBuildGrid)
        self.ui.numberCelestialStepHA.valueChanged.disconnect(self.genBuildCelestial)
        self.ui.numberCelestialStepDEC.valueChanged.disconnect(self.genBuildCelestial)
        self.ui.meridianDistanceFlip.valueChanged.disconnect(self.genBuildCelestial)

        self.ui.numberDSOPoints.valueChanged.disconnect(self.genBuildDSO)
        self.ui.buildPFileName.setText(config.get("buildPFileName", ""))
        self.ui.numberGridPointsRow.setValue(config.get("numberGridPointsRow", 5))
        self.ui.numberGridPointsCol.setValue(config.get("numberGridPointsCol", 6))
        self.ui.altitudeMin.setValue(config.get("altitudeMin", 30))
        self.ui.altitudeMax.setValue(config.get("altitudeMax", 75))
        self.ui.numberDSOPoints.setValue(config.get("numberDSOPoints", 15))
        self.ui.numberSpiral.setValue(config.get("numberSpiral", 30))
        self.ui.numberCelestialStepHA.setValue(config.get("numberCelestialStepHA", 15))
        self.ui.numberCelestialStepDEC.setValue(config.get("numberCelestialStepDEC", 15))
        self.ui.meridianDistanceFlip.setValue(config.get("meridianDistanceFlip", 5))
        self.ui.autoDeleteMeridian.setChecked(config.get("autoDeleteMeridian", False))
        self.ui.autoDeleteHorizon.setChecked(config.get("autoDeleteHorizon", True))
        self.ui.useSafetyMargin.setChecked(config.get("useSafetyMargin", False))
        self.ui.safetyMarginValue.setValue(config.get("safetyMarginValue", 0))
        self.ui.avoidFlip.setChecked(config.get("avoidFlip", False))
        self.ui.noSort.setChecked(config.get("noSort", True))
        self.ui.sortAZ.setChecked(config.get("sortAZ", False))
        self.ui.sortDomeAZ.setChecked(config.get("sortDomeAZ", False))
        self.ui.sortALT.setChecked(config.get("sortALT", False))
        self.ui.keepGeneratedPoints.setChecked(config.get("keepGeneratedPoints", False))
        self.ui.ditherBuildPoints.setChecked(config.get("ditherBuildPoints", False))

        self.ui.numberGridPointsCol.valueChanged.connect(self.genBuildGrid)
        self.ui.numberGridPointsRow.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMin.valueChanged.connect(self.genBuildGrid)
        self.ui.altitudeMax.valueChanged.connect(self.genBuildGrid)
        self.ui.numberDSOPoints.valueChanged.connect(self.genBuildDSO)
        self.ui.numberCelestialStepHA.valueChanged.connect(self.genBuildCelestial)
        self.ui.numberCelestialStepDEC.valueChanged.connect(self.genBuildCelestial)
        self.ui.meridianDistanceFlip.valueChanged.connect(self.genBuildCelestial)

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["buildPFileName"] = self.ui.buildPFileName.text()
        config["numberGridPointsRow"] = self.ui.numberGridPointsRow.value()
        config["numberGridPointsCol"] = self.ui.numberGridPointsCol.value()
        config["altitudeMin"] = self.ui.altitudeMin.value()
        config["altitudeMax"] = self.ui.altitudeMax.value()
        config["numberDSOPoints"] = self.ui.numberDSOPoints.value()
        config["numberSpiral"] = self.ui.numberSpiral.value()
        config["numberCelestialStepHA"] = self.ui.numberCelestialStepHA.value()
        config["numberCelestialStepDEC"] = self.ui.numberCelestialStepDEC.value()
        config["meridianDistanceFlip"] = self.ui.meridianDistanceFlip.value()
        config["autoDeleteMeridian"] = self.ui.autoDeleteMeridian.isChecked()
        config["autoDeleteHorizon"] = self.ui.autoDeleteHorizon.isChecked()
        config["useSafetyMargin"] = self.ui.useSafetyMargin.isChecked()
        config["safetyMarginValue"] = self.ui.safetyMarginValue.value()
        config["avoidFlip"] = self.ui.avoidFlip.isChecked()
        config["noSort"] = self.ui.noSort.isChecked()
        config["sortAZ"] = self.ui.sortAZ.isChecked()
        config["sortDomeAZ"] = self.ui.sortDomeAZ.isChecked()
        config["sortALT"] = self.ui.sortALT.isChecked()
        config["keepGeneratedPoints"] = self.ui.keepGeneratedPoints.isChecked()
        config["ditherBuildPoints"] = self.ui.ditherBuildPoints.isChecked()

    def setupIcons(self) -> None:
        """ """
        self.mainW.wIcon(self.ui.loadBuildPoints, "load")
        self.mainW.wIcon(self.ui.saveBuildPoints, "save")
        self.mainW.wIcon(self.ui.saveBuildPointsAs, "save")
        self.mainW.wIcon(self.ui.clearBuildP, "trash")

    def genBuildGrid(self) -> None:
        """ """
        self.lastGenerator = "grid"
        numbRows = int(self.ui.numberGridPointsRow.value())
        numbCols = int(self.ui.numberGridPointsCol.value())
        # we only have equal cols
        col = 2 * int(numbCols / 2)
        self.ui.numberGridPointsCol.setValue(col)
        minAlt = int(self.ui.altitudeMin.value())
        maxAlt = int(self.ui.altitudeMax.value())

        if not self.app.data.genGrid(minAlt, maxAlt, numbRows, numbCols):
            self.msg.emit(2, "Model", "Buildpoints", "Could not generate grid")
            return
        self.processPoints()

    def genBuildAlign(self) -> None:
        """ """
        self.lastGenerator = "align"
        suc = self.app.data.genAlign(altBase=55, azBase=10, numberBase=3)
        if not suc:
            self.msg.emit(2, "Model", "Buildpoints", "Could not generate 3 align stars")
            return
        self.processPoints()

    def genBuildCelestial(self) -> None:
        """ """
        self.lastGenerator = "celestial"
        stepHA = int(self.ui.numberCelestialStepHA.value())
        stepDec = int(self.ui.numberCelestialStepDEC.value())
        distFlip = int(self.ui.meridianDistanceFlip.value())
        suc = self.app.data.genGreaterCircle(stepHA, stepDec, distFlip)
        if not suc:
            self.msg.emit(
                2, "Model", "Buildpoints", "Build points celestial cannot be generated"
            )
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

        if any(x is None for x in [ha, dec, location, lst]):
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
        numberFiltered = 0
        iteration = 20
        while numberFiltered < numberTarget:
            numberPoints = numberPoints + numberTarget - numberFiltered
            iteration -= 1
            if iteration <= 0:
                break
            self.app.data.generateDSOPath(ha, dec, timeJD, location, numberPoints, keep)
            self.autoDeletePoints()
            numberFiltered = len(self.app.data.buildP)
            if numberFiltered == 0:
                break

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
        self.app.data.clearBuildP()
        model = self.app.mount.model
        for star in model.starList:
            self.app.data.addBuildP(
                [int(star.alt.degrees), int(star.az.degrees), self.app.data.UNPROCESSED]
            )
        self.processPoints()

    def genBuildFile(self) -> None:
        """ """
        self.lastGenerator = "file"
        fileName = self.ui.buildPFileName.text()
        if not fileName:
            self.msg.emit(2, "Model", "Buildpoints", "Build points file name not given")
            return

        fullFileName = self.app.mwGlob["configDir"] / fileName
        if not self.app.data.loadBuildP(fullFileName):
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

        suc = self.app.data.loadBuildP(fullFileName, ext=fullFileName.suffix)
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
        if saveFilePath.is_dir() or not saveFilePath.stem:
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

    def autoSortPoints(self) -> None:
        """ """
        if self.ui.sortALT.isChecked():
            self.app.data.sortAlt()
        if self.ui.sortAZ.isChecked():
            self.app.data.sortAz()
        if self.ui.sortDomeAZ.isChecked() and bool(self.app.deviceStat.get("dome")):
            self.app.data.sortDomeAz()
        if self.ui.avoidFlip.isChecked():
            self.app.data.sortActualPierside()

    def buildPointsChanged(self) -> None:
        """ """
        self.lastGenerator = "none"

    def processPoints(self) -> None:
        """ """
        self.autoDeletePoints()
        self.autoSortPoints()
        self.app.redrawHemisphere.emit()
        self.app.drawBuildPoints.emit()

    def rebuildPoints(self) -> None:
        """ """
        if self.lastGenerator in self.sortedGenerators:
            self.sortedGenerators[self.lastGenerator]()
        self.processPoints()

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

        self.ui.generateRa.setText("")
        self.ui.generateDec.setText("")
        self.simbadRa = Angle(hours=0)
        self.simbadDec = Angle(degrees=0)

        ident = self.ui.generateQuery.text().strip()
        if not ident:
            self.msg.emit(2, "Model", "Buildpoints", "No query data given")
            return

        result = Simbad.query_object(ident)
        if not result:
            self.msg.emit(2, "Model", "Buildpoints", f"Nox response from SIMBAD for {ident}")
            return

        self.simbadRa = Angle(degrees=float(result["ra"]))
        self.ui.generateRa.setText(f"{self.simbadRa.degrees:.6f}")
        self.simbadDec = Angle(degrees=float(result["dec"]))
        self.ui.generateDec.setText(f"{self.simbadDec.degrees:.6f}")
