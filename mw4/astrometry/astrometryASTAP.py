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
# written in python 3, (c) 2019, 2020 by mworion
#
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
from mw4.base.loggerMW import CustomLogger


class AstrometryASTAP(object):
    """
    the class Astrometry inherits all information and handling of astrometry.net handling

    Keyword definitions could be found under
        https://fits.gsfc.nasa.gov/fits_dictionary.html

        >>> a = AstrometryASTAP()

    """

    __all__ = ['AstrometryASTAP',
               'solve',
               'abort',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    def __init__(self, parent):
        self.parent = parent
        self.data = parent.data
        self.tempDir = parent.tempDir
        self.readFitsData = parent.readFitsData
        self.getSolutionFromWCS = parent.getSolutionFromWCS

        self.result = {'success': False}
        self.process = None
        self.name = ''
        self.indexPath = ''
        self.apiKey = ''
        self.timeout = 30
        self.searchRadius = 20
        self.environment = {}

        self.setEnvironment()

    def setEnvironment(self):
        """

        :return: true for test purpose
        """

        if platform.system() == 'Darwin':
            self.environment = {
                'ASTAP-Mac': {
                    'programPath': '/Applications/ASTAP.app/Contents/MacOS',
                    'indexPath': '/usr/local/opt/astap',
                }
            }

        elif platform.system() == 'Linux':
            self.environment = {
                'ASTAP-Linux': {
                    'programPath': '/opt/astap',
                    'indexPath': '/opt/astap',
                },
            }

        elif platform.system() == 'Windows':
            self.environment = {
                'ASTAP-Win': {
                    'programPath': 'C:\\Program Files\\astap',
                    'indexPath': 'C:\\Program Files\\astap',
                },
            }

    def runASTAP(self, binPath='', tempFile='', fitsPath='', options=''):
        """
        runASTAP solves finally the xy star list and writes the WCS data in a fits
        file format

        :param binPath:   full path to image2xy executable
        :param tempFile:  full path to star file
        :param fitsPath: full path to fits file in temp dir
        :param options: additional solver options e.g. ra and dec hint
        :return: success
        """

        runnable = [binPath,
                    '-f',
                    fitsPath,
                    '-o',
                    tempFile,
                    ]

        runnable += options

        timeStart = time.time()
        try:
            self.process = subprocess.Popen(args=runnable,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE
                                            )
            stdout, stderr = self.process.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            self.log.critical('Timeout expired')
            return False
        except Exception as e:
            self.log.critical(f'error: {e} happened')
            return False
        else:
            delta = time.time() - timeStart
            self.log.info(f'astap took {delta}s return code: '
                          + str(self.process.returncode)
                          + ' stderr: '
                          + stderr.decode().replace('\n', ' ')
                          + ' stdout: '
                          + stdout.decode().replace('\n', ' ')
                          )

        success = (self.process.returncode == 0)

        return success

    @staticmethod
    def getWCSHeader(wcsTextFile=None):
        """
        getWCSHeader reads the text file give by astap line by line and returns the values as
        part of a header part of a fits HDU header back.

        :param wcsTextFile: fits file with wcs data
        :return: wcsHeader
        """

        if not wcsTextFile:
            return None

        tempString = ''
        for line in wcsTextFile:
            if line.startswith('END'):
                continue
            tempString += line

        wcsHeader = fits.PrimaryHDU().header.fromstring(tempString,
                                                        sep='\n')

        return wcsHeader

    def solve(self, fitsPath='', raHint=None, decHint=None, scaleHint=None,
              updateFits=False):
        """
        Solve uses the astap solver capabilities. The intention is to use an
        offline solving capability, so we need a installed instance. As we go multi
        platform and we need to focus on MW function, we use the astap package
        which could be downloaded for all platforms. Many thanks to them providing such a
        nice package.

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
            self.result['message'] = 'image missing'
            self.log.info('Image missing for solving')
            return False

        tempFile = self.tempDir + '/temp'
        wcsPath = self.tempDir + '/temp.wcs'

        if os.path.isfile(wcsPath):
            os.remove(wcsPath)

        binPathASTAP = self.environment[self.name]['programPath'] + '/astap'

        raFITS, decFITS, scaleFITS, _, _ = self.readFitsData(fitsPath=fitsPath)

        # if parameters are passed, they have priority
        if raHint is None:
            raHint = raFITS.hours
        if decHint is None:
            decHint = decFITS.degrees

        options = ['-ra',
                   f'{raHint}',
                   '-spd',
                   f'{decHint + 90}',
                   '-r',
                   f'{self.searchRadius:1.1f}',
                   '-t',
                   '0.005',
                   '-z',
                   '0',
                   ]

        suc = self.runASTAP(binPath=binPathASTAP,
                            fitsPath=fitsPath,
                            tempFile=tempFile,
                            options=options,
                            )
        if not suc:
            self.result['message'] = 'astap error'
            self.log.error(f'astap error in [{fitsPath}]')
            return False

        if not os.path.isfile(wcsPath):
            self.result['message'] = 'solve failed'
            self.log.info(f'solve files for [{wcsPath}] missing')
            return False

        with open(wcsPath) as wcsTextFile:
            wcsHeader = self.getWCSHeader(wcsTextFile=wcsTextFile)

        with fits.open(fitsPath, mode='update') as fitsHDU:
            solve, header = self.getSolutionFromWCS(fitsHeader=fitsHDU[0].header,
                                                    wcsHeader=wcsHeader,
                                                    updateFits=updateFits)
            fitsHDU[0].header = header

        self.result = {
            'success': True,
            'solvedPath': fitsPath,
            'message': 'Solved',
        }
        self.result.update(solve)

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

    def checkAvailability(self):
        """
        checkAvailability searches for the existence of the core runtime modules from
        all applications. to this family belong:
            astrometry.net namely image2xy and solve-field
            ASTP files

        :return: available solver environments
        """

        available = list()
        for solver in self.environment:
            suc = True

            if solver == 'ASTAP-Win':
                program = self.environment[solver]['programPath'] + '/astap.exe'
                index = self.environment[solver]['indexPath'] + '/*.290'
            elif solver == 'ASTAP-Mac':
                program = self.environment[solver]['programPath'] + '/astap'
                index = self.environment[solver]['indexPath'] + '/*.290'
            elif solver == 'ASTAP-Linux':
                program = self.environment[solver]['programPath'] + '/astap'
                index = self.environment[solver]['indexPath'] + '/*.290'

            # checking binaries
            if not os.path.isfile(program):
                self.log.info(f'{program} not found')
                suc = False

            # checking indexes
            if not glob.glob(index):
                self.log.info('no index files found')
                suc = False

            if suc:
                available.append(solver)
                self.log.info(f'binary and index files available for {solver}')

        return available
