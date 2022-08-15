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
from base.tpool import Worker
from base.indiClass import IndiClass
from logic.camera.cameraSupport import CameraSupport


class CameraIndi(IndiClass, CameraSupport):
    """
    """

    __all__ = ['CameraIndi']

    def __init__(self, app=None, signals=None, data=None):
        self.signals = signals
        super().__init__(app=app, data=data)
        self.imagePath = ''
        self.isDownloading = False

    def setUpdateConfig(self, deviceName):
        """
        :param deviceName:
        :return: success
        """
        if not super().setUpdateConfig(deviceName):
            return False

        suc = self.client.setBlobMode(blobHandling='Also',
                                      deviceName=deviceName)
        self.log.info(f'Blob mode [{deviceName}] success: [{suc}]')

        objectName = self.device.getText('FITS_HEADER')
        objectName['FITS_OBJECT'] = 'Skymodel'
        objectName['FITS_OBSERVER'] = 'MountWizzard4'
        suc = self.client.sendNewText(deviceName=deviceName,
                                      propertyName='FITS_HEADER',
                                      elements=objectName)
        self.log.info(f'Fits Header [{deviceName}] success: [{suc}]')

        telescope = self.device.getText('ACTIVE_DEVICES')
        telescope['ACTIVE_TELESCOPE'] = 'LX200 10micron'
        suc = self.client.sendNewText(deviceName=deviceName,
                                      propertyName='ACTIVE_DEVICES',
                                      elements=telescope)
        self.log.info(f'Active telescope [{deviceName}] success: [{suc}]')

        telescope = self.device.getSwitch('TELESCOPE_TYPE')
        telescope['TELESCOPE_PRIMARY'] = 'On'
        suc = self.client.sendNewSwitch(deviceName=deviceName,
                                        propertyName='TELESCOPE_TYPE',
                                        elements=telescope)
        self.log.info(f'Primary telescope [{deviceName}] success: [{suc}]')
        return True

    def setExposureState(self):
        """
        setExposureState rebuilds the state information integrated and download
        as it is not explicit defined in the INDI spec. So downloaded is reached
        when that INDI state for CCD_EXPOSURE goes to IDLE or OK -> Jasem Mutlaq.
        Another definition is done by myself, when INDI state for CCD_EXPOSURE is
        BUSY and the CCD_EXPOSURE_VALUE is not 0, then we should be on integration
        side, else the download should be started. The whole stuff is made,
        because on ALPACA and ASCOM side it's a step by step sequence, which has
        very defined states for each step. I would like ta have a common
        approach for all frameworks.

        :return: success
        """
        THRESHOLD = 0.00001
        value = self.data.get('CCD_EXPOSURE.CCD_EXPOSURE_VALUE')
        if self.device.CCD_EXPOSURE['state'] == 'Busy':
            if value is None:
                return False
            elif value <= THRESHOLD:
                if not self.isDownloading:
                    self.signals.exposed.emit()
                self.isDownloading = True
                self.signals.message.emit('download')
            else:
                self.signals.message.emit(f'expose {value:2.0f} s')
        elif self.device.CCD_EXPOSURE['state'] in ['Idle', 'Ok']:
            self.signals.downloaded.emit()
            self.signals.message.emit('')
            self.isDownloading = False
        elif self.device.CCD_EXPOSURE['state'] in ['Alert']:
            self.isDownloading = False
            self.signals.exposed.emit()
            self.signals.exposeReady.emit()
            self.signals.downloaded.emit()
            self.signals.saved.emit('')
            self.abort()
            self.log.warning('INDI camera state alert')
        else:
            t = f'[{self.deviceName}] state: [{self.device.CCD_EXPOSURE["state"]}]'
            self.log.warning(t)

        return True

    def updateNumber(self, deviceName, propertyName):
        """
        :param deviceName:
        :param propertyName:
        :return:
        """
        if propertyName == 'CCD_GAIN':
            elements = self.device.CCD_GAIN['elementList']['GAIN']
            if 'min' in elements and 'max' in elements:
                self.data['CCD_GAIN.GAIN_MIN'] = elements.get('min', 0)
                self.data['CCD_GAIN.GAIN_MAX'] = elements.get('max', 0)

        if propertyName == 'CCD_OFFSET':
            elements = self.device.CCD_OFFSET['elementList']['OFFSET']
            if 'min' in elements and 'max' in elements:
                self.data['CCD_OFFSET.OFFSET_MIN'] = elements.get('min', 0)
                self.data['CCD_OFFSET.OFFSET_MAX'] = elements.get('max', 0)

        if not super().updateNumber(deviceName, propertyName):
            return False

        if propertyName == 'CCD_EXPOSURE':
            self.setExposureState()

        if propertyName == 'CCD_TEMPERATURE':
            self.data['CAN_SET_CCD_TEMPERATURE'] = True
        return True

    def updateHeaderInfo(self, header):
        """
        adding for avoid having no entry in header
        :return:
        """
        if self.raJ2000 is None or self.decJ2000 is None:
            self.log.info('No coordinate for updating the header available')
            return header

        if 'RA' in header and 'DEC' in header:
            t = f'Found FitsRA:[{header["RA"]:4.3f}], '
            t += f'TargetRA: [{self.raJ2000._degrees:4.3f}], '
            t += f'FitsDEC: [{header["DEC"]:4.3f}], '
            t += f'TargetDEC: [{self.decJ2000._degrees:4.3f}]'
            self.log.debug(t)
            return header

        t = 'Adding missing RA/DEC header '
        t += f'TargetRA: [{self.raJ2000._degrees:4.3f}], '
        t += f'TargetDEC: [{self.decJ2000._degrees:4.3f}]'
        self.log.debug(t)

        header['RA'] = self.raJ2000._degrees
        header['DEC'] = self.decJ2000.degrees
        return header

    def saveBlobSignalsFinished(self):
        """
        :return:
        """
        self.signals.saved.emit(self.imagePath)
        self.signals.exposeReady.emit()
        self.signals.message.emit('')
        return True

    def workerSaveBLOB(self, data):
        """
        :param data:
        :return:
        """
        if data['format'] == '.fits.fz':
            HDU = fits.HDUList.fromstring(data['value'])
            self.log.info('Image BLOB is in FPacked format')

        elif data['format'] == '.fits.z':
            HDU = fits.HDUList.fromstring(zlib.decompress(data['value']))
            self.log.info('Image BLOB is compressed fits format')

        elif data['format'] == '.fits':
            HDU = fits.HDUList.fromstring(data['value'])
            self.log.info('Image BLOB is uncompressed fits format')

        else:
            self.log.info('Image BLOB is not supported')
            return True

        HDU[0].header = self.updateHeaderInfo(HDU[0].header)
        fits.writeto(self.imagePath, HDU[0].data, HDU[0].header,
                     overwrite=True, output_verify='silentfix')
        return True

    def updateBLOB(self, deviceName, propertyName):
        """
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

        self.signals.message.emit('Saving')
        worker = Worker(self.workerSaveBLOB, data)
        worker.signals.finished.connect(self.saveBlobSignalsFinished)
        self.threadPool.start(worker)
        return True

    def sendDownloadMode(self, fastReadout=False):
        """
        :return: success
        """
        quality = self.device.getSwitch('READOUT_QUALITY')
        self.log.info(f'Camera has readout quality entry: {quality}')

        if fastReadout:
            quality['QUALITY_LOW'] = 'On'
            quality['QUALITY_HIGH'] = 'Off'
        else:
            quality['QUALITY_LOW'] = 'Off'
            quality['QUALITY_HIGH'] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='READOUT_QUALITY',
                                        elements=quality)
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
               ra=None,
               dec=None,
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
        :param ra:
        :param dec:

        :return: success
        """
        if not self.device:
            self.log.error('Expose, but no device present')
            return False

        self.raJ2000 = ra
        self.decJ2000 = dec
        self.imagePath = imagePath
        suc = self.sendDownloadMode(fastReadout=fastReadout)
        if not suc:
            self.log.info('Download quality could not be set')

        indiCmd = self.device.getNumber('CCD_BINNING')
        indiCmd['HOR_BIN'] = binning
        indiCmd['VER_BIN'] = binning
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='CCD_BINNING',
                                        elements=indiCmd)
        if not suc:
            self.log.info('Binning could not be set')

        indiCmd = self.device.getNumber('CCD_FRAME')
        indiCmd['X'] = posX
        indiCmd['Y'] = posY
        indiCmd['WIDTH'] = width
        indiCmd['HEIGHT'] = height
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='CCD_FRAME',
                                        elements=indiCmd)
        if not suc:
            self.log.info('Frame could not be set')

        indiCmd = self.device.getNumber('CCD_EXPOSURE')
        indiCmd['CCD_EXPOSURE_VALUE'] = expTime
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='CCD_EXPOSURE',
                                        elements=indiCmd)
        return suc

    def abort(self):
        """
        :return: success
        """
        if not self.device:
            return False

        self.raJ2000 = None
        self.decJ2000 = None
        indiCmd = self.device.getSwitch('CCD_ABORT_EXPOSURE')
        if 'ABORT' not in indiCmd:
            return False

        indiCmd['ABORT'] = 'On'
        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='CCD_ABORT_EXPOSURE',
                                        elements=indiCmd)
        return suc

    def sendCoolerSwitch(self, coolerOn=False):
        """
        :param coolerOn:
        :return: success
        """
        if not self.device:
            return False

        cooler = self.device.getSwitch('CCD_COOLER')
        if coolerOn:
            cooler['COOLER_ON'] = 'On'
            cooler['COOLER_OFF'] = 'Off'

        else:
            cooler['COOLER_ON'] = 'Off'
            cooler['COOLER_OFF'] = 'On'

        suc = self.client.sendNewSwitch(deviceName=self.deviceName,
                                        propertyName='CCD_COOLER',
                                        elements=cooler)
        return suc

    def sendCoolerTemp(self, temperature=0):
        """
        :param temperature:
        :return: success
        """
        if not self.device:
            return False

        element = self.device.getNumber('CCD_TEMPERATURE')
        if 'CCD_TEMPERATURE_VALUE' not in element:
            return False

        element['CCD_TEMPERATURE_VALUE'] = temperature
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='CCD_TEMPERATURE',
                                        elements=element)
        return suc

    def sendOffset(self, offset=0):
        """
        :param offset:
        :return: success
        """
        if not self.device:
            return False

        element = self.device.getNumber('CCD_OFFSET')
        if 'OFFSET' not in element:
            return False

        element['OFFSET'] = offset
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='CCD_OFFSET',
                                        elements=element)
        return suc

    def sendGain(self, gain=0):
        """
        :param gain:
        :return: success
        """
        if not self.device:
            return False

        element = self.device.getNumber('CCD_GAIN')
        if 'GAIN' not in element:
            return False

        element['GAIN'] = gain
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='CCD_GAIN',
                                        elements=element)
        return suc
