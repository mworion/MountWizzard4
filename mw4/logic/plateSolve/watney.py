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

    returnCodes = {0: 'No errors',
                   1: 'No solution',
                   2: 'Not enough stars detected',
                   3: 'Error reading image file',
                   32: 'No Star database found',
                   33: 'Error reading star database',
                   -1: 'Solving timed out',
                   -2: 'Exception during solving',
                   }

    log = logging.getLogger(__name__)

    def __init__(self, parent):
        self.parent = parent
        self.data = parent.data
        self.tempDir = parent.tempDir
        self.workDir = parent.workDir
        self.readFitsData = parent.readFitsData
        self.getSolutionFromWCS = parent.getSolutionFromWCS

        self.result = {'success': False}
        self.process = None
        self.deviceName = 'ASTAP'
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

    def setDefaultPath(self):
        """
        :return: true for test purpose
        """
        self.appPath = self.workDir + '/watney'
        self.indexPath = self.workDir + '/watney_index'
        self.saveConfigFile()
        return True

    def saveConfigFile(self):
        """
        :return:
        """
        cfgFile = self.tempDir + '/watney-solve-config.yml'
        with open(cfgFile, 'w+') as outFile:
            outFile.write(f'quadDbPath: {self.indexPath} n')
        return True

    def runWatney(self, binPath='', tempFile='', fitsPath='', options=''):
        """
        runASTAP solves finally the xy star list and writes the WCS data in a fits
        file format

        :param binPath:   full path to cli executable
        :param tempFile:  full path to star file
        :param fitsPath: full path to fits file in temp dir
        :param options: additional solver options e.g. ra and dec hint
        :return: success
        """
        runnable = [binPath, '-f', fitsPath, '-o', tempFile]
        runnable += options
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
                           + f' [{fitsPath}]'
                           + ' stderr: '
                           + stderr.decode().replace('\n', ' ')
                           + ' stdout: '
                           + stdout.decode().replace('\n', ' ')
                           )

        return True, int(self.process.returncode)

    @staticmethod
    def getWCSHeader(wcsTextFile=None):
        """
        getWCSHeader reads the text file give by astap line by line and returns
        the values as part of a header part of a fits HDU header back.

        :param wcsTextFile: fits file with wcs data
        :return: wcsHeader
        """
        if not wcsTextFile:
            return None

        tempString = ''
        for line in wcsTextFile:
            if line.startswith('END'):
                continue
            if line.startswith('COMMENT'):
                continue
            tempString += line

        wcsHeader = fits.PrimaryHDU().header.fromstring(tempString,
                                                        sep='\n')
        return wcsHeader

    def solve(self, fitsPath='', raHint=None, decHint=None, scaleHint=None,
              updateFits=False):
        """
        Solve uses the astap solver capabilities. The intention is to use an
        offline solving capability, so we need a installed instance. As we go
        multi-platform, and we need to focus on MW function, we use the astap
        package which could be downloaded for all platforms. Many thanks
        providing such a nice package.

        :param fitsPath:  full path to fits file
        :param raHint:  ra dest to look for solve in J2000
        :param decHint:  dec dest to look for solve in J2000
        :param scaleHint:  scale to look for solve in J2000
        :param updateFits:  if true update Fits image file with wcsHeader data

        :return: success
        """
        self.process = None
        self.result = {'success': False}

        if not os.path.isfile(fitsPath):
            self.result['message'] = 'Image missing'
            self.log.debug('Image missing for solving')
            return False

        tempFile = self.tempDir + '/temp'
        wcsPath = self.tempDir + '/temp.wcs'
        if os.path.isfile(wcsPath):
            os.remove(wcsPath)

        binPathWatney = self.appPath + '/watney-solve'
        options = ['-r', f'{self.searchRadius:1.1f}',
                   '-t', '0.005',
                   '-z', '0']

        if raHint is not None and decHint is not None:
            options += ['-ra', f'{raHint.hours}',
                        '-spd', f'{decHint.degrees + 90}']

        if self.searchRadius == 180:
            options += ['-fov', '0']

        suc, retValue = self.runWatney(binPath=binPathWatney,
                                       fitsPath=fitsPath,
                                       tempFile=tempFile,
                                       options=options)
        if not suc:
            text = self.returnCodes.get(retValue, 'Unknown code')
            self.result['message'] = f'Watney error: [{text}]'
            self.log.warning(f'Watney error [{text}] in [{fitsPath}]')
            return False

        if not os.path.isfile(wcsPath):
            self.result['message'] = 'Solve failed'
            self.log.debug(f'Solve files for [{wcsPath}] missing')
            return False

        with open(wcsPath) as wcsTextFile:
            wcsHeader = self.getWCSHeader(wcsTextFile=wcsTextFile)

        with fits.open(fitsPath, mode='update') as fitsHDU:
            solve, header = self.getSolutionFromWCS(fitsHeader=fitsHDU[0].header,
                                                    wcsHeader=wcsHeader,
                                                    updateFits=updateFits)
            self.log.debug(f'Header: [{header}]')
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
        program = self.appPath + '/watney-solve'

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
