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
from mw4.base import transform


class AstrometryNET(object):
    """
    the class Astrometry inherits all information and handling of astrometry.net handling

    Keyword definitions could be found under
        https://fits.gsfc.nasa.gov/fits_dictionary.html

        >>> astrometry = AstrometryNET(app=app,
        >>>                         )

    """

    __all__ = ['AstrometryNET',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    def __init__(self, parent=None):
        self.parent = parent
        self.data = parent.data
        self.tempDir = parent.tempDir
        self.readFitsData = parent.readFitsData
        self.getSolutionFromWCS = parent.getSolutionFromWCS

        self.result = {'success': False}
        self.process = None
        self.apiKey = ''
        self.timeout = 30
        self.searchRadius = 20
        self.name = 'ASTROMETRY.NET'

        if platform.system() == 'Darwin':
            home = os.environ.get('HOME', '')
            self.appPath = '/Applications/KStars.app/Contents/MacOS/astrometry/bin'
            self.indexPath = home + '/Library/Application Support/Astrometry'

        elif platform.system() == 'Linux':
            self.appPath = '/usr/bin'
            self.indexPath = '/usr/share/astrometry'

        elif platform.system() == 'Windows':
            self.appPath = ''
            self.indexPath = ''

    def runImage2xy(self, binPath='', tempPath='', fitsPath=''):
        """
        runImage2xy extracts a list of stars out of the fits image. there is a timeout of
        3 seconds set to get the process finished

        :param binPath:   full path to image2xy executable
        :param tempPath:  full path to star file
        :param fitsPath:  full path to fits file
        :return: success
        """

        runnable = [binPath,
                    '-O',
                    '-o',
                    tempPath,
                    fitsPath]

        timeStart = time.time()
        try:
            self.process = subprocess.Popen(args=runnable,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            )
            stdout, stderr = self.process.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired as e:
            self.log.critical(e)
            return False
        except Exception as e:
            self.log.critical(f'error: {e} happened')
            return False
        else:
            delta = time.time() - timeStart
            self.log.info(f'image2xy took {delta}s return code: '
                          + str(self.process.returncode)
                          + ' stderr: '
                          + stderr.decode().replace('\n', ' ')
                          + ' stdout: '
                          + stdout.decode().replace('\n', ' ')
                          )

        success = (self.process.returncode == 0)
        return success

    def runSolveField(self, binPath='', configPath='', tempPath='', options=''):
        """
        runSolveField solves finally the xy star list and writes the WCS data in a fits
        file format

        :param binPath:   full path to image2xy executable
        :param configPath: full path to astrometry.cfg file
        :param tempPath:  full path to star file
        :param options: additional solver options e.g. ra and dec hint
        :return: success
        """

        runnable = [binPath,
                    '--overwrite',
                    '--no-remove-lines',
                    '--no-plots',
                    '--no-verify-uniformize',
                    '--uniformize', '0',
                    '--sort-column', 'FLUX',
                    '--scale-units', 'app',
                    '--crpix-center',
                    '--cpulimit', str(self.timeout),
                    '--config',
                    configPath,
                    tempPath,
                    ]

        runnable += options

        timeStart = time.time()
        try:
            self.process = subprocess.Popen(args=runnable,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            )
            stdout, stderr = self.process.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired as e:
            self.log.critical(e)
            return False
        except Exception as e:
            self.log.critical(f'error: {e} happened')
            return False
        else:
            delta = time.time() - timeStart
            self.log.info(f'solve-field took {delta}s return code: '
                          + str(self.process.returncode)
                          + ' stderr: '
                          + stderr.decode().replace('\n', ' ')
                          + ' stdout: '
                          + stdout.decode().replace('\n', ' ')
                          )

        success = (self.process.returncode == 0)

        return success

    @staticmethod
    def getWCSHeader(wcsHDU=None):
        """
        getWCSHeader returns the header part of a fits HDU

        :param wcsHDU: fits file with wcs data
        :return: wcsHeader
        """
        if wcsHDU is None:
            return None

        wcsHeader = wcsHDU[0].header
        return wcsHeader

    def solve(self, fitsPath='', raHint=None, decHint=None, scaleHint=None,
              updateFits=False):
        """
        Solve uses the astrometry.net solver capabilities. The intention is to use an
        offline solving capability, so we need a installed instance. As we go multi
        platform and we need to focus on MW function, we use the astrometry.net package
        which is distributed with KStars / EKOS. Many thanks to them providing such a
        nice package.
        As we go using astrometry.net we focus on the minimum feature set possible to
        omit many of the installation and wrapping work to be done. So we only support
        solving of FITS files, use no python environment for astrometry.net parts (as we
        could access these via MW directly)

        The base outside ideas of implementation come from astrometry.net itself and the
        astrometry implementation from cloudmakers.eu (another nice package for MAC Astro
        software)

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
            return False

        tempPath = self.tempDir + '/temp.xy'
        configPath = self.tempDir + '/astrometry.cfg'
        solvedPath = self.tempDir + '/temp.solved'
        wcsPath = self.tempDir + '/temp.wcs'
        binPathImage2xy = self.appPath + '/image2xy'
        binPathSolveField = self.appPath + '/solve-field'

        if os.path.isfile(wcsPath):
            os.remove(wcsPath)

        cfgFile = self.tempDir + '/astrometry.cfg'
        with open(cfgFile, 'w+') as outFile:
            outFile.write('cpulimit 300\n')
            outFile.write(f'add_path {self.indexPath}\n')
            outFile.write('autoindex\n')

        # using sextractor in astrometry.net and  KStars
        """
        with open('default.param', 'w+') as outFile:
            outFile.write('MAG_AUTO  Kron-like elliptical aperture magnitude    [mag]\n')
            outFile.write('X_IMAGE   Object position along x                    [pixel]\n')
            outFile.write('Y_IMAGE   Object position along y                    [pixel]\n')

        with open('default.conv', 'w+') as outFile:
            outFile.write('CONV NORM\n')
            outFile.write('1 2 1\n')
            outFile.write('2 4 2\n')
            outFile.write('1 2 1\nn')
        """
        suc = self.runImage2xy(binPath=binPathImage2xy,
                               tempPath=tempPath,
                               fitsPath=fitsPath,
                               )
        if not suc:
            self.log.error(f'image2xy error in [{fitsPath}]')
            self.result['message'] = 'image2xy failed'
            return False

        raFITS, decFITS, scaleFITS, _, _ = self.readFitsData(fitsPath=fitsPath)

        # if parameters are passed, they have priority
        if raHint is None:
            raHint = raFITS
        if decHint is None:
            decHint = decFITS
        if scaleHint is None:
            scaleHint = scaleFITS

        searchRatio = 1.1
        ra = transform.convertToHMS(raHint)
        dec = transform.convertToDMS(decHint)
        scaleLow = scaleHint / searchRatio
        scaleHigh = scaleHint * searchRatio
        options = ['--scale-low',
                   f'{scaleLow}',
                   '--scale-high',
                   f'{scaleHigh}',
                   '--ra',
                   f'{ra}',
                   '--dec',
                   f'{dec}',
                   '--radius',
                   f'{self.searchRadius:1.1f}',
                   ]

        # split between ekos and cloudmakers as cloudmakers use an older version of
        # solve-field, which need the option '--no-fits2fits', whereas the actual
        # version used in KStars throws an error using this option.
        if 'Astrometry.app' in self.appPath:
            options.append('--no-fits2fits')

        suc = self.runSolveField(binPath=binPathSolveField,
                                 configPath=configPath,
                                 tempPath=tempPath,
                                 options=options,
                                 )
        if not suc:
            self.log.error(f'solve-field error in [{fitsPath}]')
            self.result['message'] = 'solve-field error'
            return False

        if not os.path.isfile(solvedPath):
            self.log.info(f'solve files for [{fitsPath}] missing')
            self.result['message'] = 'solve failed'
            return False

        if not os.path.isfile(wcsPath):
            self.log.info(f'solve files for [{wcsPath}] missing')
            self.result['message'] = 'solve failed'
            return False

        with fits.open(wcsPath) as wcsHDU:
            wcsHeader = self.getWCSHeader(wcsHDU=wcsHDU)

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
        abortNET stops the solving function hardly just by killing the process

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

        :return: working environment found
        """

        if platform.system() == 'Darwin':
            program = self.appPath + '/solve-field'
            index = self.indexPath + '/*.fits'
        elif platform.system() == 'Linux':
            program = self.appPath + '/solve-field'
            index = self.indexPath + '/*.fits'
        elif platform.system() == 'Windows':
            program = ''
            index = ''

        # checking binaries
        if not os.path.isfile(program):
            self.log.info(f'{program} not found')
            sucProgram = False
        else:
            sucProgram = True

        # checking indexes
        if not glob.glob(index):
            self.log.info('no index files found')
            sucIndex = False
        else:
            sucIndex = True

        self.log.info('Binary and index files available for ASTROMETRY.NET')

        return sucProgram, sucIndex
