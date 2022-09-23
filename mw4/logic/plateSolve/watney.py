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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import subprocess
import os
import glob
import time
import platform

# external packages
from astropy.io import fits

# local imports


class Watney(object):
    """
    """

    __all__ = ['Watney']
    log = logging.getLogger(__name__)

    returnCodes = {0: 'No errors',
                   1: 'No solution',
                   }

    def __init__(self, parent):
        self.parent = parent
        self.data = parent.data
        self.tempDir = parent.tempDir
        self.workDir = parent.workDir
        self.readFitsData = parent.readFitsData
        self.getSolutionFromWCS = parent.getSolutionFromWCS
        self.getWCSHeader = parent.getWCSHeader

        self.result = {'success': False}
        self.process = None
        self.deviceName = 'Watney'
        self.indexPath = ''
        self.appPath = ''
        self.timeout = 30
        self.searchRadius = 20
        self.setDefaultPath()
        self.defaultConfig = {
            'watney': {
                'deviceName': 'Watney',
                'deviceList': ['Watney'],
                'searchRadius': 10,
                'timeout': 30,
                'appPath': self.appPath,
                'indexPath': self.indexPath,
            }
        }

    def saveConfigFile(self):
        """
        :return:
        """
        cfgFile = self.tempDir + '/watney-solve-config.yml'
        with open(cfgFile, 'w+') as outFile:
            outFile.write(f"quadDbPath: '{self.indexPath}'\n")
            outFile.write("defaultStarDetectionBgOffset: 1.0\n")
            outFile.write("defaultLowerDensityOffset: 3\n")
        return True

    def setDefaultPath(self):
        """
        :return: true for test purpose
        """
        self.appPath = self.workDir + '/watney-cli'
        self.indexPath = self.workDir + '/watney-index'
        self.saveConfigFile()
        return True

    def runWatney(self, runnable):
        """
        runASTAP solves finally the xy star list and writes the WCS data in a fits
        file format

        :param runnable: additional solver options e.g. ra and dec hint
        :return: success
        """
        timeStart = time.time()
        try:
            self.process = subprocess.Popen(args=runnable,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
            stdout, stderr = self.process.communicate(timeout=self.timeout)

        except subprocess.TimeoutExpired:
            self.log.error('Timeout happened')
            return False, -1

        except Exception as e:
            self.log.critical(f'error: {e} happened')
            return False, -2

        else:
            delta = time.time() - timeStart
            self.log.debug(f'Watney took {delta}s return code: '
                           + f'{self.process.returncode}'
                           + ' stderr: '
                           + stderr.decode().replace('\n', ' ')
                           + ' stdout: '
                           + stdout.decode().replace('\n', ' '))
        return True, int(self.process.returncode)

    def solve(self, fitsPath='', raHint=None, decHint=None, scaleHint=None,
              fovHint=None, updateFits=False):
        """
        :param fitsPath:  full path to fits file
        :param raHint:  ra dest to look for solve in J2000
        :param decHint:  dec dest to look for solve in J2000
        :param scaleHint:  scale to look for solve in J2000
        :param fovHint:  degrees FOV to look for solve in J2000
        :param updateFits:  if true update Fits image file with wcsHeader data

        :return: success
        """
        self.process = None
        self.result = {'success': False,
                       'message': 'Internal error'}
        isBlind = self.searchRadius == 180
        jsonPath = self.tempDir + '/solve.json'
        wcsPath = self.tempDir + '/temp.wcs'

        if not os.path.isfile(fitsPath):
            self.result['message'] = 'Image missing'
            self.log.warning('Image missing for solving')
            return False

        if os.path.isfile(wcsPath):
            os.remove(wcsPath)

        runnable = [self.appPath + '/watney-solve']

        if isBlind:
            runnable += ['blind']
        else:
            runnable += ['nearby']

        runnable += ['-i', fitsPath,
                     '-o', jsonPath,
                     '-w', wcsPath,
                     '--use-config', self.tempDir + '/watney-solve-config.yml',
                     '--extended', 'True']

        if fovHint is not None:
            rMin = max(fovHint / 4, 0.15)
            rMax = min(fovHint * 4, 16)
        else:
            rMin = 0.15
            rMax = 16

        if isBlind:
            runnable += ['--min-radius', f'{rMin}',
                         '--max-radius', f'{rMax}']
        else:
            runnable += ['-s', f'{self.searchRadius:1.1f}']

        if raHint is not None and decHint is not None and not isBlind:
            runnable += ['-m',
                         '-r', f'{raHint.hours}',
                         '-d', f'{decHint.degrees}',
                         '-f', f'{fovHint}']
        elif not isBlind:
            runnable += ['-h']

        suc, retValue = self.runWatney(runnable=runnable)
        if not suc:
            text = self.returnCodes.get(retValue, 'Unknown code')
            self.result['message'] = f'Watney error: [{text}]'
            self.log.warning(f'Watney error [{text}] in [{fitsPath}]')
            return False

        if not os.path.isfile(wcsPath):
            self.result['message'] = 'Solve failed'
            self.log.info(f'Solve files for [{wcsPath}] missing')
            return False

        with fits.open(wcsPath) as wcsHDU:
            wcsHeader = self.getWCSHeader(wcsHDU=wcsHDU)

        with fits.open(fitsPath, mode='update') as fitsHDU:
            solve, header = self.getSolutionFromWCS(fitsHeader=fitsHDU[0].header,
                                                    wcsHeader=wcsHeader,
                                                    updateFits=updateFits)
            self.log.trace(f'Header: [{header}]')
            self.log.debug(f'Header RA: [{header["RA"]}]'
                           f'DEC: [{header["DEC"]}')
            self.log.debug(f'Solve : [{solve}]')
            fitsHDU[0].header = header

        self.result = {
            'success': True,
            'solvedPath': fitsPath,
            'message': 'Solved',
        }
        self.result.update(solve)
        self.log.debug(f'Result: [{self.result}]')
        return True

    def abort(self):
        """
        abort stops the solving function hardly just by killing the process

        :return: success
        """
        if self.process:
            self.process.kill()
            return True
        else:
            return False

    def checkAvailability(self, appPath=None, indexPath=None):
        """
        :return: working environment found
        """
        if appPath is not None:
            self.appPath = appPath
        if indexPath is not None:
            self.indexPath = indexPath

        self.saveConfigFile()

        if platform.system() == 'Darwin':
            program = self.appPath + '/watney-solve'
        elif platform.system() == 'Linux':
            program = self.appPath + '/watney-solve'
        elif platform.system() == 'Windows':
            program = self.appPath + '/watney-solve.exe'

        if not os.path.isfile(program):
            self.log.info(f'[{program}] not found')
            sucProgram = False
        else:
            sucProgram = True

        sucInd = sum('.qdb' in s for s in glob.glob(self.indexPath + '/*.*')) == 407
        if not sucInd:
            self.log.info('No index files found')

        self.log.info(f'Watney OK, app: [{program}], index: [{self.indexPath}]')
        return sucProgram, sucInd
