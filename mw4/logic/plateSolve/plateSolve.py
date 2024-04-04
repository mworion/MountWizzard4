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
import os

# external packages
import PyQt6
from astropy.io import fits
import numpy as np

# local imports
from base.fitsHeader import getCoordinates, getScale, calcAngleScaleFromWCS
from base.fitsHeader import getCoordinatesWCS
from base import tpool
from logic.plateSolve.astrometry import Astrometry
from logic.plateSolve.astap import ASTAP
from logic.plateSolve.watney import Watney


class PlateSolveSignals(PyQt6.QtCore.QObject):
    """
    """

    __all__ = ['PlateSolveSignals']

    done = PyQt6.QtCore.pyqtSignal(object)
    result = PyQt6.QtCore.pyqtSignal(object)
    message = PyQt6.QtCore.pyqtSignal(object)

    serverConnected = PyQt6.QtCore.pyqtSignal()
    serverDisconnected = PyQt6.QtCore.pyqtSignal(object)
    deviceConnected = PyQt6.QtCore.pyqtSignal(object)
    deviceDisconnected = PyQt6.QtCore.pyqtSignal(object)


class PlateSolve:
    """
    the class PlateSolve inherits all information and handling of astrometry.net
    handling

    Keyword definitions could be found under
        https://fits.gsfc.nasa.gov/fits_dictionary.html

        >>> plateSolve = PlateSolveSignals(app=None)
    """

    __all__ = ['PlateSolve',
               ]

    log = logging.getLogger(__name__)

    def __init__(self, app):
        self.app = app
        self.msg = app.msg
        self.tempDir = app.mwGlob['tempDir']
        self.workDir = app.mwGlob['workDir']
        self.threadPool = app.threadPool
        self.signals = PlateSolveSignals()

        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = ''
        self.run = {
            'astrometry': Astrometry(self),
            'astap': ASTAP(self),
            'watney': Watney(self),
        }
        for fw in self.run:
            self.defaultConfig['frameworks'].update(self.run[fw].defaultConfig)

        self.mutexSolve = PyQt6.QtCore.QMutex()
        self.raHint = None
        self.decHint = None
        self.scaleHint = None
        self.fovHint = None

    def readFitsData(self, fitsPath):
        """
        readFitsData reads the fits file with the image and tries to get some
        key fields out of the header for preparing the solver. if there is the
        need for understanding more FITS header data, it should be integrated
        in this method.

        :param fitsPath: fits file with image data
        :return: raHint, decHint, scaleHint
        """
        with fits.open(fitsPath) as fitsHDU:
            fitsHeader = fitsHDU[0].header

            raHint, decHint = getCoordinates(header=fitsHeader)
            scaleHint = getScale(header=fitsHeader)

        self.log.debug(f'Header RA: {raHint}, DEC: {decHint}, scale: {scaleHint}')

        return raHint, decHint, scaleHint

    def getSolutionFromWCS(self, fitsHeader=None, wcsHeader=None, updateFits=False):
        """
        getSolutionFromWCS reads the wcs fits file and uses the data in the
        header containing the wcs data and returns the basic data needed.
        in addition it embeds it to the given fits file with image. it removes
        all entries starting with some keywords given in selection. we're starting
        with HISTORY

        CRVAL1 and CRVAL2 give the center coordinate as right ascension and
        declination or longitude and latitude in decimal degrees.

        the difference is calculated as real coordinate (= plate solved
        coordinate) and mount reported coordinate (= including the errors) and
        set positive in this case.

        we have to take into account if the mount is on the other pierside, the
        image taken will be upside down and the angle will reference a 180
        degrees turned image. this will lead to the negative error value (sign
        will change)

        :param fitsHeader:
        :param wcsHeader:
        :param updateFits:
        :return: ra in hours, dec in degrees, angle in degrees,
                 scale in arcsec/pixel
                 error in arcsec and flag if image is flipped
        """
        self.log.trace(f'wcs header: [{wcsHeader}]')
        self.log.debug(f'wcs RA: [{wcsHeader["CRVAL1"]}] '
                       f'DEC: [{wcsHeader["CRVAL2"]}]')
        angle, scale, mirrored = calcAngleScaleFromWCS(wcsHeader=wcsHeader)
        raMount, decMount = getCoordinates(header=fitsHeader)
        raJ2000, decJ2000 = getCoordinatesWCS(header=wcsHeader)

        deltaRA = (raJ2000._degrees - raMount._degrees) * 3600
        deltaDEC = (decJ2000.degrees - decMount.degrees) * 3600
        error = np.sqrt(np.square(deltaRA) + np.square(deltaDEC))

        solve = {
            'raJ2000S': raJ2000,
            'decJ2000S': decJ2000,
            'errorRA_S': deltaRA,
            'errorDEC_S': deltaDEC,
            'angleS': angle,
            'scaleS': scale,
            'errorRMS_S': error,
            'mirroredS': mirrored,
        }

        if not updateFits:
            return solve, fitsHeader

        if 'RA' not in fitsHeader:
            fitsHeader.append(('RA', wcsHeader['CRVAL1'], 'MW4 - solved'))
        if 'DEC' not in fitsHeader:
            fitsHeader.append(('DEC', wcsHeader['CRVAL2'], 'MW4 - solved'))

        fitsHeader.append(('SCALE', solve['scaleS'], 'MW4 - solved'))
        fitsHeader.append(('PIXSCALE', solve['scaleS'], 'MW4 - solved'))
        fitsHeader.append(('ANGLE', solve['angleS'], 'MW4 - solved'))
        fitsHeader.append(('MIRRORED', solve['mirroredS'], 'MW4 - solved'))
        fitsHeader.append(('COMMENT', 'There was a cleanup of parameters'))

        fitsHeader.extend(wcsHeader, unique=True, update=True)

        # remove polynomial coefficients keys if '-SIP' is not selected in
        # CTYPE1 and CTYPE2 this might occur, if you solve a fits file a second
        # time with another solver

        if 'CTYPE1' not in fitsHeader or 'CTYPE2' not in fitsHeader:
            return solve, fitsHeader
        if '-SIP' in fitsHeader['CTYPE1'] and '-SIP' in fitsHeader['CTYPE2']:
            return solve, fitsHeader

        for key in list(fitsHeader.keys()):
            if key.startswith('A_'):
                del fitsHeader[key]
            elif key.startswith('B_'):
                del fitsHeader[key]
            elif key.startswith('AP_'):
                del fitsHeader[key]
            elif key.startswith('BP_'):
                del fitsHeader[key]

        return solve, fitsHeader

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

    def solveClear(self):
        """
        the cyclic or long-lasting tasks for solving the image should not run
        twice for the same data at the same time. so there is a mutex to prevent
        his behaviour.

        :return: true for test purpose
        """
        if self.framework not in self.run:
            return False

        solver = self.run[self.framework]
        self.signals.done.emit(solver.result)
        self.signals.message.emit('')
        self.mutexSolve.unlock()
        self.log.debug('Finished clear thread for solving')
        return True

    def solveThreading(self, fitsPath='', raHint=None, decHint=None,
                       scaleHint=None, fovHint=None, updateFits=False):
        """
        solveThreading is the wrapper for doing the solve process in a
        threadpool environment of Qt. Otherwise, the HMI would be stuck all the
        time during solving. it is done with a securing mutex to avoid starting
        solving twice. to solveClear is the partner of solve Threading

        :param fitsPath: full path to the fits image file to be solved
        :param raHint:  ra dest to look for solve in J2000
        :param decHint:  dec dest to look for solve in J2000
        :param scaleHint:  scale to look for solve in J2000
        :param fovHint:  degrees FOV to look for solve in J2000
        :param updateFits: flag, if the results should be written to the
                           original file
        :return: success
        """
        solver = self.run[self.framework]

        if not self.mutexSolve.tryLock():
            self.log.warning('Overrun in solve threading')
            self.signals.done.emit({})
            return False

        if not os.path.isfile(fitsPath):
            self.log.warning(f'Image file not found: {fitsPath}')
            self.signals.done.emit({})
            return False

        self.log.debug(f'Start thread for solving: {fitsPath}')
        self.signals.message.emit('solving')
        worker = tpool.Worker(solver.solve,
                              fitsPath=fitsPath,
                              raHint=raHint,
                              decHint=decHint,
                              scaleHint=scaleHint,
                              fovHint=fovHint,
                              updateFits=updateFits,
                              )
        worker.signals.finished.connect(self.solveClear)
        self.threadPool.start(worker)
        return True

    def abort(self):
        """
        :return:
        """
        solver = self.run[self.framework]
        suc = solver.abort()
        return suc

    def checkAvailability(self):
        """
        :return: list of available solutions
        """
        if self.framework not in self.run:
            return False, False

        val = self.run[self.framework].checkAvailability()
        return val

    def startCommunication(self):
        """
        :return: True for test purpose
        """
        if self.framework not in self.run:
            self.log.warning(f'Framework for solver not found: {self.framework}')
            return False

        sucApp, sucIndex = self.checkAvailability()
        if not sucApp or not sucIndex:
            self.log.warning(f'App or Index for solver not found: {self.framework}')
            return False

        name = self.run[self.framework].deviceName
        self.signals.deviceConnected.emit(name)
        self.signals.serverConnected.emit()
        self.msg.emit(0, 'System', 'Plate Solver found', f'{name}')
        self.log.debug(f'Framework: [{self.framework}], {sucApp}, {sucIndex}')
        return True

    def stopCommunication(self):
        """
        :return: true for test purpose
        """
        name = self.run[self.framework].deviceName
        self.signals.serverDisconnected.emit({name: 0})
        self.signals.deviceDisconnected.emit(name)
        self.msg.emit(0, 'System', 'Plate Solver remove', f'{name}')
        return True
