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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import subprocess
import os
import glob
import platform
import time
from collections import namedtuple
# external packages
import PyQt5.QtWidgets
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
        self.available = {}
        self.result = (False, [])

        if platform.system() == 'Darwin':
            home = os.environ.get('HOME')
            self.binPath = {
                'KStars': '/Applications/kstars.app/Contents/MacOS/astrometry/bin',
                'CloudMakers': '/Applications/Astrometry.app/Contents/MacOS',
            }
            self.indexPath = home + '/Library/Application Support/Astrometry'

        elif platform.system() == 'Linux':
            self.binPath = {
                'astrometry.net': '/usr/bin',
                'astrometry.net local': '/usr/local/astrometry/bin',
            }
            self.indexPath = '/usr/share/astrometry'

        else:
            self.binPath = {}
            self.indexPath = ''

        cfgFile = self.tempDir + '/astrometry.cfg'
        with open(cfgFile, 'w+') as outFile:
            outFile.write(f'cpulimit 30\nadd_path {self.indexPath}\nautoindex\n')

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

    def stringToDegree(self, value):
        """
        stringToDegree takes any form of HMS / DMS string format and tries to convert it
        to a decimal number.

        :param value:
        :return: value as decimal in degrees or None if not succeeded
        """

        if not isinstance(value, str):
            return None
        if not len(value):
            return None
        if value.count('+') > 1:
            return None
        if value.count('-') > 1:
            return None

        # managing different coding styles
        value = value.replace('*', ' ')
        value = value.replace(':', ' ')
        value = value.replace('deg', ' ')
        value = value.replace('"', ' ')
        value = value.replace('\'', ' ')
        value = value.split()

        try:
            value = [float(x) for x in value]
        except Exception as e:
            self.logger.debug(f'error: {e}, value: {value}')
            return None
        sign = 1 if value[0] > 0 else -1
        value[0] = abs(value[0])

        if len(value) == 3:
            value = sign * (value[0] + value[1] / 60 + value[2] / 3600)
            return value
        elif len(value) == 2:
            value = sign * (value[0] + value[1] / 60)
            return value
        else:
            return None

    def convertToHMS(self, ra):
        """
        takes the given RA value, which should be in HMS format (but different types) and
        convert it to solve-field readable string in HH:MM:SS

        KEYWORD:   RA
        REFERENCE: NOAO
        HDU:       any
        DATATYPE:  real or string
        UNIT:      deg
        COMMENT:   R.A. of the observation
        DEFINITION: The value field gives the Right Ascension of the
        observation.  It may be expressed either as a floating point number in
        units of decimal degrees, or as a character string in 'HH:MM:SS.sss'
        format where the decimal point and number of fractional digits are
        optional. The coordinate reference frame is given by the RADECSYS
        keyword, and the coordinate epoch is given by the EQUINOX keyword.
        Example: 180.6904 or '12:02:45.7'.

        The value field shall contain a character string giving the
        Right Ascension of the observation in 'hh:mm:ss.sss' format.  The decimal
        point and fractional seconds are optional. The coordinate
        reference frame is given by the RADECSYS keyword, and the coordinate
        epoch is given by the EQUINOX keyword. Example: '13:29:24.00'

        :param ra: right ascension in degrees
        :return: converted value as string
        """

        if not isinstance(ra, float):
            ra = self.stringToDegree(ra)
            if ra is None:
                return None
            angle = Angle(hours=ra, preference='hours')
        else:
            angle = Angle(degrees=ra, preference='hours')

        t = Angle.signed_hms(angle)
        value = f'{t[1]:02.0f}:{t[2]:02.0f}:{t[3]:02.0f}'

        return value

    def convertToDMS(self, dec):
        """
        takes the given DEC value, which should be in DMS format (but different types) and
        convert it to solve-field readable string in sDD:MM:SS

        KEYWORD:   DEC
        REFERENCE: NOAO
        HDU:       any
        DATATYPE:  real or string
        UNIT:      deg
        COMMENT:   declination of the observed object
        DEFINITION: The value field gives the declination of the
        observation.  It may be expressed either as a floating point number in
        units of decimal degrees, or as a character string in 'dd:mm:ss.sss'
        format where the decimal point and number of fractional digits are
        optional. The coordinate reference frame is given by the RADECSYS
        keyword, and the coordinate epoch is given by the EQUINOX keyword.
        Example: -47.25944 or '-47:15:34.00'.

        :param dec: declination
        :return: converted value as string
        """

        if not isinstance(dec, float):
            dec = self.stringToDegree(dec)

        if dec is None:
            return None

        angle = Angle(degrees=dec, preference='degrees')

        t = Angle.signed_dms(angle)
        sign = '+' if angle.degrees > 0 else '-'
        value = f'{sign}{t[1]:02.0f}:{t[2]:02.0f}:{t[3]:02.0f}'

        return value

    def readFitsData(self, fitsHDU='', searchRatio=1.1, radius=2):
        """
        readFitsData reads the fits file with the image and tries to get some key
        fields out of the header for preparing the solver. necessary data are

            - 'SCALE': pixel scale in arcsec per pixel
            - 'OBJCTRA' : ra position of the object in HMS format
            - 'OBJCTDEC' : dec position of the object in DMS format

        we are taking OBJCTxy, because the precision is higher than in RA/DEC

        :param fitsHDU: fits file with image data
        :param searchRatio: how the scale is extended
        :param radius: how the radius is extended
        :return: options as string
        """

        fitsHeader = fitsHDU[0].header

        # todo: there might be the necessity to read more alternative header info
        # todo: the actual definition fit for EKOS

        scale = fitsHeader.get('SCALE', '')
        ra = fitsHeader.get('OBJCTRA', '')
        dec = fitsHeader.get('OBJCTDEC', '')

        self.logger.debug(f'RA: {ra}, DEC: {dec}, Scale: {scale}')

        if not ra or not dec or not scale:
            return ''

        scale = float(scale)
        ra = self.convertToHMS(ra)
        dec = self.convertToDMS(dec)

        scaleLow = scale / searchRatio
        scaleHigh = scale * searchRatio

        options = ['--scale-low',
                   f'{scaleLow}',
                   '--scale-high',
                   f'{scaleHigh}',
                   '--ra',
                   f'{ra}',
                   '--dec',
                   f'{dec}',
                   '--radius',
                   f'{radius}',
                   ]

        return options

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

    def getSolutionFromWCS(self, fitsHeader=None, wcsHeader=None):
        """
        getSolutionFromWCS reads the fits header containing the wcs data and returns the
        basic data needed

        :param fitsHeader:
        :param wcsHeader:
        :return: ra in hours, dec in degrees, angle in degrees, scale in arcsec/pixel
                 error in arcsec and flag if image is flipped
        """

        ra = wcsHeader.get('CRVAL1')
        dec = wcsHeader.get('CRVAL2')
        angle, scale, flipped = self.calcAngleScaleFromWCS(wcsHeader=wcsHeader)

        raMount = fitsHeader.get('RA')
        decMount = fitsHeader.get('DEC')

        error = np.sqrt(np.square(ra - raMount) + np.square(dec - decMount))

        # would like to have the error RMS in arcsec
        error *= 3600

        solve = Solve(raJ2000=ra,
                      decJ2000=dec,
                      angle=angle,
                      scale=scale,
                      error=error,
                      flipped=flipped)

        return solve

    def updateFitsWithWCSData(self, fitsHeader=None, wcsHeader=None, solve=None):
        """
        updateFitsWithWCSData reads the fits file containing the wcs data output from
        solve-field and embeds it to the given fits file with image. it removes all
        entries starting with some keywords given in selection. we starting with
        HISTORY

        :param fitsHeader: fits header from image file, where wcs should be embedded
        :param wcsHeader: fits header with wcs info to be embedded
        :param solve: parameter calculation for image attributes
        :return: true for test purpose
        """

        remove = ['COMMENT', 'HISTORY']

        fitsHeader.update({k: wcsHeader[k] for k in wcsHeader if k not in remove})

        fitsHeader['RA'] = solve.raJ2000
        fitsHeader['OBJCTRA'] = self.convertToHMS(solve.raJ2000)
        fitsHeader['DEC'] = solve.decJ2000
        fitsHeader['OBJCTDEC'] = self.convertToDMS(solve.decJ2000)
        fitsHeader['SCALE'] = solve.scale
        fitsHeader['PIXSCALE'] = solve.scale
        fitsHeader['ANGLE'] = solve.angle
        fitsHeader['FLIPPED'] = solve.flipped

        return True

    def runImage2xy(self, binPath='', xyPath='', fitsPath=''):
        """
        runImage2xy extracts a list of stars out of the

        :param binPath:   full path to image2xy executable
        :param xyPath:  full path to star file
        :param fitsPath:  full path to fits file
        :return: success
        """

        runnable = [binPath,
                    '-O',
                    '-o',
                    xyPath,
                    fitsPath]

        timeStart = time.time()
        try:
            result = subprocess.run(args=runnable,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    )
        except Exception as e:
            self.logger.error(f'error: {e} happened')
            return False
        else:
            delta = time.time() - timeStart
            self.logger.debug(f'image2xy took {delta}s return code: '
                              + str(result.returncode)
                              + ' stderr: '
                              + result.stderr.decode().replace('\n', ' ')
                              + ' stdout: '
                              + result.stdout.decode().replace('\n', ' ')
                              )

        success = (result.returncode == 0)
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
            result = subprocess.run(args=runnable,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    timeout=timeout,
                                    )
        except subprocess.TimeoutExpired:
            self.logger.debug('solve-field timeout')
            return False
        except Exception as e:
            self.logger.error(f'error: {e} happened')
            return False
        else:
            delta = time.time() - timeStart
            self.logger.debug(f'solve-field took {delta}s return code: '
                              + str(result.returncode)
                              + ' stderr: '
                              + result.stderr.decode().replace('\n', ' ')
                              + ' stdout: '
                              + result.stdout.decode().replace('\n', ' ')
                              )

        success = (result.returncode == 0)
        return success

    def solve(self, app='', fitsPath='', radius=2, timeout=30, updateFits=False):
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
        :param radius:  search radius around target coordinates
        :param timeout: time after the subprocess will be killed.
        :param updateFits:  if true update Fits image file with wcsHeader data
        :return: ra, dec, angle, scale, flipped
        """

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

        suc = self.runImage2xy(binPath=binPathImage2xy,
                               xyPath=xyPath,
                               fitsPath=fitsPath,
                               )
        if not suc:
            self.logger.error(f'image2xy error in [{fitsPath}]')
            return False

        with fits.open(fitsPath) as fitsHDU:
            solveOptions = self.readFitsData(fitsHDU=fitsHDU,
                                             radius=radius)

        # split between ekos and cloudmakers as cloudmakers use an older version of
        # solve-field, which need the option '--no-fits2fits', whereas the actual
        # version used in KStars throws an error using this option.
        if app == 'CloudMakers':
            solveOptions.append('--no-fits2fits')

        suc = self.runSolveField(binPath=binPathSolveField,
                                 configPath=configPath,
                                 xyPath=xyPath,
                                 options=solveOptions,
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
            fitsHeader = fitsHDU[0].header
            solve = self.getSolutionFromWCS(fitsHeader=fitsHeader,
                                            wcsHeader=wcsHeader)
            if updateFits:
                self.updateFitsWithWCSData(fitsHeader=fitsHeader,
                                           wcsHeader=wcsHeader,
                                           solve=solve,
                                           )

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

    def solveThreading(self, app='', fitsPath='', radius=2, timeout=30, updateFits=False):
        """
        solveThreading is the wrapper for doing the solve process in a threadpool
        environment of Qt. Otherwise the HMI would be stuck all the time during solving.
        it is done with an securing mutex to avoid starting solving twice. to solveClear
        is the partner of solve Threading

        :param app: which astrometry implementation to choose
        :param fitsPath: full path to the fits image file to be solved
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
                              radius=radius,
                              timeout=timeout,
                              updateFits=updateFits,
                              )
        worker.signals.finished.connect(self.solveClear)
        self.threadPool.start(worker)

        return True
