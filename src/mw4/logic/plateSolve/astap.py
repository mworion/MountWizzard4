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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DeviceConfigASTAP:
    deviceName: str = field(default="")
    searchRadius: int = field(default=20)
    timeout: int = field(default=30)
    appPath: str = field(default="")
    indexPath: str = field(default="")


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
            "appPath": "/Applications/ASTAP.app/Contents/MacOS",
            "indexPath": "/usr/local/opt/astap",
        },
        "Linux": {
            "appPath": "/opt/astap",
            "indexPath": "/opt/astap",
        },
        "Windows": {
            "appPath": "C:\\Program Files\\astap",
            "indexPath": "C:\\Program Files\\astap",
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
        self.config = DeviceConfigASTAP()
        self.tempDir: Path = parent.app.mwGlob["tempDir"]
        self.result: dict[str, Any] = {"success": False}
        self.process: Any = None
        self.config.deviceName = "ASTAP"
        self.binPath: Path = self.setDefaultBinPath()
        self.config.appPath = self.setDefaultAppPath()
        self.config.indexPath = self.setDefaultIndexPath()

    def setDefaultAppPath(self) -> str:
        return self.apps[platform.system()]["appPath"]

    def setDefaultIndexPath(self) -> str:
        return self.apps[platform.system()]["indexPath"]

    def setDefaultBinPath(self) -> Path:
        return Path(self.config.appPath) / self.GUI

    def solve(self, imagePath: Path, updateHeader: bool) -> dict[str, Any]:
        tempPath = self.tempDir / "temp"
        wcsPath = self.tempDir / "temp.wcs"
        wcsPath.unlink(missing_ok=True)
        runnable = [self.binPath, "-f", imagePath, "-o", tempPath, "-wcs"]
        options = [
            "-r",
            f"{self.config.searchRadius:1.1f}",
            "-t",
            "0.005",
            "-z",
            "0",
            "-d",
            self.config.indexPath,
        ]
        runnable.extend(options)
        suc, msg = self.parent.runSolverBin(runnable)
        return self.parent.prepareResult(suc, msg, imagePath, wcsPath, updateHeader)

    def checkAvailabilityProgram(self, appPath: str) -> bool:
        self.config.appPath = appPath
        extension = ".exe" if platform.system() == "Windows" else ""
        bin1 = Path(self.config.appPath) / (self.CLI + extension)
        bin2 = Path(self.config.appPath) / (self.GUI + extension)
        if bin1.is_file() or bin2.is_file():
            self.binPath = bin1 if bin1.is_file() else bin2
            return True
        return False

    def checkAvailabilityIndex(self, indexPath: str) -> bool:
        self.config.indexPath = indexPath
        return any(len(list(self.config.indexPath.glob(i))) > 0 for i in self.indexes)
