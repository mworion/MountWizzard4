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
from dataclasses import dataclass, field
from mw4.logic.fits.fitsFunction import getHintFromImageFile
from mw4.mountcontrol.convert import convertToDMS, convertToHMS
from pathlib import Path
from typing import Any


@dataclass
class DeviceConfigASTROMETRY:
    deviceName: str = field(default="")
    searchRadius: int = field(default=20)
    timeout: int = field(default=30)
    appPath: str = field(default="")
    indexPath: str = field(default="")
    apiKey: str = field(default="")


class Astrometry:
    log = logging.getLogger("MW4")
    returnCodes: dict = {0: "No errors", 1: "solve-field error"}
    home = os.environ.get("HOME", "")
    apps = {
        "Darwin": {
            "appPath": "/Applications/KStars.app/Contents/MacOS/astrometry/bin",
            "indexPath": f"{home}/Library/Application Support/Astrometry",
        },
        "Linux": {
            "appPath": "/usr/bin",
            "indexPath": "/usr/share/astrometry",
        },
        "Windows": {
            "appPath": "",
            "indexPath": "",
        },
    }

    def __init__(self, parent: Any = None) -> None:
        self.parent = parent
        self.data: dict[str, Any] = parent.data
        self.config = DeviceConfigASTROMETRY()
        self.tempDir: Path = parent.app.mwGlob["tempDir"]
        self.result: dict[str, Any] = {"success": False}
        self.process: Any = None
        self.config.deviceName = "ASTROMETRY.NET"
        self.config.appPath = self.setDefaultAppPath()
        self.config.indexPath = self.setDefaultIndexPath()
        self.saveConfigFile()

    def setDefaultAppPath(self) -> str:
        return self.apps[platform.system()]["appPath"]

    def setDefaultIndexPath(self) -> str:
        return self.apps[platform.system()]["indexPath"]

    def saveConfigFile(self) -> None:
        cfgFile = self.tempDir / "astrometry.cfg"
        with open(cfgFile, "w+") as outFile:
            outFile.write("cpulimit 300\n")
            outFile.write(f"add_path {self.config.indexPath}\n")
            outFile.write("autoindex\n")

    def solve(self, imagePath: Path, updateHeader: bool) -> dict[str, Any]:
        tempPath = self.tempDir / "temp.xy"
        configPath = self.tempDir / "astrometry.cfg"
        wcsPath = self.tempDir / "temp.wcs"
        wcsPath.unlink(missing_ok=True)
        runnable = [Path(self.config.appPath) / "image2xy", "-O", "-o", tempPath, imagePath]
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
            Path(self.config.appPath) / "solve-field",
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
            str(self.config.timeout),
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
            f"{self.config.searchRadius:1.1f}",
        ]
        # split between ekos and cloudmakers as cloudmakers use an older version of
        # solve-field, which need the option '--no-fits2fits', whereas the actual
        # version used in KStars throws an error using this option.
        if "Astrometry.app" in self.config.appPath:
            options.append("--no-fits2fits")
        runnable.extend(options)
        suc, msg = self.parent.runSolverBin(runnable)
        return self.parent.prepareResult(suc, msg, imagePath, wcsPath, updateHeader)

    def checkAvailabilityProgram(self, appPath: str) -> bool:
        self.config.appPath = appPath
        if platform.system() == "Darwin" or platform.system() == "Linux":
            program = Path(self.config.appPath) / "solve-field"
        else:
            return False
        return program.is_file()

    def checkAvailabilityIndex(self, indexPath: str) -> bool:
        self.config.indexPath = indexPath
        self.saveConfigFile()
        return len(list(self.config.indexPath.glob("*.fits"))) > 0
