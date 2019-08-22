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
# local imports
from mw4.base import transform
from mw4.definitions import Solution, Solve


class AstrometryNET(object):
    """
    the class Astrometry inherits all information and handling of astrometry.net handling

    Keyword definitions could be found under
        https://fits.gsfc.nasa.gov/fits_dictionary.html

        >>> astrometry = Astrometry(app=app,
        >>>                         tempDir=tempDir,
        >>>                         threadPool=threadpool
        >>>                         )

    """

    __all__ = ['AstrometryNET',
               'solveNET',
               'abortNET',
               ]

    version = '0.100.0'
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.result = (False, [])
        self.process = None

    def runImage2xy(self, binPath='', xyPath='', fitsPath='', timeout=30):
        """
        runImage2xy extracts a list of stars out of the fits image. there is a timeout of
        3 seconds set to get the process finished

        :param binPath:   full path to image2xy executable
        :param xyPath:  full path to star file
        :param fitsPath:  full path to fits file
        :param timeout:
        :return: success
        """

        runnable = [binPath,
                    '-O',
                    '-o',
                    xyPath,
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

    def runSolveField(self, binPath='', configPath='', xyPath='', options='', timeout=30):
        """
        runSolveField solves finally the xy star list and writes the WCS data in a fits
        file format

        :param binPath:   full path to image2xy executable
        :param configPath: full path to astrometry.cfg file
        :param xyPath:  full path to star file
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
                    xyPath,
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
    def getWCSHeader(wcsHDU=''):
        """
        getWCSHeader returns the header part of a fits HDU

        :param wcsHDU: fits file with wcs data
        :return: wcsHeader
        """
        wcsHeader = wcsHDU[0].header
        return wcsHeader

    @staticmethod
    def calcAngleScaleFromWCS(wcsHeader=None):
        """
        calcAngleScaleFromWCS as the name says. important is to use the numpy arctan2
        function, because it handles the zero points and extend the calculation back
        to the full range from -pi to pi

        :return: angle in degrees and scale in arc second per pixel (app) and status if
                 image is flipped
        """

        CD11 = wcsHeader.get('CD1_1', 0)
        CD12 = wcsHeader.get('CD1_2', 0)
        CD21 = wcsHeader.get('CD2_1', 0)
        CD22 = wcsHeader.get('CD2_2', 0)

        flipped = (CD11 * CD22 - CD12 * CD21) < 0

        angleRad = np.arctan2(CD12, CD11)
        angle = np.degrees(angleRad)
        scale = CD11 / np.cos(angleRad) * 3600

        return angle, scale, flipped

    def getSolutionFromWCS(self, fitsHeader=None, wcsHeader=None, updateFits=False):
        """
        getSolutionFromWCS reads the wcs fits file and uses the data in the header
        containing the wcs data and returns the basic data needed.
        in addition it embeds it to the given fits file with image. it removes all
        entries starting with some keywords given in selection. we starting with
        HISTORY

        :param fitsHeader:
        :param wcsHeader:
        :param updateFits:
        :return: ra in hours, dec in degrees, angle in degrees, scale in arcsec/pixel
                 error in arcsec and flag if image is flipped
        """

        raJ2000 = transform.convertToAngle(wcsHeader.get('CRVAL1'), isHours=True)
        decJ2000 = transform.convertToAngle(wcsHeader.get('CRVAL2'), isHours=False)

        if self.app.mainW.ui.enableNoise.isChecked():
            raJ2000 = Angle(hours=raJ2000.hours + np.random.randn() / 10)
            decJ2000 = Angle(degrees=decJ2000.degrees + np.random.randn() / 10)

        angle, scale, flipped = self.calcAngleScaleFromWCS(wcsHeader=wcsHeader)

        raMount = transform.convertToAngle(fitsHeader.get('RA'), isHours=True)
        decMount = transform.convertToAngle(fitsHeader.get('DEC'), isHours=False)

        # todo: it would be nice, if adding, subtracting of angels are part of skyfield
        deltaRA = raJ2000._degrees - raMount._degrees
        deltaDEC = decJ2000.degrees - decMount.degrees
        error = np.sqrt(np.square(deltaRA) + np.square(deltaDEC))
        # would like to have the error RMS in arcsec
        error *= 3600

        solve = Solve(raJ2000=raJ2000,
                      decJ2000=decJ2000,
                      angle=angle,
                      scale=scale,
                      error=error,
                      flipped=flipped,
                      path='')

        if not updateFits:
            return solve, fitsHeader

        remove = ['COMMENT', 'HISTORY']
        fitsHeader.update({k: wcsHeader[k] for k in wcsHeader if k not in remove})

        fitsHeader['RA'] = solve.raJ2000._degrees
        fitsHeader['OBJCTRA'] = transform.convertToHMS(solve.raJ2000)
        fitsHeader['DEC'] = solve.decJ2000.degrees
        fitsHeader['OBJCTDEC'] = transform.convertToDMS(solve.decJ2000)
        fitsHeader['SCALE'] = solve.scale
        fitsHeader['PIXSCALE'] = solve.scale
        fitsHeader['ANGLE'] = solve.angle
        fitsHeader['FLIPPED'] = solve.flipped
        # kee the old values ra, dec as well
        fitsHeader['RA_OLD'] = raMount._degrees
        fitsHeader['DEC_OLD'] = decMount.degrees

        return solve, fitsHeader

    def solveNET(self, app='', fitsPath='', raHint=None, decHint=None, scaleHint=None,
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

        xyPath = self.tempDir + '/temp.xy'
        configPath = self.tempDir + '/astrometry.cfg'
        solvedPath = self.tempDir + '/temp.solved'
        wcsPath = self.tempDir + '/temp.wcs'
        binPathImage2xy = self.solveApp[app]['programPath'] + '/image2xy'
        binPathSolveField = self.solveApp[app]['programPath'] + '/solve-field'

        cfgFile = self.tempDir + '/astrometry.cfg'
        with open(cfgFile, 'w+') as outFile:
            outFile.write('cpulimit 300\n')
            outFile.write(f'add_path {self.solveApp[app]["indexPath"]}\n')
            outFile.write('autoindex\n')

        suc = self.runImage2xy(binPath=binPathImage2xy,
                               xyPath=xyPath,
                               fitsPath=fitsPath,
                               timeout=timeout,
                               )
        if not suc:
            self.logger.error(f'image2xy error in [{fitsPath}]')
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
        if app == 'CloudMakers':
            options.append('--no-fits2fits')

        suc = self.runSolveField(binPath=binPathSolveField,
                                 configPath=configPath,
                                 xyPath=xyPath,
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

    def abortNET(self):
        """
        abortNET stops the solving function hardly just by killing the process

        :return: success
        """

        if self.process:
            self.process.kill()
            return True
        else:
            return False
