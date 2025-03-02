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


class ASTAP(object):
    """ """

    returnCodes = {
        0: "No errors",
        1: "No solution",
        2: "Not enough stars detected",
        3: "Error reading image file",
        32: "No Star database found",
        33: "Error reading star database",
        -9: "Process aborted",
    }

    log = logging.getLogger("MW4")

    def __init__(self, parent):
        self.parent = parent
        self.data = parent.data
        self.tempDir = parent.app.mwGlob["tempDir"]

        self.result: dict = {"success": False}
        self.process = None
        self.indexPath = Path("")
        self.appPath = Path("")
        self.setDefaultPath()
        self.deviceName: str = "ASTAP"
        self.timeout: int = 30
        self.searchRadius: int = 20
        self.defaultConfig: dict = {
            "astap": {
                "deviceName": "ASTAP",
                "deviceList": ["ASTAP"],
                "searchRadius": 20,
                "timeout": 30,
                "appPath": str(self.appPath),
                "indexPath": str(self.indexPath),
            }
        }

    def setDefaultPath(self) -> None:
        """ """
        if platform.system() == "Darwin":
            self.appPath = Path("/Applications/ASTAP.app/Contents/MacOS")
            self.indexPath = Path("/usr/local/opt/astap")

        elif platform.system() == "Linux":
            self.appPath = Path("/opt/astap")
            self.indexPath = Path("/opt/astap")

        elif platform.system() == "Windows":
            self.appPath = Path("C:\\Program Files\\astap")
            self.indexPath = Path("C:\\Program Files\\astap")

    def runASTAP(
        self, binPath: Path, imagePath: Path, tempPath: Path, options: list[str]
    ) -> [bool, str]:
        """ """
        runnable = [binPath, "-f", imagePath, "-o", tempPath, "-wcs"]
        runnable.extend(options)
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

        tempPath = self.tempDir / "temp"
        binPath = self.appPath / "astap"
        wcsPath = self.tempDir / "temp.wcs"

        if wcsPath.is_file():
            os.remove(wcsPath)

        options = [
            "-r",
            f"{self.searchRadius:1.1f}",
            "-t",
            "0.005",
            "-z",
            "0",
            "-d",
            self.indexPath,
        ]

        suc, msg = self.runASTAP(binPath, imagePath, tempPath, options)
        if not suc:
            result["message"] = msg
            self.log.warning(f"ASTAP error in [{imagePath}]: {msg}")
            return result

        if not wcsPath.is_file():
            result["message"] = "ASTAP result file missing - solve failed"
            self.log.warning(f"Solve files [{wcsPath}] for [{imagePath}] missing")
            return result

        wcsHeader = getImageHeader(wcsPath)
        imageHeader = getImageHeader(imagePath)
        solution = getSolutionFromWCSHeader(wcsHeader, imageHeader)

        if updateHeader:
            updateImageFileHeaderWithSolution(imagePath, solution)

        result["success"] = True
        result["message"] = msg
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
            program = self.appPath / "astap"
        elif platform.system() == "Linux":
            program = self.appPath / "astap"
        elif platform.system() == "Windows":
            program = self.appPath / "astap.exe"
        else:
            return False
        return program.is_file()

    def checkAvailabilityIndex(self, indexPath: Path) -> bool:
        """ """
        self.indexPath = indexPath

        g17 = "g17*.290"
        g18 = "g18*.290"
        h17 = "h17*.1476"
        h18 = "h18*.1476"
        d80 = "d80*.1476"
        d50 = "d50*.1476"
        d20 = "d20*.1476"
        d05 = "d05*.1476"

        isG17 = len(list(self.indexPath.glob(g17))) > 0
        isG18 = len(list(self.indexPath.glob(g18))) > 0
        isH17 = len(list(self.indexPath.glob(h17))) > 0
        isH18 = len(list(self.indexPath.glob(h18))) > 0
        isD80 = len(list(self.indexPath.glob(d80))) > 0
        isD50 = len(list(self.indexPath.glob(d50))) > 0
        isD20 = len(list(self.indexPath.glob(d20))) > 0
        isD05 = len(list(self.indexPath.glob(d05))) > 0
        return any((isG17, isG18, isH17, isH18, isD05, isD20, isD50, isD80))
