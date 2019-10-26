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
import shutil
import time
from collections import namedtuple
# external packages
from astropy.io import fits
import numpy as np
from forwardable import forwardable, def_delegators
# local imports
from mw4.base import transform
from mw4.definitions import Solution, Solve


@forwardable()
class AstrometryASTAP(object):
    """
    the class Astrometry inherits all information and handling of astrometry.net handling

    Keyword definitions could be found under
        https://fits.gsfc.nasa.gov/fits_dictionary.html

        >>> astrometry = AstrometryASTAP()

    """

    def_delegators('parent',
                   'tempDir, readFitsData, getSolutionFromWCS',
                   )

    __all__ = ['AstrometryASTAP',
               'solveASTAP',
               'abortASTAP',
               ]

    version = '0.100.0'
    logger = logging.getLogger(__name__)

    def __init__(self, parent):
        self.parent = parent
        self.result = Solution(success=False, solve=Solve, message='-')
        self.process = None

    def runASTAP(self, binPath='', tempFile='', fitsPath='', options='', timeout=30):
        """
        runASTAP solves finally the xy star list and writes the WCS data in a fits
        file format

        :param binPath:   full path to image2xy executable
        :param tempFile:  full path to star file
        :param fitsPath: full path to fits file in temp dir
        :param options: additional solver options e.g. ra and dec hint
        :param timeout:
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

    @staticmethod
    def getWCSHeader(wcsTextFile=None):
        """
        getWCSHeader reads the text file give by astap line by line and returns the values as
        part of a header part of a fits HDU header back.

        :param wcsTextFile: fits file with wcs data
        :return: wcsHeader
        """

        tempString = ''
        for line in wcsTextFile:
            if line.startswith('END'):
                continue
            tempString += line

        wcsHeader = fits.PrimaryHDU().header.fromstring(tempString,
                                                        sep='\n')

        return wcsHeader

    def solve(self, solver={}, fitsPath='', raHint=None, decHint=None, scaleHint=None,
              radius=2, timeout=30, updateFits=False):
        """
        Solve uses the astap solver capabilities. The intention is to use an
        offline solving capability, so we need a installed instance. As we go multi
        platform and we need to focus on MW function, we use the astap package
        which could be downloaded for all platforms. Many thanks to them providing such a
        nice package.

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
            self.logger.info('Image missing for solving')
            return False

        tempFile = self.tempDir + '/temp'
        wcsPath = self.tempDir + '/temp.wcs'

        if os.path.isfile(wcsPath):
            os.remove(wcsPath)

        binPathASTAP = solver['programPath'] + '/astap'

        _, _, scaleFITS, raFITS, decFITS = self.readFitsData(fitsPath=fitsPath)

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
                   '-t',
                   '0.005',
                   '-z',
                   '0',
                   ]

        suc = self.runASTAP(binPath=binPathASTAP,
                            fitsPath=fitsPath,
                            tempFile=tempFile,
                            options=options,
                            timeout=timeout,
                            )
        if not suc:
            self.result = Solution(success=False, solve=Solve, message='astap error')
            self.logger.error(f'astap error in [{fitsPath}]')
            return False

        if not os.path.isfile(wcsPath):
            self.result = Solution(success=False, solve=Solve, message='solve failed')
            self.logger.debug(f'solve files for [{wcsPath}] missing')
            return False

        with open(wcsPath) as wcsTextFile:
            wcsHeader = self.getWCSHeader(wcsTextFile=wcsTextFile)

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
        abort stops the solving function hardly just by killing the process

        :return: success
        """

        if self.process:
            self.process.kill()
            return True
        else:
            return False
