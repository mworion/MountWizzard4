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

# external packages
from skyfield.api import Angle

# local imports
from base.transform import J2000ToJNow


class SlewInterface:
    """
    """

    __all__ = ['SlewInterface']
    log = logging.getLogger(__name__)

    def slewSelectedTargetWithDome(self, slewType='normal'):
        """
        :param slewType:
        :return: success
        """
        azimuthT = self.app.mount.obsSite.AzTarget
        altitudeT = self.app.mount.obsSite.AltTarget

        if azimuthT is None or altitudeT is None:
            return False

        azimuthT = azimuthT.degrees
        altitudeT = altitudeT.degrees

        if self.app.deviceStat['dome']:
            delta = self.app.dome.slewDome(altitude=altitudeT,
                                           azimuth=azimuthT)
            geoStat = 'Geometry corrected' if delta else 'Equal mount'
            text = f'{geoStat}'
            text += ', az: {azimuthT:3.1f} delta: {delta:3.1f}'
            self.app.msg.emit(0, 'Tools', 'Slewing dome', text)

        suc = self.app.mount.obsSite.startSlewing(slewType=slewType)
        if suc:
            self.msg.emit(0, 'Tools', 'Slewing mount', 'Slew to target')
        else:
            self.msg.emit(2, 'Tools', 'Slewing error', 'Cannot slew to target')
        return suc

    def slewTargetAltAz(self, alt, az, slewType='normal'):
        """
        :param alt:
        :param az:
        :param slewType:
        :return:
        """
        suc = self.app.mount.obsSite.setTargetAltAz(alt_degrees=alt,
                                                    az_degrees=az)
        if not suc:
            t = f'Cannot slew to Az:[{az:3.1f}], Alt:[{alt:3.1f}]'
            self.msg.emit(2, 'Tools', 'Slewing error', t)
            return False

        suc = self.slewSelectedTargetWithDome(slewType=slewType)
        return suc

    def slewTargetRaDec(self, ra, dec, slewType='normal', epoch='J2000'):
        """
        :param ra:
        :param dec:
        :param slewType:
        :param epoch:
        :return:
        """
        timeJD = self.app.mount.obsSite.timeJD
        if timeJD is None:
            return False

        if epoch == 'J2000':
            raJNow, decJNow = J2000ToJNow(ra, dec, timeJD)
        elif epoch != 'J2000' and isinstance(ra, Angle):
            raJNow = ra
            decJNow = dec
        else:
            raJNow = Angle(hours=ra)
            decJNow = Angle(degrees=dec)

        suc = self.app.mount.obsSite.setTargetRaDec(ra=raJNow,
                                                    dec=decJNow)
        if not suc:
            t = f'Cannot slew to RA:[{ra.hours:3.1f}], DEC:[{dec.degrees:3.1f}]'
            self.msg.emit(2, 'Tools', 'Slewing error', t)
            return False

        suc = self.slewSelectedTargetWithDome(slewType=slewType)
        return suc
