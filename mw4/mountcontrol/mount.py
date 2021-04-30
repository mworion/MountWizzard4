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

# local imports
from mountcontrol.firmware import Firmware
from mountcontrol.dome import Dome
from mountcontrol.setting import Setting
from mountcontrol.obsSite import ObsSite
from mountcontrol.model import Model
from mountcontrol.satellite import Satellite
from mountcontrol.geometry import Geometry


__all__ = ['Mount',
           ]


class Mount(object):
    """
    The Mount class is the main interface for interacting with the mount
    computer. The user could:
        setup / change the interface to the mount
        start / stop cyclic tasks to poll data from mount
        send and get data from mount
        has signals for interfacing to external GUI's for data updates

        >>> Mount(
        >>>       host=host,
        >>>       MAC=MAC,
        >>>       pathToData=pathToData,
        >>>       verbose=verbose,
        >>>       )

    """

    __all__ = ['Mount',
               ]

    log = logging.getLogger(__name__)
    DEFAULT_PORT = 3492

    def __init__(self,
                 host=None,
                 MAC=None,
                 pathToData=None,
                 verbose=None,
                 ):

        self._host = None
        self.MAC = MAC
        self.pathToData = pathToData
        self.verbose = verbose

        self.firmware = Firmware(self.host)
        self.setting = Setting(self.host)
        self.obsSite = ObsSite(self.host,
                               pathToData=self.pathToData,
                               verbose=self.verbose,
                               )
        self.satellite = Satellite(parent=self, host=self.host)
        self.geometry = Geometry(parent=self)
        self.dome = Dome(self.host)
        self.model = Model(parent=self, host=self.host)
        self.host = host

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        value = self.checkFormatHost(value)
        self._host = value
        self.firmware.host = value
        self.dome.host = value
        self.setting.host = value
        self.model.host = value
        self.obsSite.host = value
        self.satellite.host = value

    @property
    def MAC(self):
        return self._MAC

    @MAC.setter
    def MAC(self, value):
        value = self.checkFormatMAC(value)
        self._MAC = value

    def checkFormatHost(self, value):
        """
        checkFormatHost ensures that the host ip and port is in correct format
        to enable socket connection later on. if no port is given, the default
        port for the mount will be added automatically

        :param      value: host value
        :return:    host value as tuple including port
        """
        if not value:
            self.log.info('Wrong host value: {0}'.format(value))
            return None
        if not isinstance(value, (tuple, str)):
            self.log.info('Wrong host value: {0}'.format(value))
            return None
        if isinstance(value, str):
            value = (value, self.DEFAULT_PORT)

        return value

    def checkFormatMAC(self, value):
        """
        checkFormatMAC makes some checks to ensure that the format of the
        string is ok for WOL package.

        :param      value: string with mac address
        :return:    checked string in upper cases
        """
        if not value:
            self.log.info('wrong MAC value: {0}'.format(value))
            return None

        if not isinstance(value, str):
            self.log.info('wrong MAC value: {0}'.format(value))
            return None

        value = value.upper()
        value = value.replace('.', ':')
        value = value.split(':')
        if len(value) != 6:
            self.log.info('wrong MAC value: {0}'.format(value))
            return None

        for chunk in value:
            if len(chunk) != 2:
                self.log.info('wrong MAC value: {0}'.format(value))
                return None

            for char in chunk:
                if char not in ['0', '1', '2', '3', '4',
                                '5', '6', '7', '8', '9',
                                'A', 'B', 'C', 'D', 'E', 'F']:
                    self.log.info('wrong MAC value: {0}'.format(value))
                    return None

        value = '{0:2s}:{1:2s}:{2:2s}:{3:2s}:{4:2s}:{5:2s}'.format(*value)
        return value

    def resetData(self):
        """
        resetData deletes all data already stored in classes just by redefining
        the classes. it send as well a signal, when the data is cleared.

        :return: nothing
        """
        self.firmware = Firmware(self.host)
        self.dome = Dome(self.host)
        self.setting = Setting(self.host)
        self.model = Model(parent=self, host=self.host)
        self.obsSite = ObsSite(self.host,
                               pathToData=self.pathToData,
                               verbose=self.verbose,
                               )
        self.satellite = Satellite(parent=self, host=self.host)
        self.geometry = Geometry(parent=self)

    def calcTransformationMatricesTarget(self):
        """
        :return: alt az
        """
        ha = self.obsSite.haJNowTarget
        dec = self.obsSite.decJNowTarget
        lat = self.obsSite.location.latitude
        pierside = self.obsSite.piersideTarget
        return self.geometry.calcTransformationMatrices(ha=ha,
                                                        dec=dec,
                                                        lat=lat,
                                                        pierside=pierside)

    def calcTransformationMatricesActual(self):
        """
        :return: alt az
        """
        ha = self.obsSite.haJNow
        dec = self.obsSite.decJNow
        lat = self.obsSite.location.latitude
        pierside = self.obsSite.pierside
        return self.geometry.calcTransformationMatrices(ha=ha,
                                                        dec=dec,
                                                        lat=lat,
                                                        pierside=pierside)
