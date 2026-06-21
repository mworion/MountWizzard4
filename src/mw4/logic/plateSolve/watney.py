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
from collections.abc import Any


@dataclass
class DeviceConfigWatney:
    deviceName: str = field(default="")
    searchRadius: int = field(default=20)
    timeout: int = field(default=30)
    appPath: str = field(default="")
    indexPath: str = field(default="")


class Watney:
    log = logging.getLogger("MW4")
    returnCodes: dict = {0: "No errors", 1: "No solution"}

    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self.data: dict[str, Any] = parent.data
        self.config = DeviceConfigWatney()
        self.tempDir: Path = parent.app.mwGlob["tempDir"]
        self.workDir: Path = parent.app.mwGlob["workDir"]
        self.result: dict[str, Any] = {"success": False}
        self.process: Any = None
        self.config.deviceName = "Watney"
        self.config.appPath = self.setDefaultAppPath()
        self.config.indexPath = self.setDefaultIndexPath()
        self.saveConfigFile()

    def setDefaultAppPath(self) -> str:
        return str(self.workDir / "watney-cli")

    def setDefaultIndexPath(self) -> str:
        return str(self.workDir / "watney-index")

    def saveConfigFile(self) -> None:
        cfgFile = self.tempDir / "watney-solve-config.yml"
        with open(cfgFile, "w+") as outFile:
            outFile.write(f"quadDbPath: '{self.config.indexPath}'\n")
            outFile.write("defaultStarDetectionBgOffset: 1.0\n")
            outFile.write("defaultLowerDensityOffset: 3\n")

    def solve(self, imagePath: Path, updateHeader: bool) -> dict[str, Any]:
        isBlind = self.config.searchRadius == 180
        jsonPath = self.tempDir / "solve.json"
        wcsPath = self.tempDir / "temp.wcs"
        wcsPath.unlink(missing_ok=True)

        runnable = [Path(self.config.appPath) / "watney-solve"]
        if isBlind:
            runnable += ["blind"]
            runnable += ["--min-radius", "0.15", "--max-radius", "16"]
        else:
            runnable += ["nearby", "-h"]
            runnable += ["-s", f"{self.config.searchRadius:1.1f}"]

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

    def checkAvailabilityProgram(self, appPath: str) -> bool:
        self.config.appPath = appPath
        if platform.system() == "Darwin" or platform.system() == "Linux":
            program = Path(self.config.appPath) / "watney-solve"
        elif platform.system() == "Windows":
            program = Path(self.config.appPath) / "watney-solve.exe"
        else:
            return False
        return program.is_file()

    def checkAvailabilityIndex(self, indexPath: str) -> bool:
        self.config.indexPath = indexPath
        self.saveConfigFile()
        return len(list(self.config.indexPath.glob("*.*"))) > 0
