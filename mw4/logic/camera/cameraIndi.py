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
from base.tpool import Worker
from base.indiClass import IndiClass
from base.transform import JNowToJ2000


class CameraIndi(IndiClass):
    """
        >>> c = CameraIndi(app=None, signals=None, data=None)
    """

    __all__ = ['CameraIndi',
               ]

    # update rate to 1000 milli seconds for setting indi server
    UPDATE_RATE = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.threadPool = app.threadPool
        self.signals = signals
        self.data = data
        self.imagePath = ''
        self.ra = None
        self.dec = None
        self.isDownloading = False

    def setUpdateConfig(self, deviceName):
        """
        :param deviceName:
        :return: success
        """
        if deviceName != self.deviceName:
            return False
        if self.device is None:
            return False

        self.client.setBlobMode(blobHandling='Also',
                                deviceName=deviceName)

        objectName = self.device.getText('FITS_HEADER')
        objectName['FITS_OBJECT'] = 'skymodel'
        self.client.sendNewText(deviceName=deviceName,
                                propertyName='FITS_HEADER',
                                elements=objectName,
                                )

        wcs = self.device.getSwitch('WCS_CONTROL')
        wcs['WCS_DISABLE'] = 'On'
        self.client.sendNewSwitch(deviceName=deviceName,
                                  propertyName='WCS_CONTROL',
                                  elements=wcs,
                                  )

        telescope = self.device.getText('ACTIVE_DEVICES')
        telescope['ACTIVE_TELESCOPE'] = 'LX200 10micron'
        self.client.sendNewText(deviceName=deviceName,
                                propertyName='ACTIVE_DEVICES',
                                elements=telescope,
                                )

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
        setExposureState rebuilds the state information integrated and download as it
        is not explicit defined in the INDI spec. So downloaded is reached when that        
        INDI state for CCD_EXPOSURE goes to IDLE or OK -> Jasem Mutlaq. Another definition
        is done by myself, when INDI state for CCD_EXPOSURE is BUSY and the CCD_EPOSURE_VALUE
        is not 0, then we should be on integration side, else the download shoulds be started.
        The whole stuff is made, because on ALPACA and ASCOM side it's a step by step 
        sequence, which has very defined states for each step and I would like ta have a 
        common approach for all frameworks. 
  
        :return: success
        """
        # todo: if setExp only called, when prop is CCD_EXP, then there 
        # todo: should be no check against it. 
        
        if not hasattr(self.device, 'CCD_EXPOSURE'):
            return False

        # todo: does it makes sense not to set a default for the value,
        # todo: but to check if the entry is already there if ..is None
        
        # if busy is set one packet before EXP_Value is set, then we send
        # slew before we have integrated the image, just because we set the value
        # to 0 if no entry is made.
        
        # What about setting busy, but keeping the old value of exposure in?
        # This value will be in any case 0 after the last exposure. Does ist make
        # sense to remove this value from the dict if we check for None in the future
        
        # Question to be answered: if a INDI driver reports back zero exposure, is he
        # really in download mode ?
        
        value = self.data.get('CCD_EXPOSURE.CCD_EXPOSURE_VALUE', 0)
        if self.device.CCD_EXPOSURE['state'] == 'Idle':
            self.signals.message.emit('')

        elif self.device.CCD_EXPOSURE['state'] == 'Busy':
            if value == 0:
                if not self.isDownloading:
                    self.signals.integrated.emit()
                self.isDownloading = True
                self.signals.message.emit('download')

            else:
                self.signals.message.emit(f'expose {value:2.0f} s')

        elif self.device.CCD_EXPOSURE['state'] == 'Ok':
            pass
            # why having here removed the message emit
            # self.signals.message.emit('')

        if self.device.CCD_EXPOSURE['state'] in ['Idle', 'Ok']:
            self.isDownloading = False
            
        """
        as result the following solution would be there:
        
        value = self.data.get('CCD_EXPOSURE.CCD_EXPOSURE_VALUE')
        if self.device.CCD_EXPOSURE['state'] == 'Busy':
            if value is None:
                return False
            elif value == 0:
                if not self.isDownloading:
                    self.signals.integrated.emit()
                self.isDownloading = True
                self.signals.message.emit('download')
            else:
                self.signals.message.emit(f'expose {value:2.0f} s')

        elif self.device.CCD_EXPOSURE['state'] in ['Idle', 'Ok']:
            del(self.data['CCD_EXPOSURE.CCD_EXPOSURE_VALUE'])
            self.signals.message.emit('')
            self.isDownloading = False
        """

        return True

    def updateNumber(self, deviceName, propertyName):
        """
        :param deviceName:
        :param propertyName:
        :return:
        """
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
        if 'RA' in header and 'DEC' in header:
            return header

        if self.ra is None or self.dec is None:
            return header

        self.log.info('Missing Ra/Dec in header adding from mount')
        header['RA'] = self.ra._degrees
        header['DEC'] = self.dec.degrees
        return header

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
            self.signals.saved.emit(self.imagePath)
            self.signals.message.emit('')
            return True

        HDU[0].header = self.updateHeaderInfo(HDU[0].header)
        fits.writeto(self.imagePath, HDU[0].data, HDU[0].header,
                     overwrite=True, output_verify='silentfix+warn')

        self.signals.saved.emit(self.imagePath)
        self.signals.message.emit('')
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
        self.threadPool.start(worker)
        return True

    def sendDownloadMode(self, fastReadout=False):
        """
        :return: success
        """
        if not self.device:
            return False

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
        isMount = self.app.deviceStat['mount']
        if isMount:
            ra = self.app.mount.obsSite.raJNow
            dec = self.app.mount.obsSite.decJNow
            timeJD = self.app.mount.obsSite.timeJD
            if ra is not None and dec is not None and timeJD is not None:
                ra, dec = JNowToJ2000(ra, dec, timeJD)
            self.ra = ra
            self.dec = dec
        else:
            self.ra = None
            self.dec = None

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
                                        elements=cooler,
                                        )
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
                                        elements=element,
                                        )
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
                                        elements=element,
                                        )
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
                                        elements=element,
                                        )
        return suc
