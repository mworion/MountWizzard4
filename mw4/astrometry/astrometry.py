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
import glob
import platform
import time
from collections import namedtuple
# external packages
import PyQt5
from skyfield.api import Angle
from astropy.io import fits
from astropy.wcs import WCS
import astropy.wcs
import numpy as np
# local imports
from mw4.base import tpool
from mw4.base import transform
from mw4.definitions import Solution, Solve
from mw4.astrometry.astrometryNET import AstrometryNET
from mw4.astrometry.astrometryASTAP import AstrometryASTAP


class AstrometrySignals(PyQt5.QtCore.QObject):
    """
    The AstrometrySignals class offers a list of signals to be used and instantiated by the
    Worker class to get signals for error, finished and result to be transferred to the
    caller back
    """

    __all__ = ['AstrometrySignals']
    version = '1.0.0'

    done = PyQt5.QtCore.pyqtSignal(object)
    result = PyQt5.QtCore.pyqtSignal(object)
    message = PyQt5.QtCore.pyqtSignal(object)


class Astrometry(AstrometryNET, AstrometryASTAP):
    """
    the class Astrometry inherits all information and handling of astrometry.net handling

    Keyword definitions could be found under
        https://fits.gsfc.nasa.gov/fits_dictionary.html

        >>> astrometry = Astrometry(app=app,
        >>>                         tempDir=tempDir,
        >>>                         threadPool=threadpool
        >>>                         )

    """

    __all__ = ['Astrometry',
               'solveThreading',
               'checkAvailability',
               'abort',
               ]

    version = '0.100.0'
    logger = logging.getLogger(__name__)

    def __init__(self, app, tempDir='', threadPool=None):
        super().__init__()

        self.app = app
        self.tempDir = tempDir
        self.threadPool = threadPool
        self.signals = AstrometrySignals()
        self.available = {}
        self.mutexSolve = PyQt5.QtCore.QMutex()
        self.result = (False, [])
        self.process = None

        if platform.system() == 'Darwin':
            home = os.environ.get('HOME')
            self.solveApp = {
                'CloudMakers': {
                    'programPath': '/Applications/Astrometry.app/Contents/MacOS',
                    'indexPath': home + '/Library/Application Support/Astrometry',
                    'solve': self.solveNET,
                    'abort': self.abortNET,
                },
                'KStars': {
                    'programPath': '/Applications/KStars.app/Contents/MacOS/astrometry/bin',
                    'indexPath': home + '/Library/Application Support/Astrometry',
                    'solve': self.solveNET,
                    'abort': self.abortNET,
                },
                'ASTAP': {
                    'programPath': '/Applications/ASTAP.app/Contents/MacOS',
                    'indexPath': '/Applications/ASTAP.app/Contents/MacOS',
                    'solve': self.solveASTAP,
                    'abort': self.abortASTAP,
                }
            }

        elif platform.system() == 'Linux':
            self.solveApp = {
                'astrometry-glob': {
                    'programPath': '/usr/bin',
                    'indexPath': '/usr/share/astrometry',
                    'solve': self.solveNET,
                    'abort': self.abortNET,
                },
                'astrometry-local': {
                    'programPath': '/usr/local/astrometry/bin',
                    'indexPath': '/usr/share/astrometry',
                    'solve': self.solveNET,
                    'abort': self.abortNET,
                },
            }

        elif platform.system() == 'windows':
            self.solveApp = {
                '': {
                    'programPath': '',
                    'indexPath': '',
                },
            }

        else:
            self.solveApp = {
                '': {
                    'programPath': '',
                    'indexPath': '',
                },
            }

        self.checkAvailability()

    def checkAvailability(self):
        """
        checkAvailability searches for the existence of the core runtime modules from
        all applications. to this family belong:
            astrometry.net namely image2xy and solve-field
            ASTP files

        :return: True if local solve and components is available
        """

        self.available = {}
        for solver in self.solveApp:
            suc = True

            if solver != 'ASTAP':
                program = self.solveApp[solver]['programPath'] + '/solve-field'
                index = '/*.fits'
            else:
                program = self.solveApp[solver]['programPath'] + '/astap'
                index = '/*.290'

            # checking binaries
            if not os.path.isfile(program):
                self.logger.info(f'{program} not found')
                suc = False

            # checking indexes
            if not glob.glob(self.solveApp[solver]['indexPath'] + index):
                self.logger.info('no index files found')
                suc = False

            if suc:
                self.available[solver] = solver
                self.logger.info(f'binary and index files available for {solver}')

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
            # todo: the actual definition is OK for EKOS

            scaleHint = float(fitsHeader.get('SCALE', 0))
            ra = fitsHeader.get('RA', 0)
            dec = fitsHeader.get('DEC', 0)
            raHint = transform.convertToAngle(ra, isHours=True)
            decHint = transform.convertToAngle(dec, isHours=False)

        self.logger.info(f'RA: {raHint} ({ra}), DEC: {decHint} ({dec}), Scale: {scaleHint}')

        return raHint, decHint, scaleHint, ra, dec

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

        for key in wcsHeader:
            print(key, wcsHeader[key])
            fitsHeader.update({key: wcsHeader[key]})

        fitsHeader['RA'] = solve.raJ2000._degrees
        fitsHeader['OBJCTRA'] = transform.convertToHMS(solve.raJ2000)
        fitsHeader['DEC'] = solve.decJ2000.degrees
        fitsHeader['OBJCTDEC'] = transform.convertToDMS(solve.decJ2000)
        fitsHeader['SCALE'] = solve.scale
        fitsHeader['PIXSCALE'] = solve.scale
        fitsHeader['ANGLE'] = solve.angle
        fitsHeader['FLIPPED'] = solve.flipped

        # remove keys if 'SIP' is not selected i CTYPE1 and CTYPE2
        if 'SIP' in fitsHeader['CTYPE1'] and 'SIP' in fitsHeader['CTYPE2']:
            return solve, fitsHeader

        for key in fitsHeader:
            if key.startswith('A_'):
                del fitsHeader[key]
            elif key.startswith('B_'):
                del fitsHeader[key]
            elif key.startswith('AP_'):
                del fitsHeader[key]
            elif key.startswith('BP_'):
                del fitsHeader[key]

        return solve, fitsHeader

    def solveClear(self):
        """
        the cyclic or long lasting tasks for solving the image should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour.

        :return: true for test purpose
        """

        self.mutexSolve.unlock()
        self.signals.done.emit(self.result)
        self.signals.message.emit('')

        return True

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

        if app not in self.solveApp:
            return False
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
        worker = tpool.Worker(self.solveApp[app]['solve'],
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

    def abort(self, app=''):
        """

        :param app: which astrometry implementation to choose
        :return:
        """

        if app not in self.solveApp:
            return False

        suc = self.solveApp[app]['abort']()
        return suc
