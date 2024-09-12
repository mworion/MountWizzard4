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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import os
import queue
from os.pathlib import Path

# external packages
from astropy.io import fits

# local imports
from mountcontrol.convert import convertToAngle
from base.tpool import Worker
from gui.utilities.toolsQtWidget import sleepAndEvents
from logic.plateSolveSignals import PlateSolveSignals
from logic.plateSolve.astrometry import Astrometry
from logic.plateSolve.astap import ASTAP
from logic.plateSolve.watney import Watney


class PlateSolve:
    """
    Keyword definitions could be found under
        https://fits.gsfc.nasa.gov/fits_dictionary.html
    """
    __all__ = ['PlateSolve']

    log = logging.getLogger('MW4')

    def __init__(self, app):
        self.app = app
        self.msg = app.msg
        self.threadPool = app.threadPool
        self.signals = PlateSolveSignals()
        self.solvingQueue = queue.Queue()
        self.solveLoopRunning = False
        self.tempDir = app.mwGlob['tempDir']
        self.workDir = app.mwGlob['workDir']
    
        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = ''
        self.run = {
            'astrometry': Astrometry(self),
            'astap': ASTAP(self),
            'watney': Watney(self),
        }
        for fw in self.run:
            self.defaultConfig['frameworks'].update(self.run[fw].defaultConfig)

    def processSolveQueue(self) - None:
        """
        """
        imagePath, updateHeader = self.solveQueue.get()
        if not os.path.isfile(imagePath):
            result = {'success': False, 'message': f'{imagePath} not found'}
        else 
            result = self.run[self.framework].solve(**data)
        self.signals.done.emit(result)
         
    def workerSolveLoop(self) -> None:
        """
        """
        while self.solveLoopRunning:
            if self.solveQueue.empty():
                sleepAndEvents(500)
                continue
            self.processSolveQueue() 
            
    def startSolveLoop(self) -> None:
        """
        """
        worker = Worker(self.workerSolveLoop)
        self.threadPool.start(worker)

    def startCommunication(self):
        """
        """
        sucApp = self.checkAvailabilityProgram()
        sucIndex = self.checkAvailabilityIndex()
        name = self.run[self.framework].deviceName
        if not sucApp or not sucIndex:
            return

        self.solveLoopRunning = True
        self.startSolveLoop()
        self.signals.deviceConnected.emit(name)
        self.signals.serverConnected.emit()

    def stopCommunication(self):
        """
        """
        self.solveLoopRunning = False
        name = self.run[self.framework].deviceName
        self.signals.serverDisconnected.emit({name: 0})
        self.signals.deviceDisconnected.emit(name)
        
    def solve(imagePath: Path, updateHeader: bool = False) -> None:
        """
        """
         data = (imagePath, updateHeader)
         self.solveQueue.put(data)
         
    def abort(self) -> None:
        """
        """
        self.run[self.framework].abort()

    def checkAvailabilityProgram(self) -> bool:
        """
        """
        return self.run[self.framework].checkAvailabilityProgram()

    def checkAvailabilityIndex(self) -> bool:
        """
        """
        return self.run[self.framework].checkAvailabilityIndex() 
