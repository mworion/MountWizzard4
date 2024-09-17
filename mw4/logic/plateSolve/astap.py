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
import subprocess
import os
from os.path import normpath, join
from glob import glob
import time
import platform
from pathlib import Path

# external packages

# local imports
from logic.fits.fitsFunction import getSolutionFromWCSHeader, getImageHeader, \
    updateImageFileHeaderWithSolution


class ASTAP(object):
    """
    """
    __all__ = ['ASTAP']

    returnCodes = {0: 'No errors',
                   1: 'No solution',
                   2: 'Not enough stars detected',
                   3: 'Error reading image file',
                   32: 'No Star database found',
                   33: 'Error reading star database',
                   -9: 'Process aborted',
                   }

    log = logging.getLogger('MW4')
    
    def __init__(self, parent):
        self.parent = parent
        self.data = parent.data
        self.tempDir = parent.tempDir

        self.result = {'success': False}
        self.process = None
        self.indexPath = ''
        self.appPath = ''
        self.setDefaultPath()
        self.deviceName = 'ASTAP'
        self.timeout = 30
        self.searchRadius = 20
        self.defaultConfig = {
            'astap': {
                'deviceName': 'ASTAP',
                'deviceList': ['ASTAP'],
                'searchRadius': 20,
                'timeout': 30,
                'appPath': self.appPath,
                'indexPath': self.indexPath,
            }
        }

    def setDefaultPath(self) -> None:
        """
        """
        if platform.system() == 'Darwin':
            self.appPath = normpath('/Applications/ASTAP.app/Contents/MacOS')
            self.indexPath = normpath('/usr/local/opt/astap')

        elif platform.system() == 'Linux':
            self.appPath = normpath('/opt/astap')
            self.indexPath = normpath('/opt/astap')

        elif platform.system() == 'Windows':
            self.appPath = normpath('C:\\Program Files\\astap')
            self.indexPath = normpath('C:\\Program Files\\astap')

    def runASTAP(self, binPath: Path, tempPath: Path, imagePath: Path,
                 options: list[str]) -> [bool, str]:
        """
        """
        runnable = [binPath, '-f', imagePath, '-o', tempPath, '-wcs']
        runnable.extend(options)
        timeStart = time.time()
        try:
            self.process = subprocess.Popen(args=runnable,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
            stdout, _ = self.process.communicate(timeout=self.timeout)

        except subprocess.TimeoutExpired:
            self.log.error('Timeout happened')
            return False, 'Solving timed out'
            
        except Exception as e:
            self.log.critical(f'error: {e} happened')
            return False, 'Exception during solving'

        delta = time.time() - timeStart
        stdoutText = stdout.decode().replace("\n", " ")
        self.log.debug(f'Run {delta}s, {stdoutText}') 
        rCode = int(self.process.returncode)
        suc = rCode == 0
        msg = self.returnCodes.get(rCode, 'Unknown code')
        return suc, msg

    def solve(self, imagePath: Path, updateHeader: bool) -> dict:
        """
        """
        self.process = None
        result = {'success': False, 'message': 'Internal error'}
        
        tempPath = join(self.tempDir + 'temp')
        binPath = join(self.appPath, 'astap')
        wcsPath = join(self.tempDir + 'temp.wcs')

        if os.path.isfile(wcsPath):
            os.remove(wcsPath)

        options = ['-r', f'{self.searchRadius:1.1f}', '-t', '0.005', '-z', '0',
                   '-d', self.indexPath]

        suc, msg = self.runASTAP(binPath=binPath,
                                 imagePath=imagePath,
                                 tempPath=tempPath,
                                 options=options)
        if not suc:
            result['message'] = msg
            self.log.warning(f'ASTAP error in [{imagePath}]: {msg}')
            return result

        if not os.path.isfile(wcsPath):
            result['message'] = 'ASTAP result file missing - solve failed'
            self.log.warning(f'Solve files [{wcsPath}] for [{imagePath}] missing')
            return result

        wcsHeader = getImageHeader(imagePath=wcsPath)
        imageHeader = getImageHeader(imagePath=imagePath)
        solution = getSolutionFromWCSHeader(wcsHeader=wcsHeader, imageHeader=imageHeader)

        if updateHeader:
            updateImageFileHeaderWithSolution(imagePath, solution)

        result['success'] = True
        result['message'] = msg
        result.update(solution)
        self.log.debug(f'Result: [{result}]')
        return result

    def abort(self) -> bool:
        """
        """
        if self.process:
            self.process.kill()
            return True
        return False

    def checkAvailabilityProgram(self, appPath: Path) -> bool:
        """
        """
        self.appPath = appPath

        if platform.system() == 'Darwin':
            program = os.path.join(self.appPath, 'astap')
        elif platform.system() == 'Linux':
            program = os.path.join(self.appPath, 'astap')
        elif platform.system() == 'Windows':
            program = os.path.join(self.appPath, 'astap.exe')
        else:
            return False
        return os.path.isfile(program)

    def checkAvailabilityIndex(self, indexPath: Path) -> bool:
        """
        """
        self.indexPath = indexPath

        g17 = 'g17*.290'
        g18 = 'g18*.290'
        h17 = 'h17*.1476'
        h18 = 'h18*.1476'
        d80 = 'd80*.1476'
        d50 = 'd50*.1476'
        d20 = 'd20*.1476'
        d05 = 'd05*.1476'

        isG17 = sum('.290' in s for s in glob(join(self.indexPath, g17))) != 0
        isG18 = sum('.290' in s for s in glob(join(self.indexPath, g18))) != 0
        isH17 = sum('.1476' in s for s in glob(join(self.indexPath, h17))) != 0
        isH18 = sum('.1476' in s for s in glob(join(self.indexPath, h18))) != 0
        isD80 = sum('.1476' in s for s in glob(join(self.indexPath, d80))) != 0
        isD50 = sum('.1476' in s for s in glob(join(self.indexPath, d50))) != 0
        isD20 = sum('.1476' in s for s in glob(join(self.indexPath, d20))) != 0
        isD05 = sum('.1476' in s for s in glob(join(self.indexPath, d05))) != 0
        return any((isG17, isG18, isH17, isH18, isD05, isD20, isD50, isD80))
