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
import os
import queue
from pathlib import Path

# external packages

# local imports
from base.tpool import Worker
from gui.utilities.toolsQtWidget import sleepAndEvents
from base.signalsDevices import Signals
from logic.plateSolve.astrometry import Astrometry
from logic.plateSolve.astap import ASTAP
from logic.plateSolve.watney import Watney


class PlateSolve:
    """
    Keyword definitions could be found under
        https://fits.gsfc.nasa.gov/fits_dictionary.html
    """

    log = logging.getLogger("MW4")

    def __init__(self, app):
        self.app = app
        self.msg = app.msg
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.solveQueue = queue.Queue()
        self.solveLoopRunning: bool = False
        self.worker: Worker = None

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

    def processSolveQueue(self, imagePath: Path, updateHeader: bool = False) -> None:
        """ """
        if not os.path.isfile(imagePath):
            result = {"success": False, "message": f"{imagePath} not found"}
        else:
            self.signals.message.emit("solving")
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

    def abort(self) -> None:
        """ """
        self.run[self.framework].abort()
