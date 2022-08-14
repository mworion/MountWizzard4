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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import platform

# external packages
import PyQt5
import numpy as np

# local imports
from base.driverDataClass import Signals
from base.transform import diffModulusAbs
from logic.dome.domeIndi import DomeIndi
from logic.dome.domeAlpaca import DomeAlpaca
if platform.system() == 'Windows':
    from logic.dome.domeAscom import DomeAscom


class Dome:

    __all__ = ['Dome']
    log = logging.getLogger(__name__)

    def __init__(self, app):
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data = {
            'Slewing': False,
        }
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = ''
        self.run = {
            'indi': DomeIndi(self.app, self.signals, self.data),
            'alpaca': DomeAlpaca(self.app, self.signals, self.data),
        }

        if platform.system() == 'Windows':
            self.run['ascom'] = DomeAscom(self.app, self.signals, self.data)

        for fw in self.run:
            self.defaultConfig['frameworks'].update({fw: self.run[fw].defaultConfig})

        self.useGeometry = False
        self.useDynamicFollowing = False
        self.isSlewing = False
        self.overshoot = None
        self.domeStarted = False
        self.lastFinalAz = None
        self.avoidFirstSlewOvershoot = True
        self.openingHysteresis = None
        self.clearanceZenith = None
        self.radius = None
        self.clearOpening = None
        self.counterStartSlewing = -1
        self.settlingTime = 0
        self.settlingWait = PyQt5.QtCore.QTimer()
        self.settlingWait.setSingleShot(True)
        self.settlingWait.timeout.connect(self.waitSettlingAndEmit)

    @property
    def updateRate(self):
        return self.run[self.framework].updateRate

    @updateRate.setter
    def updateRate(self, value):
        value = int(value)
        for fw in self.run:
            self.run[fw].updateRate = value

    @property
    def loadConfig(self):
        return self.run[self.framework].loadConfig

    @loadConfig.setter
    def loadConfig(self, value):
        value = bool(value)
        for fw in self.run:
            self.run[fw].loadConfig = value

    def startCommunication(self):
        """
        :return:
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].startCommunication()
        self.app.update1s.connect(self.checkSlewingDome)
        self.domeStarted = True
        return suc

    def stopCommunication(self):
        """
        :return:
        """
        if self.framework not in self.run.keys():
            return False

        self.signals.message.emit('')
        suc = self.run[self.framework].stopCommunication()
        if self.domeStarted:
            self.app.update1s.disconnect(self.checkSlewingDome)
            self.domeStarted = False
        return suc

    def waitSettlingAndEmit(self):
        """
        :return: true for test purpose
        """
        self.signals.slewFinished.emit()
        self.signals.message.emit('')
        return True

    def checkSlewingDome(self):
        """
        :return:
        """
        if self.isSlewing:
            self.signals.message.emit('slewing')
            self.counterStartSlewing = -1
            if not self.data.get('Slewing'):
                self.isSlewing = False
                self.signals.message.emit('wait settle')
                self.settlingWait.start(self.settlingTime * 1000)

        else:
            if self.data.get('Slewing'):
                self.log.debug('Slewing start by signal')
                self.isSlewing = True

            else:
                if self.counterStartSlewing == 0:
                    self.log.debug('Slewing start by counter')
                    self.isSlewing = True
                self.counterStartSlewing -= 1

        return True

    def checkTargetConditions(self):
        """
        :return:
        """
        if self.openingHysteresis is None:
            self.log.debug('No opening hysteresis')
            return False
        if self.clearanceZenith is None:
            self.log.debug('No clearance zenith')
            return False
        if self.overshoot is None:
            self.log.debug('No overshoot')
            return False
        if self.radius is None:
            self.log.debug('No radius')
            return False
        if self.clearOpening is None:
            self.log.debug('No clear opening')
            return False
        BC = self.clearOpening - 2 * self.openingHysteresis
        if BC < 0:
            self.log.warning('Resulting opening to small')
            return False
        return True

    def calcTargetRectanglePoints(self, azimuth):
        """
        :param azimuth:
        :return:
        """
        azRad = np.radians(-azimuth)
        sinAz = np.sin(azRad)
        cosAz = np.cos(azRad)
        rot = np.array([[cosAz, -sinAz], [sinAz, cosAz]])

        A = np.array([- self.clearanceZenith + self.openingHysteresis,
                     self.clearOpening / 2 - self.openingHysteresis])
        B = np.array([self.radius,
                     self.clearOpening / 2 - self.openingHysteresis])
        C = np.array([self.radius,
                     - self.clearOpening / 2 + self.openingHysteresis])

        A = np.dot(rot, A)
        B = np.dot(rot, B)
        C = np.dot(rot, C)

        return A, B, C

    @staticmethod
    def targetInDomeShutter(A, B, C, M):
        """
        Based on the maths presented on:
            https://stackoverflow.com/questions/2752725/
            finding-whether-a-point-lies-inside-a-rectangle-or-not
        :param A: Rectangle point A
        :param B: Rectangle point B in clockwise
        :param C: Rectangle point C in clockwise
        :param M: Point to be checked
        :return:
        """
        checkAB = 0 <= np.dot(B - A, M - A) <= np.dot(B - A, B - A)
        checkBC = 0 <= np.dot(C - B, M - A) <= np.dot(C - B, C - B)
        result = checkAB and checkBC
        return result

    def checkSlewNeeded(self, x, y):
        """
        :param x:
        :param y:
        :return:
        """
        if not self.checkTargetConditions():
            self.log.info('Target conditions not mez, slewing anyway')
            return True

        azimuth = self.data.get('ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION', 0)
        A, B, C = self.calcTargetRectanglePoints(azimuth)
        M = np.array([x, y])
        slewNeeded = not self.targetInDomeShutter(A, B, C, M)
        self.log.debug(f'Slew needed: [{slewNeeded}]')
        return slewNeeded

    def calcSlewTarget(self, altitude, azimuth, func):
        """
        :param altitude:
        :param azimuth:
        :param func:
        :return:
        """
        if self.useGeometry:
            alt, az, intersect, _, _ = func()

            if alt is None or az is None:
                self.log.info(f'Geometry error, alt:{altitude}, az:{azimuth}')
                alt = altitude
                az = azimuth
            else:
                alt = alt.degrees
                az = az.degrees
        else:
            alt = altitude
            az = azimuth
            intersect = [None, None, None]

        x = intersect[0]
        y = intersect[1]
        return alt, az, x, y

    def calcOvershoot(self, az):
        """
        :param az:
        :return:
        """
        if not self.overshoot:
            self.lastFinalAz = None
            return az

        if self.avoidFirstSlewOvershoot:
            self.avoidFirstSlewOvershoot = False
            self.lastFinalAz = None
            self.log.debug(f'First overshoot disabled: [{az}]')
            return az

        direction = self.app.mount.obsSite.AzDirection
        if direction is None:
            self.log.info(f'Overshoot discarded no direction: [{az}]')
            return az

        y = max(self.clearOpening / 2 - self.openingHysteresis, 0)
        x = self.radius
        maxOvershootAzimuth = abs(np.degrees(np.arctan2(y, x)))

        deltaAz = maxOvershootAzimuth * direction
        finalAz = (az + deltaAz + 360) % 360

        if self.lastFinalAz is None:
            self.lastFinalAz = finalAz
            self.log.debug(f'First overshoot value: [{finalAz}]')
            return finalAz

        delta = diffModulusAbs(self.lastFinalAz, finalAz, 360)
        if delta > maxOvershootAzimuth / 2:
            self.lastFinalAz = finalAz
            self.log.debug('New overshoot value')
        else:
            self.log.debug('Use old overshoot value')

        self.log.debug(f'Overshoot value: [{self.lastFinalAz}]')
        return self.lastFinalAz

    def slewDome(self, altitude=0, azimuth=0, follow=False):
        """
        :param altitude:
        :param azimuth:
        :param follow:
        :return: success
        """
        if not self.data:
            self.log.error('No data dict available')
            return False

        mount = self.app.mount
        if follow:
            func = mount.calcTransformationMatricesActual
        else:
            func = mount.calcTransformationMatricesTarget

        alt, az, x, y = self.calcSlewTarget(altitude, azimuth, func)

        if self.useDynamicFollowing and x is not None and y is not None:
            doSlew = self.checkSlewNeeded(x, y)
        else:
            doSlew = True

        if doSlew:
            self.counterStartSlewing = 3
            az = self.calcOvershoot(az)
            self.run[self.framework].slewToAltAz(azimuth=az, altitude=alt)
            self.signals.message.emit('slewing')
        else:
            self.signals.slewFinished.emit()
        delta = azimuth - az

        return delta

    def avoidFirstOvershoot(self):
        """
        :return:
        """
        self.avoidFirstSlewOvershoot = True
        return True

    def openShutter(self):
        """
        :return: success
        """
        if not self.data:
            self.log.error('No data dict available')
            return False

        suc = self.run[self.framework].openShutter()
        return suc

    def closeShutter(self):
        """
        :return: success
        """
        if not self.data:
            self.log.error('No data dict available')
            return False

        suc = self.run[self.framework].closeShutter()
        return suc

    def slewCW(self):
        """
        :return: success
        """
        if not self.data:
            self.log.error('No data dict available')
            return False

        suc = self.run[self.framework].slewCW()
        return suc

    def slewCCW(self):
        """
        :return: success
        """
        if not self.data:
            self.log.error('No data dict available')
            return False

        suc = self.run[self.framework].slewCCW()
        return suc

    def abortSlew(self):
        """
        :return: success
        """
        if not self.data:
            self.log.error('No data dict available')
            return False

        suc = self.run[self.framework].abortSlew()
        return suc
