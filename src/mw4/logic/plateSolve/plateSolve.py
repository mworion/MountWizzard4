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
import queue
import subprocess
import time
from mw4.base.signalsDevices import Signals
from mw4.base.tpool import Worker
from mw4.base.transform import J2000ToJNow
from mw4.gui.utilities.toolsQtWidget import sleepAndEvents
from mw4.logic.fits.fitsFunction import (
    getImageHeader,
    getSolutionFromWCSHeader,
    updateImageFileHeaderWithSolution,
)
from mw4.logic.plateSolve.astap import ASTAP
from mw4.logic.plateSolve.astrometry import Astrometry
from mw4.logic.plateSolve.watney import Watney
from pathlib import Path


class PlateSolve:
    """
    Keyword definitions could be found under
        https://fits.gsfc.nasa.gov/fits_dictionary.html
    """

    log = logging.getLogger("MW4")

    def __init__(self, app):
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.solveQueue = queue.Queue()
        self.solveLoopRunning: bool = False
        self.worker: Worker = None
        self.process = None

        self.data: dict = {}
        self.defaultConfig: dict = {"framework": "", "frameworks": {}}
        self.framework: str = ""
        self.run: dict = {
            "astrometry": Astrometry(self),
            "astap": ASTAP(self),
            "watney": Watney(self),
        }
        for fw in self.run:
            self.defaultConfig["frameworks"].update(self.run[fw].defaultConfig)

        self.signals.serverConnected.connect(self.startSolveLoop)

    def runSolverBin(self, runnable: list) -> tuple[bool, str]:
        """ """
        timeStart = time.time()
        try:
            self.process = subprocess.Popen(
                args=runnable,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            timeout = self.run[self.framework].timeout
            stdout, _ = self.process.communicate(timeout=timeout)

        except subprocess.TimeoutExpired as e:
            self.log.critical(e)
            return False, "Timeout expired"

        except Exception as e:
            self.log.critical(f"Error: {e} happened")
            return False, f"Exception {e} during process run"

        delta = time.time() - timeStart
        stdoutText = stdout.decode()
        self.log.debug(f"Solve Runtime: [{delta:2.2f}s]")
        for line in stdoutText.splitlines():
            self.log.debug(f"Solver output: [{line}]")
        rCode = int(self.process.returncode)
        suc = rCode == 0
        msg = self.run[self.framework].returnCodes.get(rCode, "Unknown code")
        return suc, msg

    def prepareResult(self, suc: bool, msg: str, imagePath: Path, wcsPath: Path, update: bool):
        """ """
        result = {"success": False, "message": msg, "imagePath": imagePath}
        if not suc:
            self.log.warning(f"Error: [{imagePath.stem}], message: {msg}")
            return result

        if not wcsPath.is_file():
            self.log.warning(f"Solve files for [{wcsPath.stem}] missing")
            result["message"] = "Solve failed, no WCS file"
            return result

        wcsHeader = getImageHeader(wcsPath)
        imageHeader = getImageHeader(imagePath)
        solution = getSolutionFromWCSHeader(wcsHeader, imageHeader)

        if update:
            updateImageFileHeaderWithSolution(imagePath, solution)

        import random

        result["success"] = bool(random.getrandbits(1))  # Placeholder for actual success logic
        result["message"] = "Fail introduced"

        # result["success"] = True
        # result["message"] = "Solved"
        result.update(solution)
        ra, dec = J2000ToJNow(
            result["raJ2000S"], result["decJ2000S"], self.app.mount.obsSite.timeJD
        )
        result["raJNowS"] = ra
        result["decJNowS"] = dec
        self.log.debug(f"Solve result:  [{imagePath.stem:10s}], [{result}]")
        return result

    def processSolveQueue(self, imagePath: Path, updateHeader: bool = False) -> None:
        """ """
        if not imagePath.is_file():
            result = {"success": False, "message": f"{imagePath} not found"}
        else:
            self.signals.message.emit("solving")
            t = f"Solver start:  [{imagePath.stem}] with [{self.framework}], "
            t += f"timeout: [{self.run[self.framework].timeout}], "
            t += f"radius: [{self.run[self.framework].searchRadius}], "
            self.log.debug(t)
            result = self.run[self.framework].solve(
                imagePath=imagePath, updateHeader=updateHeader
            )
        self.signals.message.emit("")
        self.signals.result.emit(result)

    def workerSolveLoop(self) -> None:
        """ """
        while self.solveLoopRunning:
            if self.solveQueue.empty():
                sleepAndEvents(500)
                continue
            imagePath, updateHeader = self.solveQueue.get()
            self.processSolveQueue(imagePath, updateHeader)
            self.solveQueue.task_done()

    def startSolveLoop(self) -> None:
        """ """
        self.solveLoopRunning = True
        self.worker = Worker(self.workerSolveLoop)
        self.threadPool.start(self.worker)

    def checkAvailabilityProgram(self, framework: str) -> bool:
        """ """
        appPath = Path(self.run[framework].appPath)
        return self.run[framework].checkAvailabilityProgram(appPath=appPath)

    def checkAvailabilityIndex(self, framework: str) -> bool:
        """ """
        indexPath = Path(self.run[framework].indexPath)
        return self.run[framework].checkAvailabilityIndex(indexPath=indexPath)

    def startCommunication(self) -> None:
        """ """
        sucProgram = self.checkAvailabilityProgram(self.framework)
        sucIndex = self.checkAvailabilityIndex(self.framework)
        name = self.run[self.framework].deviceName
        if not sucProgram or not sucIndex:
            return

        self.signals.deviceConnected.emit(name)
        self.signals.serverConnected.emit()

    def stopCommunication(self) -> None:
        """ """
        self.solveLoopRunning = False
        name = self.run[self.framework].deviceName
        self.signals.serverDisconnected.emit({name: 0})
        self.signals.deviceDisconnected.emit(name)

    def solve(self, imagePath: Path, updateHeader: bool = False) -> None:
        """ """
        data = (imagePath, updateHeader)
        self.solveQueue.put(data)

    def abort(self) -> bool:
        """ """
        if self.process:
            self.process.kill()
            return True
        return False
