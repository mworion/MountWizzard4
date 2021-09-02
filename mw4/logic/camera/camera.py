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
import logging
import platform

# external packages
import PyQt5
from PyQt5.QtTest import QTest

# local imports
from logic.camera.cameraIndi import CameraIndi
from logic.camera.cameraAlpaca import CameraAlpaca
if platform.system() == 'Windows':
    from logic.camera.cameraAscom import CameraAscom


class CameraSignals(PyQt5.QtCore.QObject):
    """
    """

    __all__ = ['CameraSignals']

    integrated = PyQt5.QtCore.pyqtSignal()
    saved = PyQt5.QtCore.pyqtSignal(object)
    message = PyQt5.QtCore.pyqtSignal(object)

    serverConnected = PyQt5.QtCore.pyqtSignal()
    serverDisconnected = PyQt5.QtCore.pyqtSignal(object)
    deviceConnected = PyQt5.QtCore.pyqtSignal(str)
    deviceDisconnected = PyQt5.QtCore.pyqtSignal(str)


class Camera:

    __all__ = ['Camera',
               ]

    log = logging.getLogger(__name__)

    def __init__(self, app):

        self.app = app
        self.threadPool = app.threadPool
        self.signals = CameraSignals()
        # todo: to be removed
        self.exposing = False

        self.data = {}
        self.defaultConfig = {'framework': '',
                              'frameworks': {}}
        self.framework = ''
        self.run = {
            'indi': CameraIndi(self.app, self.signals, self.data),
            'alpaca': CameraAlpaca(self.app, self.signals, self.data),
        }

        if platform.system() == 'Windows':
            self.run['ascom'] = CameraAscom(self.app, self.signals, self.data)
            ascomSignals = self.run['ascom'].ascomSignals
            ascomSignals.serverConnected.connect(self.signals.serverConnected)
            ascomSignals.serverDisconnected.connect(self.signals.serverDisconnected)
            ascomSignals.deviceConnected.connect(self.signals.deviceConnected)
            ascomSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

        for fw in self.run:
            self.defaultConfig['frameworks'].update(self.run[fw].defaultConfig)

        # signalling from subclasses to main
        alpacaSignals = self.run['alpaca'].client.signals
        alpacaSignals.serverConnected.connect(self.signals.serverConnected)
        alpacaSignals.serverDisconnected.connect(self.signals.serverDisconnected)
        alpacaSignals.deviceConnected.connect(self.signals.deviceConnected)
        alpacaSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

        indiSignals = self.run['indi'].client.signals
        indiSignals.serverConnected.connect(self.signals.serverConnected)
        indiSignals.serverDisconnected.connect(self.signals.serverDisconnected)
        indiSignals.deviceConnected.connect(self.signals.deviceConnected)
        indiSignals.deviceDisconnected.connect(self.signals.deviceDisconnected)

        # todo: to be removed
        self.signals.saved.connect(self.resetExposed)

    def startCommunication(self, loadConfig=False):
        """
        :param loadConfig:
        :return: success
        """
        if self.framework in self.run.keys():
            suc = self.run[self.framework].startCommunication(loadConfig=loadConfig)
            return suc
        else:
            return False

    def stopCommunication(self):
        """
        :return: success

        """
        if self.framework in self.run.keys():
            suc = self.run[self.framework].stopCommunication()
            return suc
        else:
            return False

    def canSubFrame(self, subFrame=100):
        """
        :param subFrame:
        :return: success
        """
        if subFrame > 100:
            return False
        if subFrame < 10:
            return False
        if 'CCD_FRAME.X' not in self.data or 'CCD_FRAME.Y' not in self.data:
            return False

        return True

    def canBinning(self, binning=1):
        """
        :param binning:
        :return: success
        """
        if binning < 1:
            return False
        if binning > 4:
            return False
        if 'CCD_BINNING.HOR_BIN' not in self.data:
            return False

        return True

    def calcSubFrame(self, subFrame=100):
        """
        :param subFrame: percentage 0-100 of
        :return: success
        """
        if 'CCD_INFO.CCD_MAX_X' not in self.data:
            return False
        if 'CCD_INFO.CCD_MAX_Y' not in self.data:
            return False

        maxX = self.data['CCD_INFO.CCD_MAX_X']
        maxY = self.data['CCD_INFO.CCD_MAX_Y']

        if subFrame < 10 or subFrame > 100:
            width = maxX
            height = maxY
            posX = 0
            posY = 0

        else:
            width = int(maxX * subFrame / 100)
            height = int(maxY * subFrame / 100)
            posX = int((maxX - width) / 2)
            posY = int((maxY - height) / 2)

        return posX, posY, width, height

    def sendDownloadMode(self, fastReadout=False):
        """
        :return: success
        """
        if self.framework in self.run.keys():
            suc = self.run[self.framework].sendDownloadMode(fastReadout=fastReadout)
            return suc
        else:
            return False

    # todo: to be removed
    def resetExposed(self):
        """
        :return: True for test purpose
        """
        self.exposing = False
        return True

    def expose(self,
               imagePath='',
               expTime=3,
               binning=1,
               subFrame=100,
               fastReadout=True,
               focalLength=1):
        """
        :param imagePath:
        :param expTime:
        :param binning:
        :param subFrame:
        :param fastReadout:
        :param focalLength:
        :return: success
        """
        if self.framework not in self.run.keys():
            return False
        if not imagePath:
            return False
        if not self.canSubFrame(subFrame=subFrame):
            return False
        if not self.canBinning(binning=binning):
            return False

        result = self.calcSubFrame(subFrame=subFrame)
        if not result:
            return False

        posX, posY, width, height = result

        # todo: to be removed with new signal combination
        # this protects against overrun
        if self.exposing:
            self.log.warning('Expose overrun happened')
        while self.exposing:
            QTest.qWait(250)
        self.exposing = True

        text = f'Image bin:{binning}, posX:{posX}, posY:{posY}'
        text += f', width:{width}, height:{height}, fast:{fastReadout}'
        self.log.debug(text)
        suc = self.run[self.framework].expose(imagePath=imagePath,
                                              expTime=expTime,
                                              binning=binning,
                                              fastReadout=fastReadout,
                                              posX=posX,
                                              posY=posY,
                                              width=width,
                                              height=height,
                                              focalLength=focalLength)
        return suc

    def abort(self):
        """
        :return: success
        """
        # todo: to be removed
        self.exposing = False
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].abort()
        self.signals.message.emit('')
        return suc

    def sendCoolerSwitch(self, coolerOn=False):
        """
        :param coolerOn:
        :return: success
        """
        if self.framework not in self.run.keys():
            return False
        suc = self.run[self.framework].sendCoolerSwitch(coolerOn=coolerOn)
        return suc

    def sendCoolerTemp(self, temperature=0):
        """
        :param temperature:
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].sendCoolerTemp(temperature=temperature)
        return suc

    def sendOffset(self, offset=0):
        """
        :param offset:
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].sendOffset(offset=offset)
        return suc

    def sendGain(self, gain=0):
        """
        :param gain:
        :return: success
        """
        if self.framework not in self.run.keys():
            return False

        suc = self.run[self.framework].sendGain(gain=gain)
        return suc
