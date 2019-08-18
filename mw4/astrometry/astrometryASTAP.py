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
import fnmatch
import time
from collections import namedtuple
# external packages
from astropy.io import fits
# local imports
from mw4.base import transform
from mw4.definitions import Solution, Solve


class AstrometryASTAP(object):
    """
    the class Astrometry inherits all information and handling of astrometry.net handling

    Keyword definitions could be found under
        https://fits.gsfc.nasa.gov/fits_dictionary.html

        >>> astrometry = AstrometryASTAP()

    """

    __all__ = ['AstrometryASTAP',
               'solveASTAP',
               'abortASTAP',
               ]

    version = '0.100.0'
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.result = (False, [])
        self.process = None

    def runASTAP(self, binPath='', fitsTempPath='', options='', timeout=30):
        """
        runSolveField solves finally the xy star list and writes the WCS data in a fits
        file format

        :param binPath:   full path to image2xy executable
        :param fitsTempPath: full path to fits file in temp dir
        :param options: additional solver options e.g. ra and dec hint
        :param timeout:
        :return: success
        """

        runnable = [binPath,
                    fitsTempPath,
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
            self.logger.debug(f'astap took {delta}s return code: '
                              + str(self.process.returncode)
                              + ' stderr: '
                              + stderr.decode().replace('\n', ' ')
                              + ' stdout: '
                              + stdout.decode().replace('\n', ' ')
                              )

        success = (self.process.returncode == 0)

        return success

    def solveASTAP(self, app='', fitsPath='', raHint=None, decHint=None, scaleHint=None,
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

        :param app: which astrometry implementation to choose
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
        self.result = Solution(success=False,
                               solve=[])

        if not os.path.isfile(fitsPath):
            return False

        fitsTempPath = self.tempDir + '/temp.solved'
        wcsPath = self.tempDir + '/temp.wcs'

        binPathASTAP = self.binPath[app]

        raFITS, decFITS, scaleFITS = self.readFitsData(fitsPath=fitsPath)

        # if parameters are passed, they have priority
        if raHint is None:
            raHint = raFITS
        if decHint is None:
            decHint = decFITS

        options = ['-ra',
                   f'{raHint}',
                   '-spd',
                   f'{decHint + 90}',
                   '-r',
                   f'{radius:1.1f}',
                   ]

        suc = self.runASTAP(binPath=binPathASTAP,
                            fitsTempPath=fitsTempPath,
                            options=options,
                            timeout=timeout,
                            )
        if not suc:
            self.logger.error(f'solve-field error in [{fitsPath}]')
            return False
        if not (os.path.isfile(solvedPath) and os.path.isfile(wcsPath)):
            self.logger.error(f'solve files for [{fitsPath}] missing')
            return False

        with fits.open(wcsPath) as wcsHDU:
            wcsHeader = self.getWCSHeader(wcsHDU=wcsHDU)

        with fits.open(fitsPath, mode='update') as fitsHDU:
            solve, header = self.getSolutionFromWCS(wcsHeader=wcsHeader,
                                                    fitsHeader=fitsHDU[0].header,
                                                    updateFits=updateFits)
            fitsHDU[0].header = header

        solve = Solve(raJ2000=solve.raJ2000,
                      decJ2000=solve.decJ2000,
                      angle=solve.angle,
                      scale=solve.scale,
                      error=solve.error,
                      flipped=solve.flipped,
                      path=fitsPath)
        self.result = Solution(success=True,
                               solve=solve)
        return True

    def abortASTAP(self):
        """
        abortNET stops the solving function hardly just by killing the process

        :return: success
        """

        if self.process:
            self.process.kill()
            return True
        else:
            return False
