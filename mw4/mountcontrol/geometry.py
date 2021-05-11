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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
import numpy as np
from skyfield.api import Angle

# local imports
from mountcontrol.convert import valueToFloat


class Geometry(object):
    """
    The class Geometry contains all necessary geometric calculations and
    parameters for mount orientation, dome slit correction or 3D animation of
    telescope.

        >>> geometry = Geometry()

    transformations are defined as homogeneous matrices to be able to calculate
    translations and rotation in the same manner. therefore the system has 4
    dimensions

    for the transformation between homogeneous vectors (vh) and kartesian vectors
    (vk):
    vk = vh[0:2]/vh[3]
    vh = [vk, 1]

    """

    __all__ = ['Geometry',
               ]

    log = logging.getLogger(__name__)

    geometryData = {
        '10micron GM1000HPS': {
            'offBaseAltAxisX': -0.005,
            'offBaseAltAxisZ': 0.095,
            'offAltAxisGemX': 0.156,
            'offAltAxisGemZ': 0.12,
            'offGemPlate': 0.15,
        },
        '10micron GM2000HPS': {
            'offBaseAltAxisX': -0.102,
            'offBaseAltAxisZ': 0.132,
            'offAltAxisGemX': 0.304,
            'offAltAxisGemZ': 0.0,
            'offGemPlate': 0.175,
        },
        '10micron GM3000HPS': {
            'offBaseAltAxisX': -0.122,
            'offBaseAltAxisZ': 0.167,
            'offAltAxisGemX': 0.363,
            'offAltAxisGemZ': 0.0,
            'offGemPlate': 0.233,
        },
        '10micron GM4000HPS': {
            'offBaseAltAxisX': -0.128,
            'offBaseAltAxisZ': 0.19,
            'offAltAxisGemX': 0.413,
            'offAltAxisGemZ': 0.0,
            'offGemPlate': 0.300,
        },
    }

    def __init__(self, parent=None):

        self.parent = parent
        self.offBaseAltAxisX = 0
        self.offBaseAltAxisZ = 0
        self.offAltAxisGemX = 0
        self.offAltAxisGemZ = 0
        self.offGemPlate = 0
        self.altAdj = 0
        self.azAdj = 0

        self._offNorth = 0
        self._offEast = 0
        self._offVert = 0
        self._offVertGEM = 0
        self._domeRadius = 1
        self._offGEM = 0
        self._offLAT = 0
        self._offPlateOTA = 0

        self.transMatrix = None
        self.transVector = None

    @property
    def domeRadius(self):
        return self._domeRadius

    @domeRadius.setter
    def domeRadius(self, value):
        self._domeRadius = valueToFloat(value)

    @property
    def offNorth(self):
        return self._offNorth

    @offNorth.setter
    def offNorth(self, value):
        self._offNorth = valueToFloat(value)

    @property
    def offEast(self):
        return self._offEast

    @offEast.setter
    def offEast(self, value):
        self._offEast = valueToFloat(value)

    @property
    def offVert(self):
        return self._offVert

    @offVert.setter
    def offVert(self, value):
        self._offVert = valueToFloat(value)
        if self.parent.obsSite.location is None:
            self.log.debug('offVert called without lat')
            return

        lat = self.parent.obsSite.location.latitude.radians
        val = valueToFloat(value) + self.offBaseAltAxisZ
        val += np.sin(abs(lat)) * self.offAltAxisGemX
        self._offVertGEM = val

    @property
    def offVertGEM(self):
        return self._offVertGEM

    @offVertGEM.setter
    def offVertGEM(self, value):
        self._offVertGEM = valueToFloat(value)
        if self.parent.obsSite.location is None:
            self.log.debug('offVertGEM called without lat')
            return

        lat = self.parent.obsSite.location.latitude.radians
        val = valueToFloat(value) - self.offBaseAltAxisZ
        val -= np.sin(abs(lat)) * self.offAltAxisGemX
        self._offVert = val

    @property
    def offGEM(self):
        return self._offGEM

    @offGEM.setter
    def offGEM(self, value):
        self._offGEM = valueToFloat(value)
        self._offPlateOTA = self._offGEM - self.offGemPlate

    @property
    def offLAT(self):
        return self._offLAT

    @offLAT.setter
    def offLAT(self, value):
        self._offLAT = valueToFloat(value)

    @property
    def offPlateOTA(self):
        return self._offPlateOTA

    @offPlateOTA.setter
    def offPlateOTA(self, value):
        self._offPlateOTA = valueToFloat(value)
        self._offGEM = self._offPlateOTA + self.offGemPlate

    def initializeGeometry(self, mountType):
        """
        initializeGeometry takes the mount type as string and searches for the
        right parameters in his database. If found it populates the parameters
        for geometry calculation and returns True otherwise false

        :param mountType: string from mount
        :return: success
        """

        if mountType not in self.geometryData:
            self.log.error(f'[{mountType}] not in database')
            return False

        else:
            self.log.debug(f'using [{mountType}] geometry')

        self.offBaseAltAxisX = self.geometryData[mountType]['offBaseAltAxisX']
        self.offBaseAltAxisZ = self.geometryData[mountType]['offBaseAltAxisZ']
        self.offAltAxisGemX = self.geometryData[mountType]['offAltAxisGemX']
        self.offAltAxisGemZ = self.geometryData[mountType]['offAltAxisGemZ']
        self.offGemPlate = self.geometryData[mountType]['offGemPlate']

        return True

    @staticmethod
    def transformRotX(rotX, degrees=False):
        """
        :param rotX: rotation angle
        :param degrees:
        :return: homogeneous transformation matrix
        """
        if isinstance(rotX, Angle):
            rot = rotX.radians
        else:
            if degrees:
                rot = np.radians(rotX)
            else:
                rot = rotX

        tCos = np.cos(rot)
        tSin = np.sin(rot)

        T = np.array([[1, 0, 0, 0],
                      [0, tCos, -tSin, 0],
                      [0, tSin, tCos, 0],
                      [0, 0, 0, 1]])
        return T

    @staticmethod
    def transformRotY(rotY, degrees=False):
        """
        :param rotY: rotation angle
        :param degrees:
        :return: homogeneous transformation matrix
        """
        if isinstance(rotY, Angle):
            rot = rotY.radians
        else:
            if degrees:
                rot = np.radians(rotY)
            else:
                rot = rotY

        tCos = np.cos(rot)
        tSin = np.sin(rot)

        T = np.array([[tCos, 0, tSin, 0],
                      [0, 1, 0, 0],
                      [-tSin, 0, tCos, 0],
                      [0, 0, 0, 1]])
        return T

    @staticmethod
    def transformRotZ(rotZ, degrees=False):
        """
        :param rotZ: rotation angle
        :param degrees:
        :return: homogeneous transformation matrix
        """
        if isinstance(rotZ, Angle):
            rot = rotZ.radians
        else:
            if degrees:
                rot = np.radians(rotZ)
            else:
                rot = rotZ

        tCos = np.cos(rot)
        tSin = np.sin(rot)

        T = np.array([[tCos, -tSin, 0, 0],
                      [tSin, tCos, 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])
        return T

    @staticmethod
    def transformTranslate(vector):
        """
        :param vector: translation
        :return: homogeneous transformation matrix
        """
        T = np.array([[1, 0, 0, vector[0]],
                      [0, 1, 0, vector[1]],
                      [0, 0, 1, vector[2]],
                      [0, 0, 0, 1]])
        return T

    def calcTransformationMatrices(self, ha=None, dec=None, lat=None, pierside='W'):
        """
        :param ha: hour angle in radians
        :param dec: declination in radians
        :param lat: latitude of observation site in radians
        :param pierside: 'W' or 'E' for setting the right HA
        :return: altDome, azDome: the real pointing angles for OTA in dome
        """
        if not isinstance(ha, Angle):
            return None, None, None, None, None
        if not isinstance(dec, Angle):
            return None, None, None, None, None
        if not isinstance(lat, Angle):
            return None, None, None, None, None

        text = f'HA:{ha.hours}, DEC:{dec.degrees}, LAT:{lat.degrees}, '
        text += f'pierside:{pierside} ,'
        text += f'offGEM:{self.offGEM}, offPlateOTA:{self.offPlateOTA}, '
        text += f'offNorth:{self.offNorth}, offEast:{self.offEast}, '
        text += f'offVert:{self.offVert}, offLAT:{self.offLAT}, '
        text += f'domeRadius:{self.domeRadius}'
        self.log.trace(text)

        ha = ha.radians
        dec = dec.radians
        lat = lat.radians

        # the equator of the dome and it's middle point of the hemisphere is
        # zero point for coordinate system.
        P0 = np.array([0, 0, 0, 1])

        # next adjustment if the position of the base of mount in relation to
        # the offset in north is x and the offset in east is -y. in vertical
        # direction up is positive, which means the mount is above the middle
        # point of dome
        vec0 = [self.offNorth,
                -self.offEast,
                self.offVert]
        T0 = self.transformTranslate(vec0)
        P1 = np.dot(T0, P0)

        # the rotation around z axis (polar direction) to adjust the orientation
        # of the mount to true north, if the fixed pier does not make it.
        # turning counterclockwise is positive
        T1 = np.dot(T0, self.transformRotZ(self.azAdj))
        P2 = np.dot(T1, P0)

        # next we have the translation between the base plate and the rotation
        # axis for the altitude adjustment. the axis is normally above the plate (
        # positive z) and sometime shifted. shift north mean positive x
        vec2 = [self.offBaseAltAxisX,
                0,
                self.offBaseAltAxisZ]
        T2 = np.dot(T1, self.transformTranslate(vec2))
        P3 = np.dot(T2, P0)

        # next step is the rotation around y axis for compensation of latitude.
        # the adjustment angle compensates the latitude. for lat = 0 we have 0
        # degree correction an below north pole there is 90 deg correction needed.
        # so phi = -lat because it's a turn counterclockwise around Y, all angles
        # are in radians
        self.altAdj = -abs(lat)
        T3 = np.dot(T2, self.transformRotY(self.altAdj))
        P4 = np.dot(T3, P0)

        # next is the translation fom the rotation axis of the lat compensation of
        # the mount to the GEM point of the mount. GEM means the crossing of the
        # ra and dec axis of the german equatorial mount basically there should be
        # a translation in x/z plane up and forward (to north)
        vec4 = [self.offAltAxisGemX,
                0,
                self.offAltAxisGemZ]
        T4 = np.dot(T3, self.transformTranslate(vec4))
        P5 = np.dot(T4, P0)

        # next is the rotation around the ra axis of the mount, this is rotation
        # around x this should be (as we don't track) measured in HA, where HA = 6
        # / 18 h is North depending of the pierside the direction is clockwise,
        # turning to west over time
        #
        # using the definition of ASCOM about the pierEAST state
        # Normal state:
        # HA_sky = HA_mech
        # Beyond the pole
        # HA_sky = HA_mech + 12h, expressed in range ± 12h

        if pierside == 'E':
            value = - ha + np.radians(6 / 24 * 360)

        else:
            value = - ha + np.radians(18 / 24 * 360)

        T5 = np.dot(T4, self.transformRotX(value))
        P6 = np.dot(T5, P0)

        # the rotation around dec axis of the mount is next step. this rotation is
        # around z axis. dec = 0 means rectangular directing scope. direction
        # changes due to position of the mount and pierside
        #
        # using the definition of ASCOM about the pierEAST state
        # Normal state:
        # Dec_sky = Dec_mech
        # Beyond the pole
        # Dec_sky = 180d - Dec_mech, expressed in range ± 90d

        value = dec - np.radians(90)
        if pierside == 'E':
            value = -value

        T6 = np.dot(T5, self.transformRotZ(value))
        P7 = np.dot(T6, P0)

        # the translation from GEM to the center of the ota, this should be a
        # translation in z. it consists of two parts: the user OTA measures and the
        # distance from GEM to base plate, which is depending on mount type and is
        # fixed and secondly the distance between the mount plate and the OTA line
        # of sight axis
        vec6 = [0,
                0,
                self.offPlateOTA + self.offGemPlate]
        T7 = np.dot(T6, self.transformTranslate(vec6))
        P8 = np.dot(T7, P0)

        # the translation from center of the ota, to the side if a second ota is
        # installed but not centered should be a translation in y. if the ota is
        # de-centered looking in the direction of the ota (out of the hemisphere)
        # to the right it's a negative y otherwise a positive one

        vec7 = [0,
                - self.offLAT,
                0]
        T8 = np.dot(T7, self.transformTranslate(vec7))
        P9 = np.dot(T8, P0)

        # calculating the direction of OTA for dome geometry. pointing direction is
        # in x axis, length is standard 1. P10 would be the head of the vector,
        # P9 is the base of the vector. subtracting gives the resulting direction
        # of the vector which is in PD
        vec9 = [1, 0, 0]
        T9 = np.dot(T8, self.transformTranslate(vec9))
        P10 = np.dot(T9, P0)
        PD = (P10 - P9)[:-1]

        # calculating the crossing point between view of sight of the OTA and the
        # dome hemisphere using the traditional p-q formula
        # if you have g: v = v0 + t * tDir and hem: x^2 + y^2 + z^2 = r^2
        # with v0 = PB and tDir = PD you get t1 and t2 from p-q formula as
        # t1 = -p/2 + sqr (p^2/4 - q), t2 = -p/2 - sqr (p^2/4 - q)
        # for the right point whe have to choose the one, which crosses the
        # hemisphere above the OTA point as we normally are looking upward.
        # and we have to use scalar product on a cartesian system
        PB = P9[:-1]

        p = 2 * np.dot(PD, PB)
        q = (np.dot(PB, PB) - self.domeRadius**2)

        self.log.trace(f'Geometry calc p:[{p}], q:[{q}]')

        # there should be always a reasonable solution
        if (p * p / 4 - q) < 0:
            self.log.error('Geometry solution impossible')
            return None, None, None, None, None

        t1 = - p / 2 + np.sqrt(p * p / 4 - q)
        # t2 = - p / 2 - np.sqrt(p * p / 4 - q)

        # we choose the positive solution as we look in the positive direction and
        # can omit the view to the back

        intersect = PB + np.dot(t1, PD)

        # simplify the names and calculate the geometry angles based on the
        # coordinates of the intersection between line of sight and dome
        # hemisphere. as we have y to the left because of the right turning
        # homogeneous coordinate system, we have to negate the angle of azimuth.
        # we use arctan2 for getting the full quadrants and shifting
        # the angle in an value range from 0 .. 2pi

        x = intersect[0]
        y = intersect[1]
        z = intersect[2]

        value = np.mod(- np.arctan2(y, x), 2 * np.pi)
        azDome = Angle(radians=value)
        base = np.sqrt(x * x + y * y)

        altDome = Angle(radians=np.arctan2(z, base))

        self.transMatrix = [T0, T1, T2, T3, T4, T5, T6, T7, T8, T9]
        self.transVector = [P0[:-1], P1[:-1], P2[:-1], P3[:-1], P4[:-1],
                            P5[:-1], P6[:-1], P7[:-1], P8[:-1], P9[:-1],
                            P10[:-1]]

        self.log.trace(f'az:{azDome}, alt:{altDome}')

        return altDome, azDome, intersect, PB, PD
