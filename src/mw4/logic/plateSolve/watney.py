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
# Licence APL2.0
#
###########################################################
import logging
import platform
from pathlib import Path


class Watney:
    """ """

    log = logging.getLogger("MW4")
    returnCodes: dict = {0: "No errors", 1: "No solution"}

    def __init__(self, parent):
        self.parent = parent
        self.data = parent.data
        self.tempDir = parent.app.mwGlob["tempDir"]
        self.workDir = parent.app.mwGlob["workDir"]

        self.result: dict = {"success": False}
        self.process = None
        self.deviceName: str = "Watney"
        self.indexPath = Path("")
        self.appPath = Path("")
        self.timeout: int = 30
        self.searchRadius: int = 20
        self.setDefaultPath()
        self.defaultConfig: dict = {
            "watney": {
                "deviceName": "Watney",
                "deviceList": ["Watney"],
                "searchRadius": 10,
                "timeout": 30,
                "appPath": str(self.appPath),
                "indexPath": str(self.indexPath),
            }
        }

    def saveConfigFile(self) -> None:
        """ """
        cfgFile = self.tempDir / "watney-solve-config.yml"
        with open(cfgFile, "w+") as outFile:
            outFile.write(f"quadDbPath: '{self.indexPath}'\n")
            outFile.write("defaultStarDetectionBgOffset: 1.0\n")
            outFile.write("defaultLowerDensityOffset: 3\n")

    def setDefaultPath(self) -> None:
        """ """
        self.appPath = self.workDir / "watney-cli"
        self.indexPath = self.workDir / "watney-index"
        self.saveConfigFile()

    def solve(self, imagePath: Path, updateHeader: bool) -> dict:
        """ """
        isBlind = self.searchRadius == 180
        jsonPath = self.tempDir / "solve.json"
        wcsPath = self.tempDir / "temp.wcs"
        wcsPath.unlink(missing_ok=True)

        runnable = [self.appPath / "watney-solve"]
        if isBlind:
            runnable += ["blind"]
            runnable += ["--min-radius", "0.15", "--max-radius", "16"]
        else:
            runnable += ["nearby", "-h"]
            runnable += ["-s", f"{self.searchRadius:1.1f}"]

        options = [
            "-i",
            imagePath,
            "-o",
            jsonPath,
            "-w",
            wcsPath,
            "--use-config",
            self.tempDir / "watney-solve-config.yml",
            "--extended",
            "True",
        ]
        runnable.extend(options)
        suc, msg = self.parent.runSolverBin(runnable)
        return self.parent.prepareResult(suc, msg, imagePath, wcsPath, updateHeader)

    def checkAvailabilityProgram(self, appPath: Path) -> bool:
        """ """
        self.appPath = appPath

        if platform.system() == "Darwin" or platform.system() == "Linux":
            program = self.appPath / "watney-solve"
        elif platform.system() == "Windows":
            program = self.appPath / "watney-solve.exe"
        else:
            return False
        return program.is_file()

    def checkAvailabilityIndex(self, indexPath: Path) -> bool:
        """ """
        self.indexPath = indexPath
        self.saveConfigFile()

        return len(list(self.indexPath.glob("*.*"))) > 0
