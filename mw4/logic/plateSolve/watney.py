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
import logging
import subprocess
import os
import time
import platform
from pathlib import Path

# external packages

# local imports
from logic.fits.fitsFunction import (
    getSolutionFromWCSHeader,
    getImageHeader,
    updateImageFileHeaderWithSolution,
)


class Watney(object):
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
        cfgFile = os.path.join(self.tempDir, "watney-solve-config.yml")
        with open(cfgFile, "w+") as outFile:
            outFile.write(f"quadDbPath: '{self.indexPath}'\n")
            outFile.write("defaultStarDetectionBgOffset: 1.0\n")
            outFile.write("defaultLowerDensityOffset: 3\n")

    def setDefaultPath(self) -> None:
        """ """
        self.appPath = self.workDir / "watney-cli"
        self.indexPath = self.workDir / "watney-index"
        self.saveConfigFile()

    def runWatney(self, runnable: list) -> [bool, str]:
        """ """
        timeStart = time.time()
        try:
            self.process = subprocess.Popen(
                args=runnable, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, _ = self.process.communicate(timeout=self.timeout)

        except subprocess.TimeoutExpired:
            self.log.error("Timeout happened")
            return False, "Solving timed out"

        except Exception as e:
            self.log.critical(f"error: {e} happened")
            return False, "Exception during solving"

        delta = time.time() - timeStart
        stdoutText = stdout.decode().replace("\n", " ")
        self.log.debug(f"Run {delta}s, {stdoutText}")
        rCode = int(self.process.returncode)
        suc = rCode == 0
        msg = self.returnCodes.get(rCode, "Unknown code")
        return suc, msg

    def solve(self, imagePath: Path, updateHeader: bool) -> dict:
        """ """
        self.process = None
        result = {"success": False, "message": "Internal error"}

        isBlind = self.searchRadius == 180
        jsonPath = self.tempDir / "solve.json"
        wcsPath = self.tempDir / "temp.wcs"

        if wcsPath.is_file():
            os.remove(wcsPath)

        runnable = [self.appPath / "watney-solve"]

        if isBlind:
            runnable += ["blind"]
            runnable += ["--min-radius", "0.15", "--max-radius", "16"]
        else:
            runnable += ["nearby", "-h"]
            runnable += ["-s", f"{self.searchRadius:1.1f}"]

        runnable += [
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

        suc, retValue = self.runWatney(runnable)
        if not suc:
            text = self.returnCodes.get(retValue, "Unknown code")
            result["message"] = f"Watney error: [{text}]"
            self.log.warning(f"Watney error [{text}] in [{imagePath}]")
            return result

        if not wcsPath.is_file():
            result["message"] = "Solve failed"
            self.log.warning(f"Solve files for [{wcsPath}] missing")
            return result

        wcsHeader = getImageHeader(wcsPath)
        imageHeader = getImageHeader(imagePath)
        solution = getSolutionFromWCSHeader(wcsHeader, imageHeader)

        if updateHeader:
            updateImageFileHeaderWithSolution(imagePath, solution)

        result["success"] = True
        result["message"] = "Solved"
        result.update(solution)
        self.log.debug(f"Result: [{result}]")
        return result

    def abort(self) -> bool:
        """ """
        if self.process:
            self.process.kill()
            return True
        return False

    def checkAvailabilityProgram(self, appPath: Path) -> bool:
        """ """
        self.appPath = appPath

        if platform.system() == "Darwin":
            program = self.appPath / "watney-solve"
        elif platform.system() == "Linux":
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
