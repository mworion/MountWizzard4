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
# Python  v3.7.3
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
import glob
import re
import fnmatch
import platform
import time
from collections import namedtuple
# external packages
import PyQt5.QtWidgets
from mw4.base import transform
from skyfield.api import Angle
from astropy.io import fits
from astropy.wcs import WCS
import astropy.wcs
from PyQt5.QtTest import QTest
import numpy as np
# local imports
from mw4.base import tpool
from mw4.definitions import Solution, Solve


class AstrometrySignals(PyQt5.QtCore.QObject):
    """
    The AstrometrySignals class offers a list of signals to be used and instantiated by the
    Worker class to get signals for error, finished and result to be transferred to the
    caller back
    """

    __all__ = ['AstrometrySignals']
    version = '0.1'

    done = PyQt5.QtCore.pyqtSignal(object)
    result = PyQt5.QtCore.pyqtSignal(object)
    message = PyQt5.QtCore.pyqtSignal(object)


class Astrometry(object):
    """
    the class Astrometry inherits all information and handling of astrometry.net handling

    Keyword definitions could be found under
        https://fits.gsfc.nasa.gov/fits_dictionary.html

        >>> astrometry = Astrometry(tempDir=tempDir,
        >>>                         threadPool=threadpool
        >>>                         )

    """

    __all__ = ['Astrometry',
               'solve',
               'solveThreading',
               'checkAvailability',
               ]

    version = '0.60'
    logger = logging.getLogger(__name__)

    def __init__(self, tempDir='', threadPool=None):
        self.tempDir = tempDir
        self.threadPool = threadPool
        self.mutexSolve = PyQt5.QtCore.QMutex()
        self.signals = AstrometrySignals()
        self.process = None
        self.available = {}
        self.result = (False, [])

        if platform.system() == 'Darwin':
            home = os.environ.get('HOME')

            self.binPath = {
                'CloudMakers': '/Applications/Astrometry.app/Contents/MacOS',
            }
            # getting all versions of KStars, of the are multiple versions in app folder
            pattern = re.compile(fnmatch.translate('kstars*.app'), re.IGNORECASE)
            header = '/Applications'
            trailer = '/Contents/MacOS/astrometry/bin'
            for name in sorted(os.listdir('/Applications')):
                if not pattern.match(name):
                    continue
                title = name.strip('.app')
                appPath = f'{header}/{name}{trailer}'
                self.binPath[title] = appPath
            self.indexPath = home + '/Library/Application Support/Astrometry'

        elif platform.system() == 'Linux':
            self.binPath = {
                'astrometry-glob': '/usr/bin',
                'astrometry-local': '/usr/local/astrometry/bin',
            }
            self.indexPath = '/usr/share/astrometry'

        else:
            self.binPath = {}
            self.indexPath = ''

        self.checkAvailability()

    def checkAvailability(self):
        """
        checkAvailability searches for the existence of the core runtime modules from
        astrometry.net namely image2xy and solve-field

        :return: True if local solve and components is available
        """

        self.available = {}
        for app, path in self.binPath.items():
            suc = True
            binPathSolveField = path + '/solve-field'
            binPathImage2xy = path + '/image2xy'

            # checking binaries
            if not os.path.isfile(binPathSolveField):
                self.logger.error(f'{binPathSolveField} not found')
                suc = False
            if not os.path.isfile(binPathImage2xy):
                self.logger.error(f'{binPathImage2xy} not found')
                suc = False

            # checking indexes
            if not glob.glob(self.indexPath + '/index-4*.fits'):
                self.logger.error('no index files found')
                suc = False
            if suc:
                self.available[app] = path
                self.logger.info(f'binary and index files available for {app}')

        return True

    def readFitsData(self, fitsPath):
        """
        readFitsData reads the fits file with the image and tries to get some key
        fields out of the header for preparing the solver.

        :param fitsPath: fits file with image data
        :return: raHint, decHint, scaleHint
        """

        with fits.open(fitsPath) as fitsHDU:
            fitsHeader = fitsHDU[0].header

            # todo: there might be the necessity to read more alternative header info
            # todo: the actual definition fit for EKOS

            scaleHint = float(fitsHeader.get('SCALE', 0))
            raHint = transform.convertToAngle(fitsHeader.get('RA', 0), isHours=True)
            decHint = transform.convertToAngle(fitsHeader.get('DEC', 0), isHours=False)

        self.logger.debug(f'RA: {raHint}, DEC: {decHint}, Scale: {scaleHint}')

        return raHint, decHint, scaleHint

    @staticmethod
    def getWCSHeader(wcsHDU=''):
        """

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
        getSolutionFromWCS reads the fits header containing the wcs data and returns the
        basic data needed.
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
        angle, scale, flipped = self.calcAngleScaleFromWCS(wcsHeader=wcsHeader)

        raMount = transform.convertToAngle(fitsHeader.get('RA'), isHours=True)
        decMount = transform.convertToAngle(fitsHeader.get('DEC'), isHours=False)

        deltaRA = raJ2000.hours - raMount.hours
        deltaDEC = decJ2000.degrees - decMount.degrees
        error = np.sqrt(np.square(deltaRA) + np.square(deltaDEC))
        # would like to have the error RMS in arcsec
        error *= 3600

        solve = Solve(raJ2000=raJ2000,
                      decJ2000=decJ2000,
                      angle=angle,
                      scale=scale,
                      error=error,
                      flipped=flipped)

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

        return solve, fitsHeader

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
                    '--no-plots',
                    '--no-remove-lines',
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

    def abort(self):
        """

        :return: success
        """

        if self.process:
            self.process.kill()

        return True

    def solve(self, app='', fitsPath='', raHint=None, decHint=None, scaleHint=None,
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
        :return: ra, dec, angle, scale, flipped
        """

        self.process = None
        self.result = Solution(success=False,
                               solve=[])

        if not os.path.isfile(fitsPath):
            return False
        if app not in self.binPath:
            return False

        xyPath = self.tempDir + '/temp.xy'
        configPath = self.tempDir + '/astrometry.cfg'
        solvedPath = self.tempDir + '/temp.solved'
        wcsPath = self.tempDir + '/temp.wcs'
        binPathImage2xy = self.binPath[app] + '/image2xy'
        binPathSolveField = self.binPath[app] + '/solve-field'

        cfgFile = self.tempDir + '/astrometry.cfg'
        with open(cfgFile, 'w+') as outFile:
            outFile.write(f'cpulimit 60\nadd_path {self.indexPath}\nautoindex\n')

        suc = self.runImage2xy(binPath=binPathImage2xy,
                               xyPath=xyPath,
                               fitsPath=fitsPath,
                               timeout=timeout,
                               )
        if not suc:
            self.logger.error(f'image2xy error in [{fitsPath}]')
            return False

        raFITS, decFITS, scaleFITS = self.readFitsData(fitsPath=fitsPath)

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

        self.result = Solution(success=True,
                               solve=solve)
        return True

    def solveClear(self):
        """
        the cyclic or long lasting tasks for solving the image should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour.

        :return:
        """

        self.mutexSolve.unlock()
        self.signals.done.emit(self.result)
        self.signals.message.emit('')

    def solveThreading(self, app='', fitsPath='', raHint=None, decHint=None, scaleHint=None,
                       radius=2, timeout=30, updateFits=False):
        """
        solveThreading is the wrapper for doing the solve process in a threadpool
        environment of Qt. Otherwise the HMI would be stuck all the time during solving.
        it is done with an securing mutex to avoid starting solving twice. to solveClear
        is the partner of solve Threading

        :param app: which astrometry implementation to choose
        :param fitsPath: full path to the fits image file to be solved
        :param raHint:  ra dest to look for solve in J2000
        :param decHint:  dec dest to look for solve in J2000
        :param scaleHint:  scale to look for solve in J2000
        :param radius:  search radius around target coordinates
        :param timeout: as said
        :param updateFits: flag, if the results should be written to the original file
        :return: success
        """

        if not os.path.isfile(fitsPath):
            self.signals.done.emit(self.result)
            return False
        if not self.checkAvailability():
            self.signals.done.emit(self.result)
            return False
        if not self.mutexSolve.tryLock():
            self.logger.info('overrun in solve threading')
            self.signals.done.emit(self.result)
            return False

        self.signals.message.emit('solving')
        worker = tpool.Worker(self.solve,
                              app=app,
                              fitsPath=fitsPath,
                              raHint=raHint,
                              decHint=decHint,
                              scaleHint=scaleHint,
                              radius=radius,
                              timeout=timeout,
                              updateFits=updateFits,
                              )
        worker.signals.finished.connect(self.solveClear)
        self.threadPool.start(worker)

        return True
