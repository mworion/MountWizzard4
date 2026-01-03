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
import logging
import platform
from pathlib import Path


class ASTAP:
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

    def solve(self, imagePath: Path, updateHeader: bool) -> dict:
        """ """
        tempPath = self.tempDir / "temp"
        binPath = self.appPath / "astap"
        wcsPath = self.tempDir / "temp.wcs"
        wcsPath.unlink(missing_ok=True)

        runnable = [binPath, "-f", imagePath, "-o", tempPath, "-wcs"]
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
        """ """
        self.appPath = appPath

        if platform.system() == "Darwin" or platform.system() == "Linux":
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
