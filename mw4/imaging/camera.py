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
            print(propertyName, element, value)

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
            print(propertyName, element, value)
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

    def canSubFrame(self, subFrame=100):
        """
        canSubFrame checks if a camera supports sub framing and reports back

        :param subFrame:
        :return: success
        """
        if subFrame > 100:
            return False
        if subFrame == 100:
            return True
        if subFrame < 10:
            return False
        if 'OffX' not in self.data or 'SizeX' not in self.data:
            return False

        return True

    def canBinning(self, binning=1):
        """
        canBinning checks if the camera supports that type of binning

        :param binning:
        :return: success
        """
        if binning == 1:
            return True
        if 'HOR_BIN' not in self.data:
            return False

        return True

    def canFilterPos(self, filterPos=0):
        """
        canFilterPos checks if the camera support filter selection

        :param filterPos:
        :return:
        """

        if filterPos == 0:
            return True
        if '' not in self.data:
            return False

        return True

    def calcSubFrame(self, subFrame=100):
        """
        calcSubFrame calculates the subFrame parameters depending on the percentage of
        the reduction. the subFrame will be centered on the image area.

        :param subFrame: percentage 0-100 of
        :return:
        """
        if subFrame < 10 or subFrame > 100:
            width = self.data['CCD_MAX_X']
            height = self.data['CCD_MAX_Y']
            posX = 0
            posY = 0
        else:
            width = int(self.data['CCD_MAX_X'] * subFrame / 100)
            height = int(self.data['CCD_MAX_Y'] * subFrame / 100)
            posX = int(self.data['CCD_MAX_X'] - width / 2)
            posY = int(self.data['CCD_MAX_Y'] - height / 2)

        return posX, posY, width, height

    def expose(self, expTime=3, binning=1, subFrame=100, filterPos=0):
        """

        :param expTime:
        :param binning:
        :param subFrame:
        :param filterPos:
        :return: success
        """

        if not self.canSubFrame(subFrame=subFrame):
            return False
        if not self.canBinning(binning=binning):
            return False
        if not self.canFilterPos(filterPos=filterPos):
            return False

        successOverall = False

        # setting compression to on as default
        indiCmd = self.device.getSwitch('CCD_COMPRESSION')
        if 'CCD_COMPRESS' not in indiCmd:
            return False
        indiCmd['CCD_COMPRESS'] = True
        suc = self.client.sendNewSwitch(deviceName=self.name,
                                        propertyName='CCD_COMPRESSION',
                                        elements=indiCmd,
                                        )
        successOverall = successOverall and suc

        # setting frame type to light
        indiCmd = self.device.getSwitch('CCD_FRAME_TYPE')
        if 'FRAME_LIGHT' not in indiCmd:
            return False
        indiCmd['FRAME_LIGHT'] = True
        suc = self.client.sendNewSwitch(deviceName=self.name,
                                        propertyName='CCD_FRAME_TYPE',
                                        elements=indiCmd,
                                        )
        successOverall = successOverall and suc

        # setting binning value for x and y equally
        indiCmd = self.device.getNumber('CCD_BINNING')
        if 'HOR_BIN' not in indiCmd:
            return False
        indiCmd['HOR_BIN'] = binning
        suc = self.client.sendNewNumber(deviceName=self.name,
                                        propertyName='CCD_BINNING',
                                        elements=indiCmd,
                                        )
        successOverall = successOverall and suc
        if 'VER_BIN' not in indiCmd:
            return False
        indiCmd['VER_BIN'] = binning
        suc = self.client.sendNewNumber(deviceName=self.name,
                                        propertyName='CCD_BINNING',
                                        elements=indiCmd,
                                        )
        successOverall = successOverall and suc

        # setting subFrame
        posX, posY, width, height = self.calcSubFrame(subFrame)

        indiCmd = self.device.getNumber('CCD_FRAME')
        if 'X' not in indiCmd:
            return False
        indiCmd['X'] = posX
        suc = self.client.sendNewNumber(deviceName=self.name,
                                        propertyName='CCD_FRAME',
                                        elements=indiCmd,
                                        )
        successOverall = successOverall and suc
        if 'Y' not in indiCmd:
            return False
        indiCmd['Y'] = posY
        suc = self.client.sendNewNumber(deviceName=self.name,
                                        propertyName='CCD_FRAME',
                                        elements=indiCmd,
                                        )
        successOverall = successOverall and suc
        if 'WIDTH' not in indiCmd:
            return False
        indiCmd['WIDTH'] = width
        suc = self.client.sendNewNumber(deviceName=self.name,
                                        propertyName='CCD_FRAME',
                                        elements=indiCmd,
                                        )
        successOverall = successOverall and suc
        if 'HEIGHT' not in indiCmd:
            return False
        indiCmd['HEIGHT'] = height
        suc = self.client.sendNewNumber(deviceName=self.name,
                                        propertyName='CCD_FRAME',
                                        elements=indiCmd,
                                        )
        successOverall = successOverall and suc

        # setting and starting exposure
        indiCmd = self.device.getNumber('CCD_EXPOSURE')
        if 'CCD_EXPOSURE_VALUE' not in indiCmd:
            return False
        indiCmd['CCD_EXPOSURE_VALUE'] = expTime
        suc = self.client.sendNewNumber(deviceName=self.name,
                                        propertyName='CCD_EXPOSURE',
                                        elements=indiCmd,
                                        )
        successOverall = successOverall and suc

        return successOverall

    def abort(self):
        """
        abort cancels the exposing

        :return: success
        """

        indiCmd = self.device.getSwitch('CCD_ABORT_EXPOSURE')
        if 'ABORT' not in indiCmd:
            return False
        indiCmd['ABORT'] = True
        suc = self.client.sendNewSwitch(deviceName=self.name,
                                        propertyName='CCD_ABORT_EXPOSURE',
                                        elements=indiCmd,
                                        )

        return suc
