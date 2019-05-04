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
from datetime import datetime
# external packages
import PyQt5
import numpy as np
# local imports
from mw4.base import indiClass


class CameraSignals(PyQt5.QtCore.QObject):
    """
    The CameraSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['CameraSignals']
    version = '0.1'

    finished = PyQt5.QtCore.pyqtSignal()
    message = PyQt5.QtCore.pyqtSignal(object)


class Camera(indiClass.IndiClass):
    """
    the class Camera inherits all information and handling of the Camera device.


        >>> fw = Camera(
        >>>           app=app
        >>>           host=host
        >>>           name=''
        >>>          )
    """

    __all__ = ['Dome',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    # update rate to 1000 milli seconds for setting indi server
    UPDATE_RATE = 1000

    def __init__(self,
                 app=None,
                 host=None,
                 name='',
                 ):
        super().__init__(host=host,
                         name=name
                         )

        self.app = app
        self.signals = CameraSignals()

    def setUpdateConfig(self, deviceName):
        """
        _setUpdateRate corrects the update rate of camera devices to get an defined
        setting regardless, what is setup in server side.

        :param deviceName:
        :return: success
        """

        if deviceName != self.name:
            return False

        if self.device is None:
            return False

        # setting polling updates in driver
        update = self.device.getNumber('POLLING_PERIOD')

        if 'PERIOD_MS' not in update:
            return False

        if update.get('PERIOD_MS', 0) == self.UPDATE_RATE:
            return True

        update['PERIOD_MS'] = self.UPDATE_RATE
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='POLLING_PERIOD',

                                        elements=update,
                                        )

        return suc

    def updateNumber(self, deviceName, propertyName):
        """
        updateNumber is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.

        :param deviceName:
        :param propertyName:
        :return:
        """

        if self.device is None:
            return False
        if deviceName != self.name:
            return False

        for element, value in self.device.getNumber(propertyName).items():
            self.data[element] = value
            # print(propertyName, element, value)

            if propertyName == 'CCD_EXPOSURE':
                if self.device.CCD_EXPOSURE['state'] == 'Idle':
                    pass
                elif self.device.CCD_EXPOSURE['state'] == 'Busy':
                    if value == 0:
                        self.signals.message.emit('download')
                    else:
                        self.signals.message.emit(f'expose {value:2.0f} s')
                elif self.device.CCD_EXPOSURE['state'] == 'Ok':
                    self.signals.finished.emit()
                    self.signals.message.emit('')

        return True

    def updateText(self, deviceName, propertyName):
        """
        updateNumber is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.

        :param deviceName:
        :param propertyName:
        :return:
        """

        if self.device is None:
            return False
        if deviceName != self.name:
            return False

        for element, value in self.device.getText(propertyName).items():
            self.data[element] = value
            # print(propertyName, element, value)
        return True

    def updateSwitch(self, deviceName, propertyName):
        """
        updateNumber is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.

        :param deviceName:
        :param propertyName:
        :return:
        """

        if self.device is None:
            return False
        if deviceName != self.name:
            return False

        for element, value in self.device.getSwitch(propertyName).items():
            self.data[element] = value
            # print(propertyName, element, value)
        return True

    def updateLight(self, deviceName, propertyName):
        """
        updateNumber is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.

        :param deviceName:
        :param propertyName:
        :return:
        """

        if self.device is None:
            return False
        if deviceName != self.name:
            return False

        for element, value in self.device.getLight(propertyName).items():
            self.data[element] = value
            # print(propertyName, element, value)
        return True
