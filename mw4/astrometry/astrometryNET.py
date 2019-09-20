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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import subprocess
import os
import time
from collections import namedtuple
# external packages
import numpy as np
from astropy.io import fits
from forwardable import forwardable, def_delegators
# local imports
from mw4.base import transform
from mw4.definitions import Solution, Solve


@forwardable()
class AstrometryNET(object):
    """
    the class Astrometry inherits all information and handling of astrometry.net handling

    Keyword definitions could be found under
        https://fits.gsfc.nasa.gov/fits_dictionary.html

        >>> astrometry = AstrometryNET(app=app,
        >>>                         )

    """

    def_delegators('parent',
                   'tempDir, readFitsData, getSolutionFromWCS',
                   )

    __all__ = ['AstrometryNET',
               'solveNET',
               'abortNET',
               ]

    version = '0.100.0'
    logger = logging.getLogger(__name__)

    def __init__(self, parent):
        self.parent = parent
        self.result = Solution(success=False, solve=Solve, message='')
        self.process = None

    def runImage2xy(self, binPath='', tempPath='', fitsPath='', timeout=30):
        """
        runImage2xy extracts a list of stars out of the fits image. there is a timeout of
        3 seconds set to get the process finished

        :param binPath:   full path to image2xy executable
        :param tempPath:  full path to star file
        :param fitsPath:  full path to fits file
        :param timeout:
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
            stdout, stderr = self.process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as e:
            self.logger.debug(e)
            return False
        except Exception as e:
            self.logger.error(f'error: {e} happened')
            return False
        else:
            delta = time.time() - timeStart
            self.logger.debug(f'image2xy took {delta}s return code: '
                              + str(self.process.returncode)
                              + ' stderr: '
                              + stderr.decode().replace('\n', ' ')
                              + ' stdout: '
                              + stdout.decode().replace('\n', ' ')
                              )

        success = (self.process.returncode == 0)
        return success

    def runSolveField(self, binPath='', configPath='', tempPath='', options='', timeout=30):
        """
        runSolveField solves finally the xy star list and writes the WCS data in a fits
        file format

        :param binPath:   full path to image2xy executable
        :param configPath: full path to astrometry.cfg file
        :param tempPath:  full path to star file
        :param options: additional solver options e.g. ra and dec hint
        :param timeout:
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
                    '--cpulimit', str(timeout),
                    '--config',
                    configPath,
                    tempPath,
                    ]

        runnable += options

        timeStart = time.time()
        try:
            self.process = subprocess.Popen(args=runnable,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE
                                            )
            stdout, stderr = self.process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as e:
            self.logger.debug(e)
            return False
        except Exception as e:
            self.logger.error(f'error: {e} happened')
            return False
        else:
            delta = time.time() - timeStart
            self.logger.debug(f'solve-field took {delta}s return code: '
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
        wcsHeader = wcsHDU[0].header
        return wcsHeader

    def solve(self, solver={}, fitsPath='', raHint=None, decHint=None, scaleHint=None,
              radius=2, timeout=30, updateFits=False):
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

        :param solver: which astrometry implementation to choose
        :param fitsPath:  full path to fits file
        :param raHint:  ra dest to look for solve in J2000
        :param decHint:  dec dest to look for solve in J2000
        :param scaleHint:  scale to look for solve in J2000
        :param radius:  search radius around target coordinates
        :param timeout: time after the subprocess will be killed.
        :param updateFits:  if true update Fits image file with wcsHeader data

        :return: success
        """

        self.process = None
        self.result = Solution(success=False, solve=Solve, message='default')

        if not os.path.isfile(fitsPath):
            self.result = Solution(success=False, solve=Solve, message='image missing')
            return False

        tempPath = self.tempDir + '/temp.xy'
        configPath = self.tempDir + '/astrometry.cfg'
        solvedPath = self.tempDir + '/temp.solved'
        wcsPath = self.tempDir + '/temp.wcs'
        binPathImage2xy = solver['programPath'] + '/image2xy'
        binPathSolveField = solver['programPath'] + '/solve-field'

        if os.path.isfile(wcsPath):
            os.remove(wcsPath)

        cfgFile = self.tempDir + '/astrometry.cfg'
        with open(cfgFile, 'w+') as outFile:
            outFile.write('cpulimit 300\n')
            outFile.write(f'add_path {solver["indexPath"]}\n')
            outFile.write('autoindex\n')

        suc = self.runImage2xy(binPath=binPathImage2xy,
                               tempPath=tempPath,
                               fitsPath=fitsPath,
                               timeout=timeout,
                               )
        if not suc:
            self.logger.error(f'image2xy error in [{fitsPath}]')
            self.result = Solution(success=False, solve=Solve, message='image2xy error')
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
                   f'{radius:1.1f}',
                   ]

        # split between ekos and cloudmakers as cloudmakers use an older version of
        # solve-field, which need the option '--no-fits2fits', whereas the actual
        # version used in KStars throws an error using this option.
        if 'Astrometry.app' in solver['programPath']:
            options.append('--no-fits2fits')

        suc = self.runSolveField(binPath=binPathSolveField,
                                 configPath=configPath,
                                 tempPath=tempPath,
                                 options=options,
                                 timeout=timeout,
                                 )
        if not suc:
            self.logger.error(f'solve-field error in [{fitsPath}]')
            self.result = Solution(success=False, solve=Solve, message='solve-field error')
            return False

        if not os.path.isfile(solvedPath):
            self.logger.debug(f'solve files for [{fitsPath}] missing')
            self.result = Solution(success=False, solve=Solve, message='solve failed')
            return False

        if not os.path.isfile(wcsPath):
            self.logger.debug(f'solve files for [{wcsPath}] missing')
            self.result = Solution(success=False, solve=Solve, message='solve failed')
            return False

        with fits.open(wcsPath) as wcsHDU:
            wcsHeader = self.getWCSHeader(wcsHDU=wcsHDU)

        with fits.open(fitsPath, mode='update') as fitsHDU:
            solve, header = self.getSolutionFromWCS(fitsHeader=fitsHDU[0].header,
                                                    wcsHeader=wcsHeader,
                                                    updateFits=updateFits)
            fitsHDU[0].header = header

        solve = Solve(raJ2000=solve.raJ2000,
                      decJ2000=solve.decJ2000,
                      angle=solve.angle,
                      scale=solve.scale,
                      error=solve.error,
                      flipped=solve.flipped,
                      path=fitsPath)
        self.result = Solution(success=True, solve=solve, message='solved')
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
