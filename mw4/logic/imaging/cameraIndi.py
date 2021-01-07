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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import zlib
import os

# external packages
import astropy.io.fits as fits

# local imports
from base.indiClass import IndiClass


class CameraIndi(IndiClass):
    """
    the class Camera inherits all information and handling of the Camera device.


        >>> c = CameraIndi(app=None, signals=None, data=None)
    """

    __all__ = ['CameraIndi',
               ]

    # update rate to 1000 milli seconds for setting indi server
    UPDATE_RATE = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data
        self.imagePath = ''
        self.isDownloading = False

    def setUpdateConfig(self, deviceName):
        """
        _setUpdateRate corrects the update rate of camera devices to get an defined
        setting regardless, what is setup in server side.

        :param deviceName:
        :return: success
        """

        if deviceName != self.deviceName:
            return False

        if self.device is None:
            return False

        # set BLOB mode also
        self.client.setBlobMode(blobHandling='Also',
                                deviceName=deviceName)

        # setting a object name
        objectName = self.device.getText('FITS_HEADER')
        objectName['FITS_OBJECT'] = 'skymodel'
        self.client.sendNewText(deviceName=deviceName,
                                propertyName='FITS_HEADER',
                                elements=objectName,
                                )

        # setting WCS Control off
        wcs = self.device.getSwitch('WCS_CONTROL')
        wcs['WCS_DISABLE'] = 'On'

        self.client.sendNewSwitch(deviceName=deviceName,
                                  propertyName='WCS_CONTROL',
                                  elements=wcs,
                                  )

        # setting active device for telescope
        telescope = self.device.getText('ACTIVE_DEVICES')
        telescope['ACTIVE_TELESCOPE'] = 'LX200 10micron'
        self.client.sendNewText(deviceName=deviceName,
                                propertyName='ACTIVE_DEVICES',
                                elements=telescope,
                                )

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

    def setExposureState(self):
        """
        :return: success
        """
        if not hasattr(self.device, 'CCD_EXPOSURE'):
            return False

        value = self.data.get('CCD_EXPOSURE.CCD_EXPOSURE_VALUE', 0)

        if self.device.CCD_EXPOSURE['state'] == 'Idle':
            self.signals.message.emit('')

        elif self.device.CCD_EXPOSURE['state'] == 'Busy':
            if value == 0:
                self.isDownloading = True
                self.signals.message.emit('download')
                self.signals.integrated.emit()

            else:
                self.signals.message.emit(f'expose {value:2.0f} s')

        elif self.device.CCD_EXPOSURE['state'] == 'Ok':
            self.signals.message.emit('')

        if self.device.CCD_EXPOSURE['state'] in ['Idle', 'Ok'] and self.isDownloading:
            self.isDownloading = False

        return True

    def updateNumber(self, deviceName, propertyName):
        """
        updateNumber is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.

        :param deviceName:
        :param propertyName:
        :return:
        """
        if not super().updateNumber(deviceName, propertyName):
            return False

        if propertyName == 'CCD_EXPOSURE':
            self.setExposureState()

        return True

    def updateBLOB(self, deviceName, propertyName):
        """
        updateBLOB is called whenever a new BLOB is received in client. it runs
        through the device list and writes the number data to the according locations.

        :param deviceName:
        :param propertyName:
        :return: success
        """

        if not super().updateBLOB(deviceName, propertyName):
            return False

        data = self.device.getBlob(propertyName)

        if 'value' not in data:
            return False
        if 'name' not in data:
            return False
        if 'format' not in data:
            return False
        if data.get('name', '') != 'CCD1':
            return False
        if not self.imagePath:
            return False
        if not os.path.isdir(os.path.dirname(self.imagePath)):
            return False

        if data['format'] == '.fits.fz':
            HDU = fits.HDUList.fromstring(data['value'])
            fits.writeto(self.imagePath, HDU[0].data, HDU[0].header, overwrite=True)
            self.log.info('Image BLOB is in FPacked format')

        elif data['format'] == '.fits.z':
            HDU = fits.HDUList.fromstring(zlib.decompress(data['value']))
            fits.writeto(self.imagePath, HDU[0].data, HDU[0].header, overwrite=True)
            self.log.info('Image BLOB is compressed fits format')

        elif data['format'] == '.fits':
            HDU = fits.HDUList.fromstring(data['value'])
            fits.writeto(self.imagePath, HDU[0].data, HDU[0].header, overwrite=True)
            self.log.info('Image BLOB is uncompressed fits format')

        else:
            self.log.info('Image BLOB is not supported')

        self.signals.saved.emit(self.imagePath)
        return True

    def sendDownloadMode(self, fastReadout=False):
        """
        setDownloadMode sets the readout speed of the camera

        :return: success
        """

        if not self.device:
            return False

        # setting fast mode:
        quality = self.device.getSwitch('READOUT_QUALITY')
        self.log.debug(f'camera has readout quality entry: {quality}')

        if fastReadout:
            quality['QUALITY_LOW'] = 'On'
            quality['QUALITY_HIGH'] = 'Off'

        else:
            quality['QUALITY_LOW'] = 'Off'
            quality['QUALITY_HIGH'] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='READOUT_QUALITY',
                                        elements=quality,
                                        )

        return suc

    def expose(self,
               imagePath='',
               expTime=3,
               binning=1,
               fastReadout=True,
               posX=0,
               posY=0,
               width=1,
               height=1,
               focalLength=1,
               ):
        """

        :param imagePath:
        :param expTime:
        :param binning:
        :param fastReadout:
        :param posX:
        :param posY:
        :param width:
        :param height:
        :param focalLength:
        :return: success
        """

        if not self.device:
            return False

        self.imagePath = imagePath

        suc = self.sendDownloadMode(fastReadout=fastReadout)
        if not suc:
            self.log.debug('Download quality could not be set')

        indiCmd = self.device.getNumber('CCD_BINNING')
        indiCmd['HOR_BIN'] = binning
        indiCmd['VER_BIN'] = binning
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='CCD_BINNING',
                                        elements=indiCmd,
                                        )
        if not suc:
            self.log.debug('Binning could not be set')

        indiCmd = self.device.getNumber('CCD_FRAME')
        indiCmd['X'] = posX
        indiCmd['Y'] = posY
        indiCmd['WIDTH'] = width
        indiCmd['HEIGHT'] = height
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='CCD_FRAME',
                                        elements=indiCmd,
                                        )
        if not suc:
            self.log.debug('Frame could not be set')

        indiCmd = self.device.getNumber('CCD_EXPOSURE')
        indiCmd['CCD_EXPOSURE_VALUE'] = expTime
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='CCD_EXPOSURE',
                                        elements=indiCmd,
                                        )
        return suc

    def abort(self):
        """
        abort cancels the exposing

        :return: success
        """

        if not self.device:
            return False

        indiCmd = self.device.getSwitch('CCD_ABORT_EXPOSURE')

        if 'ABORT' not in indiCmd:
            return False

        indiCmd['ABORT'] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='CCD_ABORT_EXPOSURE',
                                        elements=indiCmd,
                                        )

        return suc

    def sendCoolerSwitch(self, coolerOn=False):
        """
        sendCoolerTemp send the desired cooler temp, but does not switch on / off the cooler

        :param coolerOn:
        :return: success
        """

        if not self.device:
            return False

        # setting fast mode:
        cooler = self.device.getSwitch('CCD_COOLER')

        if coolerOn:
            cooler['COOLER_ON'] = 'On'
            cooler['COOLER_OFF'] = 'Off'

        else:
            cooler['COOLER_ON'] = 'Off'
            cooler['COOLER_OFF'] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='CCD_COOLER',
                                        elements=cooler,
                                        )

        return suc

    def sendCoolerTemp(self, temperature=0):
        """
        sendCoolerTemp send the desired cooler temp, indi does automatically start cooler

        :param temperature:
        :return: success
        """

        if not self.device:
            return False

        temp = self.device.getNumber('CCD_TEMPERATURE')

        if 'CCD_TEMPERATURE_VALUE' not in temp:
            return False

        temp['CCD_TEMPERATURE_VALUE'] = temperature
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='CCD_TEMPERATURE',
                                        elements=temp,
                                        )

        return suc
