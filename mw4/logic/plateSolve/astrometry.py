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
from mountcontrol import convert
from logic.fits.fitsFunction import getSolutionFromWCSHeader, getImageHeader
from logic.fits.fitsFunction import getHintFromImageFile
from logic.fits.fitsFunction import updateImageFileHeaderWithSolution


class Astrometry(object):
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, parent=None):
        self.parent = parent
        self.data = parent.data
        self.tempDir = parent.app.mwGlob["tempDir"]
        self.result = {"success": False}
        self.process = None
        self.indexPath = Path("")
        self.appPath = Path("")
        self.setDefaultPath()
        self.apiKey: str = ""
        self.timeout: int = 30
        self.searchRadius: int = 20
        self.deviceName: str = "ASTROMETRY.NET"
        self.defaultConfig: dict = {
            "astrometry": {
                "deviceName": "ASTROMETRY.NET",
                "deviceList": ["ASTROMETRY.NET"],
                "searchRadius": 10,
                "timeout": 30,
                "appPath": str(self.appPath),
                "indexPath": str(self.indexPath),
            }
        }

    def setDefaultPath(self) -> None:
        """ """
        if platform.system() == "Darwin":
            home = os.environ.get("HOME", "")
            self.appPath = Path("/Applications/KStars.app/Contents/MacOS/astrometry/bin")
            self.indexPath = Path(home + "/Library/Application Support/Astrometry")

        elif platform.system() == "Linux":
            self.appPath = Path("/usr/bin")
            self.indexPath = Path("/usr/share/astrometry")

        elif platform.system() == "Windows":
            self.appPath = Path("")
            self.indexPath = Path("")
        self.saveConfigFile()

    def saveConfigFile(self):
        """ """
        cfgFile = self.tempDir / "astrometry.cfg"
        with open(cfgFile, "w+") as outFile:
            outFile.write("cpulimit 300\n")
            outFile.write(f"add_path {self.indexPath}\n")
            outFile.write("autoindex\n")

    def runImage2xy(self, binPath: Path, imagePath: Path, tempPath: Path) -> bool:
        """ """
        runnable = [binPath, "-O", "-o", tempPath, imagePath]
        timeStart = time.time()
        try:
            self.process = subprocess.Popen(
                args=runnable,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, _ = self.process.communicate(timeout=self.timeout)

        except subprocess.TimeoutExpired as e:
            self.log.critical(e)
            return False

        except Exception as e:
            self.log.critical(f"error: {e} happened")
            return False

        delta = time.time() - timeStart
        stdoutText = stdout.decode().replace("\n", " ")
        self.log.debug(f"Run {delta}s, {stdoutText}")
        return self.process.returncode == 0

    def runSolveField(self, binPath: Path, configPath: Path, tempPath: Path, options: list):
        """ """
        runnable = [
            binPath,
            "--overwrite",
            "--no-remove-lines",
            "--no-plots",
            "--no-verify-uniformize",
            "--uniformize",
            "0",
            "--sort-column",
            "FLUX",
            "--scale-units",
            "app",
            "--crpix-center",
            "--cpulimit",
            str(self.timeout),
            "--config",
            configPath,
            tempPath,
        ]

        runnable += options

        timeStart = time.time()
        try:
            self.process = subprocess.Popen(
                args=runnable,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, _ = self.process.communicate(timeout=self.timeout)

        except subprocess.TimeoutExpired as e:
            self.log.critical(e)
            return False

        except Exception as e:
            self.log.critical(f"error: {e} happened")
            return False

        delta = time.time() - timeStart
        stdoutText = stdout.decode().replace("\n", " ")
        self.log.debug(f"Run {delta}s, {stdoutText}")
        return self.process.returncode == 0

    def solve(self, imagePath: Path, updateHeader: bool) -> dict:
        """ """
        self.process = None
        result = {"success": False, "message": "Internal error"}

        tempPath = self.tempDir / "temp.xy"
        configPath = self.tempDir / "astrometry.cfg"
        wcsPath = self.tempDir / "temp.wcs"
        binPathImage2xy = self.appPath / "image2xy"
        binPathSolveField = self.appPath / "solve-field"

        if wcsPath.is_file():
            os.remove(wcsPath)

        suc = self.runImage2xy(binPathImage2xy, imagePath, tempPath)
        if not suc:
            self.log.warning(f"IMAGE2XY error in [{imagePath}]")
            self.result["message"] = "image2xy failed"
            return result

        raHint, decHint, scaleHint = getHintFromImageFile(imagePath)
        searchRatio = 1.1
        ra = convert.convertToHMS(raHint)
        dec = convert.convertToDMS(decHint)
        scaleLow = scaleHint / searchRatio
        scaleHigh = scaleHint * searchRatio
        options = [
            "--scale-low",
            f"{scaleLow}",
            "--scale-high",
            f"{scaleHigh}",
            "--ra",
            f"{ra}",
            "--dec",
            f"{dec}",
            "--radius",
            f"{self.searchRadius:1.1f}",
        ]

        # split between ekos and cloudmakers as cloudmakers use an older version of
        # solve-field, which need the option '--no-fits2fits', whereas the actual
        # version used in KStars throws an error using this option.
        if "Astrometry.app" in str(self.appPath):
            options.append("--no-fits2fits")

        suc = self.runSolveField(binPathSolveField, configPath, tempPath, options)
        if not suc:
            self.log.warning(f"SOLVE-FIELD error in [{imagePath}]")
            result["message"] = "solve-field error"
            return result

        if not wcsPath.is_file():
            self.log.warning(f"Solve files for [{wcsPath}] missing")
            result["message"] = "solve failed"
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
            program = self.appPath / "solve-field"
        elif platform.system() == "Linux":
            program = self.appPath / "solve-field"
        elif platform.system() == "Windows":
            program = Path("")
        else:
            return False
        return program.is_file()

    def checkAvailabilityIndex(self, indexPath: Path) -> bool:
        """ """
        self.indexPath = indexPath
        self.saveConfigFile()

        return len(list(self.indexPath.glob("*.fits"))) > 0
