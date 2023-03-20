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
# written in python3, (c) 2019-2023 by mworion
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
                   -1: 'Solving timed out',
                   -2: 'Exception during solving',
                   }

    log = logging.getLogger(__name__)

    def __init__(self, parent):
        self.parent = parent
        self.data = parent.data
        self.tempDir = parent.tempDir
        self.readFitsData = parent.readFitsData
        self.getSolutionFromWCS = parent.getSolutionFromWCS
        self.getWCSHeader = parent.getWCSHeader

        self.result = {'success': False}
        self.process = None
        self.deviceName = 'ASTAP'
        self.indexPath = ''
        self.appPath = ''
        self.timeout = 30
        self.searchRadius = 20
        self.setDefaultPath()
        self.defaultConfig = {
            'astap': {
                'deviceName': 'ASTAP',
                'deviceList': ['ASTAP'],
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
        if platform.system() == 'Darwin':
            self.appPath = '/Applications/ASTAP.app/Contents/MacOS'
            self.indexPath = '/usr/local/opt/astap'

        elif platform.system() == 'Linux':
            self.appPath = '/opt/astap'
            self.indexPath = '/opt/astap'

        elif platform.system() == 'Windows':
            self.appPath = 'C:\\Program Files\\astap'
            self.indexPath = 'C:\\Program Files\\astap'

        return True

    def runASTAP(self, binPath='', tempFile='', fitsPath='', options=''):
        """
        runASTAP solves finally the xy star list and writes the WCS data in
        a fits file format

        :param binPath:   full path to astap executable
        :param tempFile:  full path to star file
        :param fitsPath: full path to fits file in temp dir
        :param options: additional solver options e.g. ra and dec hint
        :return: success
        """
        runnable = [binPath, '-f', fitsPath, '-o', tempFile, '-wcs']
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
            self.log.debug(f'ASTAP took {delta}s return code: '
                           + f'{self.process.returncode}'
                           + f' [{fitsPath}]'
                           + ' stderr: '
                           + stderr.decode().replace('\n', ' ')
                           + ' stdout: '
                           + stdout.decode().replace('\n', ' ')
                           )

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

        if not os.path.isfile(fitsPath):
            self.result['message'] = 'Image missing'
            self.log.warning('Image missing for solving')
            return False

        tempFile = os.path.normpath(self.tempDir + '/temp')
        wcsPath = os.path.normpath(self.tempDir + '/temp.wcs')
        if os.path.isfile(wcsPath):
            os.remove(wcsPath)

        binPathASTAP = self.appPath + '/astap'
        options = ['-r', f'{self.searchRadius:1.1f}',
                   '-t', '0.005',
                   '-z', '0',
                   '-d', self.indexPath]

        if raHint is not None and decHint is not None:
            options += ['-ra', f'{raHint.hours}',
                        '-spd', f'{decHint.degrees + 90}']

        if self.searchRadius == 180:
            options += ['-fov', '0']

        suc, retValue = self.runASTAP(binPath=binPathASTAP,
                                      fitsPath=fitsPath,
                                      tempFile=tempFile,
                                      options=options)
        if not suc:
            text = self.returnCodes.get(retValue, 'Unknown code')
            self.result['message'] = f'ASTAP error: [{text}]'
            self.log.warning(f'ASTAP error [{text}] in [{fitsPath}]')
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

        g17 = '/g17*.290'
        g18 = '/g18*.290'
        h17 = '/h17*.1476'
        h18 = '/h18*.1476'
        d50 = '/d50*.1476'
        d20 = '/d20*.1476'
        d05 = '/d05*.1476'
        if platform.system() == 'Darwin':
            program = self.appPath + '/astap'
        elif platform.system() == 'Linux':
            program = self.appPath + '/astap'
        elif platform.system() == 'Windows':
            program = self.appPath + '/astap.exe'

        program = os.path.normpath(program)
        if not os.path.isfile(program):
            self.log.info(f'[{program}] not found')
            sucProgram = False
        else:
            sucProgram = True

        isG17 = sum('.290' in s for s in glob.glob(self.indexPath + g17)) == 290
        isG18 = sum('.290' in s for s in glob.glob(self.indexPath + g18)) == 290
        isH17 = sum('.1476' in s for s in glob.glob(self.indexPath + h17)) == 1476
        isH18 = sum('.1476' in s for s in glob.glob(self.indexPath + h18)) == 1476
        isD50 = sum('.1476' in s for s in glob.glob(self.indexPath + d50)) == 1476
        isD20 = sum('.1476' in s for s in glob.glob(self.indexPath + d20)) == 1169
        isD05 = sum('.1476' in s for s in glob.glob(self.indexPath + d05)) == 1476
        if not any((isG17, isG18, isH17, isH18, isD05, isD20, isD50)):
            self.log.info('No index files found')
            sucIndex = False
        else:
            sucIndex = True

        self.log.info(f'ASTAP OK, app: [{program}], index: [{self.indexPath}]')
        self.log.info(f'ASTAP Index G17:{isG17}, G18:{isG18}, H17:{isH17}, H18:{isH18}')
        self.log.info(f'ASTAP Index D50:{isD50}, D20:{isD20}, D05:{isD05}')
        return sucProgram, sucIndex
