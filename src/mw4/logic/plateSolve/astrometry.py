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
import logging
import os
import platform
from mw4.logic.fits.fitsFunction import getHintFromImageFile
from mw4.mountcontrol.convert import convertToDMS, convertToHMS
from pathlib import Path
from typing import Any


class Astrometry:
    log = logging.getLogger("MW4")
    returnCodes: dict = {0: "No errors", 1: "solve-field error"}
    home = os.environ.get("HOME", "")
    apps = {
        "Darwin": {
            "appPath": Path("/Applications/KStars.app/Contents/MacOS/astrometry/bin"),
            "indexPath": Path(f"{home}/Library/Application Support/Astrometry"),
        },
        "Linux": {
            "appPath": Path("/usr/bin"),
            "indexPath": Path("/usr/share/astrometry"),
        },
        "Windows": {
            "appPath": Path(),
            "indexPath": Path(),
        },
    }

    def __init__(self, parent: Any = None) -> None:
        self.parent = parent
        self.data: dict[str, Any] = parent.data
        self.tempDir: Path = parent.app.mwGlob["tempDir"]
        self.result: dict[str, Any] = {"success": False}
        self.process: Any = None
        self.indexPath = Path()
        self.appPath = Path()
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
        self.appPath = self.apps[platform.system()]["appPath"]
        self.indexPath = self.apps[platform.system()]["indexPath"]
        self.saveConfigFile()

    def saveConfigFile(self) -> None:
        cfgFile = self.tempDir / "astrometry.cfg"
        with open(cfgFile, "w+") as outFile:
            outFile.write("cpulimit 300\n")
            outFile.write(f"add_path {self.indexPath}\n")
            outFile.write("autoindex\n")

    def solve(self, imagePath: Path, updateHeader: bool) -> dict[str, Any]:
        tempPath = self.tempDir / "temp.xy"
        configPath = self.tempDir / "astrometry.cfg"
        wcsPath = self.tempDir / "temp.wcs"
        wcsPath.unlink(missing_ok=True)

        runnable = [self.appPath / "image2xy", "-O", "-o", tempPath, imagePath]

        suc, msg = self.parent.runSolverBin(runnable)
        if not suc:
            self.log.warning(f"IMAGE2XY error in [{imagePath}]")
            return {"success": False, "message": "image2xy failed"}

        raHint, decHint, scaleHint = getHintFromImageFile(imagePath)
        searchRatio = 1.1
        ra = convertToHMS(raHint)
        dec = convertToDMS(decHint)
        scaleLow = scaleHint / searchRatio
        scaleHigh = scaleHint * searchRatio

        runnable = [
            self.appPath / "solve-field",
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

        runnable.extend(options)
        suc, msg = self.parent.runSolverBin(runnable)
        return self.parent.prepareResult(suc, msg, imagePath, wcsPath, updateHeader)

    def checkAvailabilityProgram(self, appPath: Path) -> bool:
        self.appPath = appPath

        if platform.system() == "Darwin" or platform.system() == "Linux":
            program = self.appPath / "solve-field"
        else:
            return False
        return program.is_file()

    def checkAvailabilityIndex(self, indexPath: Path) -> bool:
        self.indexPath = indexPath
        self.saveConfigFile()

        return len(list(self.indexPath.glob("*.fits"))) > 0
