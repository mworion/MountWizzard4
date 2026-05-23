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
import platform
from pathlib import Path
from typing import Any


class ASTAP:
    log = logging.getLogger("MW4")
    GUI = "astap"
    CLI = "astap_cli"
    indexes = [
        "g17*.290",
        "g18*.290",
        "h17*.1476",
        "h18*.1476",
        "d80*.1476",
        "d50*.1476",
        "d20*.1476",
        "d05*.1476",
    ]
    apps = {
        "Darwin": {
            "appPath": Path("/Applications/ASTAP.app/Contents/MacOS"),
            "indexPath": Path("/usr/local/opt/astap"),
        },
        "Linux": {
            "appPath": Path("/opt/astap"),
            "indexPath": Path("/opt/astap"),
        },
        "Windows": {
            "appPath": Path("C:\\Program Files\\astap"),
            "indexPath": Path("C:\\Program Files\\astap"),
        },
    }
    returnCodes = {
        0: "No errors",
        1: "No solution",
        2: "Not enough stars detected",
        3: "Error reading image file",
        32: "No Star database found",
        33: "Error reading star database",
        -9: "Process aborted",
    }

    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self.data: dict[str, Any] = parent.data
        self.tempDir: Path = parent.app.mwGlob["tempDir"]

        self.result: dict[str, Any] = {"success": False}
        self.process: Any = None
        self.indexPath: Path = Path()
        self.appPath: Path = Path()
        self.binPath: Path = Path()
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
        self.appPath = self.apps[platform.system()]["appPath"]
        self.indexPath = self.apps[platform.system()]["indexPath"]
        self.binPath = self.appPath / self.GUI

    def solve(self, imagePath: Path, updateHeader: bool) -> dict[str, Any]:
        tempPath = self.tempDir / "temp"
        wcsPath = self.tempDir / "temp.wcs"
        wcsPath.unlink(missing_ok=True)

        runnable = [self.binPath, "-f", imagePath, "-o", tempPath, "-wcs"]
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
        runnable.extend(options)
        suc, msg = self.parent.runSolverBin(runnable)
        return self.parent.prepareResult(suc, msg, imagePath, wcsPath, updateHeader)

    def checkAvailabilityProgram(self, appPath: Path) -> bool:
        self.appPath = appPath

        bin1 = self.appPath / self.GUI
        bin2 = self.appPath / self.CLI

        if bin1.is_file() or bin2.is_file():
            self.binPath = bin1 if bin1.is_file() else bin2
            return True

        return False

    def checkAvailabilityIndex(self, indexPath: Path) -> bool:
        self.indexPath = indexPath
        return any(len(list(self.indexPath.glob(i))) > 0 for i in self.indexes)
