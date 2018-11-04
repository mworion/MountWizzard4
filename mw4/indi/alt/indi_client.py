############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #  ####
#      ##  ##  #  ##  #     #
#     # # # #  # # # #     ###
#    #  ##  #  ##  ##        #
#   #   #   #  #   #     ####
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.6.4
#
# Michael Würtenberger
# (c) 2016, 2017, 2018
#
# Licence APL2.0
#
###########################################################
import logging
import time
import zlib
import queue
import os
from xml.etree import ElementTree
import PyQt5
import indi.indiXML as indiXML
import astropy.io.fits as pyfits
from baseclasses import checkIP


class INDIClient(PyQt5.QtCore.QObject):
    logger = logging.getLogger(__name__)
    status = PyQt5.QtCore.pyqtSignal(int)
    statusCCD = PyQt5.QtCore.pyqtSignal(bool)
    statusEnvironment = PyQt5.QtCore.pyqtSignal(bool)
    statusDome = PyQt5.QtCore.pyqtSignal(bool)
    receivedImage = PyQt5.QtCore.pyqtSignal(bool)
    processMessage = PyQt5.QtCore.pyqtSignal(object)

    signalDestruct = PyQt5.QtCore.pyqtSignal()

    # INDI device types
    GENERAL_INTERFACE = 0
    TELESCOPE_INTERFACE = (1 << 0)
    CCD_INTERFACE = (1 << 1)
    GUIDER_INTERFACE = (1 << 2)
    FOCUSER_INTERFACE = (1 << 3)
    FILTER_INTERFACE = (1 << 4)
    DOME_INTERFACE = (1 << 5)
    GPS_INTERFACE = (1 << 6)
    WEATHER_INTERFACE = (1 << 7)
    AO_INTERFACE = (1 << 8)
    DUSTCAP_INTERFACE = (1 << 9)
    LIGHTBOX_INTERFACE = (1 << 10)
    DETECTOR_INTERFACE = (1 << 11)
    AUX_INTERFACE = (1 << 15)

    CYCLE = 200
    CONNECTION_TIMEOUT = 2000

    data = {
        'ServerIP': '',
        'ServerPort': 7624,
        'Device': {}
    }

    def __init__(self, app, thread):
        super().__init__()

        self.app = app
        self.thread = thread
        self.isRunning = False
        self.connectCounter = 0
        self.tagFrame = ''
        self.messageString = ''
        self.mutexIPChange = PyQt5.QtCore.QMutex()
        self.mutexIsRunning = PyQt5.QtCore.QMutex()
        self.checkIP = checkIP.CheckIP()
        self.socket = None
        self.newDeviceQueue = queue.Queue()
        self.imagePath = ''
        self.cameraDevice = ''
        self.environmentDevice = ''
        self.domeDevice = ''
        self.telescopeDevice = ''
        self.auxDevice = ''
        self.cycleTimer = None
        # signal slot
        self.app.ui.le_INDIServerIP.editingFinished.connect(self.changedINDIClientConnectionSettings)
        self.app.ui.le_INDIServerPort.editingFinished.connect(self.changedINDIClientConnectionSettings)
        self.app.ui.checkEnableINDI.stateChanged.connect(self.enableDisableINDI)

    def initConfig(self):
        try:
            if 'INDIServerPort' in self.app.config:
                self.app.ui.le_INDIServerPort.setText(self.app.config['INDIServerPort'])
            if 'INDIServerIP' in self.app.config:
                self.app.ui.le_INDIServerIP.setText(self.app.config['INDIServerIP'])
            if 'CheckEnableINDI' in self.app.config:
                self.app.ui.checkEnableINDI.setChecked(self.app.config['CheckEnableINDI'])
            if 'CheckEnableINDIListening' in self.app.config:
                self.app.ui.checkEnableINDIListening.setChecked(self.app.config['CheckEnableINDIListening'])
            if 'CheckEnableINDISolving' in self.app.config:
                self.app.ui.checkEnableINDISolving.setChecked(self.app.config['CheckEnableINDISolving'])
        except Exception as e:
            self.logger.error('item in config.cfg not be initialize, error:{0}'.format(e))
        finally:
            pass
        # setting changes in gui on false, because the set of the config changed them already
        self.changedINDIClientConnectionSettings()
        self.enableDisableINDI()

    def storeConfig(self):
        self.app.config['INDIServerPort'] = self.app.ui.le_INDIServerPort.text()
        self.app.config['INDIServerIP'] = self.app.ui.le_INDIServerIP.text()
        self.app.config['CheckEnableINDI'] = self.app.ui.checkEnableINDI.isChecked()
        self.app.config['CheckEnableINDIListening'] = self.app.ui.checkEnableINDIListening.isChecked()
        self.app.config['CheckEnableINDISolving'] = self.app.ui.checkEnableINDISolving.isChecked()

    def changedINDIClientConnectionSettings(self):
        if self.isRunning:
            self.mutexIPChange.lock()
            self.stop()
            self.data['ServerIP'] = self.app.ui.le_INDIServerIP.text()
            self.data['ServerPort'] = int(self.app.ui.le_INDIServerPort.text())
            self.thread.start()
            self.mutexIPChange.unlock()
        else:
            self.mutexIPChange.lock()
            self.data['ServerIP'] = self.app.ui.le_INDIServerIP.text()
            self.data['ServerPort'] = int(self.app.ui.le_INDIServerPort.text())
            self.mutexIPChange.unlock()
        self.app.messageQueue.put('Setting IP address for INDI to: {0}:{1}\n'.format(self.data['ServerIP'], self.data['ServerPort']))

    def enableDisableINDI(self):
        if self.app.ui.checkEnableINDI.isChecked():
            if not self.isRunning:
                self.thread.start()
        else:
            if self.isRunning:
                self.stop()
            self.status.emit(0)

    def run(self):
        self.logger.info('indi started')
        self.mutexIsRunning.lock()
        if not self.isRunning:
            self.isRunning = True
        self.mutexIsRunning.unlock()
        self.socket = PyQt5.QtNetwork.QTcpSocket()
        self.socket.setSocketOption(PyQt5.QtNetwork.QAbstractSocket.LowDelayOption, 1)
        self.socket.setSocketOption(PyQt5.QtNetwork.QAbstractSocket.KeepAliveOption, 1)
        self.socket.hostFound.connect(self.handleHostFound)
        self.socket.connected.connect(self.handleConnected)
        self.socket.stateChanged.connect(self.handleStateChanged)
        self.socket.disconnected.connect(self.handleDisconnect)
        self.socket.readyRead.connect(self.handleReadyRead)
        self.socket.error.connect(self.handleError)
        self.processMessage.connect(self.handleReceived)
        self.signalDestruct.connect(self.destruct, type=PyQt5.QtCore.Qt.BlockingQueuedConnection)
        self.cycleTimer = PyQt5.QtCore.QTimer(self)
        self.cycleTimer.setSingleShot(False)
        self.cycleTimer.timeout.connect(self.doCommand)
        self.cycleTimer.start(self.CYCLE)

    def stop(self):
        # if I leave the loop, I close the connection to remote host
        self.mutexIsRunning.lock()
        if self.isRunning:
            self.isRunning = False
            self.signalDestruct.emit()
            self.thread.quit()
            self.thread.wait()
        self.mutexIsRunning.unlock()
        self.logger.info('indi client stopped')

    @PyQt5.QtCore.pyqtSlot()
    def destruct(self):
        self.cycleTimer.stop()
        self.signalDestruct.disconnect(self.destruct)
        self.socket.hostFound.disconnect(self.handleHostFound)
        self.socket.connected.disconnect(self.handleConnected)
        self.socket.stateChanged.disconnect(self.handleStateChanged)
        self.socket.disconnected.disconnect(self.handleDisconnect)
        self.socket.readyRead.disconnect(self.handleReadyRead)
        self.socket.error.disconnect(self.handleError)
        self.socket.abort()

    def doCommand(self):
        self.doReconnect()
        self.handleNewDevice()
        self.app.sharedINDIDataLock.lockForRead()
        if not self.app.INDICommandQueue.empty() and (self.socket.state() == PyQt5.QtNetwork.QAbstractSocket.ConnectedState):
            indiCommand = self.app.INDICommandQueue.get()
            self.sendMessage(indiCommand)
        self.app.sharedINDIDataLock.unlock()

    def doReconnect(self):
        if self.socket.state() == PyQt5.QtNetwork.QAbstractSocket.UnconnectedState:
            if self.connectCounter == 0:
                self.app.sharedINDIDataLock.lockForRead()
                self.socket.connectToHost(self.data['ServerIP'], self.data['ServerPort'])
                self.app.sharedINDIDataLock.unlock()
            else:
                # connection build up is ongoing
                pass
            if self.connectCounter * self.CYCLE > self.CONNECTION_TIMEOUT:
                self.socket.abort()
                self.connectCounter = 0
            else:
                self.connectCounter += 1
        else:
            if self.socket.state() != PyQt5.QtNetwork.QAbstractSocket.ConnectedState:
                if self.connectCounter * self.CYCLE > self.CONNECTION_TIMEOUT:
                    self.socket.abort()
                    self.connectCounter = 0
                else:
                    self.connectCounter += 1
            else:
                # connected
                pass

    @PyQt5.QtCore.pyqtSlot()
    def handleHostFound(self):
        self.app.sharedINDIDataLock.lockForRead()
        self.logger.debug('INDI Server found at {}:{}'.format(self.data['ServerIP'], self.data['ServerPort']))
        self.app.sharedINDIDataLock.unlock()

    @PyQt5.QtCore.pyqtSlot()
    def handleConnected(self):
        self.app.sharedINDIDataLock.lockForRead()
        self.logger.info('INDI Server connected at {0}:{1}'.format(self.data['ServerIP'], self.data['ServerPort']))
        self.app.sharedINDIDataLock.unlock()
        # get all informations about existing devices on the choosen indi server
        self.app.INDICommandQueue.put(indiXML.clientGetProperties(indi_attr={'version': '1.7'}))

    def handleNewDevice(self):
        if not self.newDeviceQueue.empty():
            device = self.newDeviceQueue.get()
            # now place the information about accessible devices in the gui and set the connection status
            # and configure the new devices adequately
            # todo: handling of multiple devices of one type and doing the selection
            self.app.sharedINDIDataLock.lockForRead()
            if device in self.data['Device']:
                if 'DRIVER_INFO' in self.data['Device'][device]:
                    if int(self.data['Device'][device]['DRIVER_INFO']['DRIVER_INTERFACE']) & self.CCD_INTERFACE:
                        # make a shortcut for later use and knowing which is a Camera
                        self.cameraDevice = device
                        self.app.INDICommandQueue.put(
                            indiXML.newSwitchVector([indiXML.oneSwitch('On', indi_attr={'name': 'ABORT'})],
                                                    indi_attr={'name': 'CCD_ABORT_EXPOSURE', 'device': self.app.workerINDI.cameraDevice}))
                    elif int(self.data['Device'][device]['DRIVER_INFO']['DRIVER_INTERFACE']) & self.WEATHER_INTERFACE:
                        # make a shortcut for later use
                        self.environmentDevice = device
                    elif int(self.data['Device'][device]['DRIVER_INFO']['DRIVER_INTERFACE']) & self.TELESCOPE_INTERFACE:
                        # make a shortcut for later use
                        self.telescopeDevice = device
                    elif int(self.data['Device'][device]['DRIVER_INFO']['DRIVER_INTERFACE']) & self.DOME_INTERFACE:
                        # make a shortcut for later use
                        self.domeDevice = device
                    elif device == 'SQM':
                        self.auxDevice = device
                    # elif int(self.data['Device'][device]['DRIVER_INFO']['DRIVER_INTERFACE']) == 0:
                        # make a shortcut for later use
                else:
                    # if not ready, put it on the stack again !
                    self.newDeviceQueue.put(device)
            self.app.sharedINDIDataLock.unlock()

    @PyQt5.QtCore.pyqtSlot(PyQt5.QtNetwork.QAbstractSocket.SocketError)
    def handleError(self, socketError):
        if self.socket.error() > 0:
            self.logger.warning('INDI client connection fault, error: {0}'.format(socketError))

    @PyQt5.QtCore.pyqtSlot()
    def handleStateChanged(self):
        self.status.emit(self.socket.state())
        self.logger.debug('INDI client connection has state: {0}'.format(self.socket.state()))

    @PyQt5.QtCore.pyqtSlot()
    def handleDisconnect(self):
        self.logger.info('INDI client connection is disconnected from host')
        self.app.sharedINDIDataLock.lockForWrite()
        self.data['Device'] = {}
        self.app.sharedINDIDataLock.unlock()
        self.cameraDevice = ''
        self.environmentDevice = ''
        self.domeDevice = ''
        self.telescopeDevice = ''
        self.app.INDIStatusQueue.put({'Name': 'Environment', 'value': '---'})
        self.app.INDIStatusQueue.put({'Name': 'CCD', 'value': '---'})
        self.app.INDIStatusQueue.put({'Name': 'Dome', 'value': '---'})
        self.app.INDIStatusQueue.put({'Name': 'Telescope', 'value': '---'})
        self.app.INDIStatusQueue.put({'Name': 'Aux', 'value': '---'})

    @PyQt5.QtCore.pyqtSlot(object)
    def handleReceived(self, message):
        # central dispatcher for data coming from INDI devices. I makes the whole status and data evaluation and fits the
        # data to mountwizzard3
        if 'device' not in message.attr:
            return
        device = message.attr['device']
        # receiving all definitions for vectors in indi and building them up in self.data['Device']
        if isinstance(message, indiXML.DefBLOBVector):
            self.app.sharedINDIDataLock.lockForWrite()
            if device not in self.data['Device']:
                self.data['Device'][device] = {}
            if device in self.data['Device']:
                if 'name' in message.attr:
                    defVector = message.attr['name']
                    if defVector not in self.data['Device'][device]:
                        self.data['Device'][device][defVector] = {}
                    for elt in message.elt_list:
                        self.data['Device'][device][defVector][elt.attr['name']] = ''
            self.app.sharedINDIDataLock.unlock()

        elif isinstance(message, indiXML.SetBLOBVector):
            self.app.sharedINDIDataLock.lockForRead()
            if device in self.data['Device']:
                if int(self.data['Device'][device]['DRIVER_INFO']['DRIVER_INTERFACE']) & self.CCD_INTERFACE:
                    name = message.attr['name']
                    # ccd1 is the main camera in INDI
                    if name == 'CCD1':
                        # format tells me raw or compressed format
                        if 'format' in message.getElt(0).attr:
                            try:
                                if self.imagePath != '':
                                    if message.getElt(0).attr['format'] == '.fits':
                                        imageHDU = pyfits.HDUList.fromstring(message.getElt(0).getValue())
                                        imageHDU.writeto(self.imagePath, overwrite=True)
                                        self.logger.debug('Image BLOB is in raw fits format')
                                    else:
                                        imageHDU = pyfits.HDUList.fromstring(zlib.decompress(message.getElt(0).getValue()))
                                        imageHDU.writeto(self.imagePath, overwrite=True)
                                        self.logger.debug('Image BLOB is compressed fits format')
                                    self.receivedImage.emit(True)
                                else:
                                    # here are some functions to listen to image transfer on ethernet
                                    if self.app.ui.checkEnableINDIListening.isChecked():
                                        # received an image without asking for it. just listening
                                        path = os.getcwd() + '/images/listen.fit'
                                        if message.getElt(0).attr['format'] == '.fits':
                                            imageHDU = pyfits.HDUList.fromstring(message.getElt(0).getValue())
                                            imageHDU.writeto(path, overwrite=True)
                                            self.logger.debug('Image while listening is received in raw fits format')
                                        else:
                                            imageHDU = pyfits.HDUList.fromstring(zlib.decompress(message.getElt(0).getValue()))
                                            imageHDU.writeto(path, overwrite=True)
                                            self.logger.debug('Image while listening is received in compressed fits format')
                                        self.app.imageWindow.signalShowFitsImage.emit(path)
                                        # if there is a hint, we could solve it as well automatically
                                        if self.app.ui.checkEnableINDISolving.isChecked():
                                            self.app.imageWindow.signalSolveFitsImage.emit(path)
                                    else:
                                        # do nothing
                                        pass
                            except Exception as e:
                                self.receivedImage.emit(False)
                                self.logger.debug('Could not receive Image, error:{0}'.format(e))
                            finally:
                                pass
                        else:
                            self.logger.debug('Could not find format in message from device: {0}'.format(device))
                    else:
                        self.logger.debug('Got BLOB from device: {0}, name: {1}'.format(device, name))
                else:
                    self.logger.debug('Got unexpected BLOB from device: {0}'.format(device))
            else:
                self.logger.debug('Did not find device: {0} in device list'.format(device))
            self.app.sharedINDIDataLock.unlock()

        # deleting properties from devices
        elif isinstance(message, indiXML.DelProperty):
            self.app.sharedINDIDataLock.lockForWrite()
            if device in self.data['Device']:
                if 'name' in message.attr:
                    delVector = message.attr['name']
                    if delVector in self.data['Device'][device]:
                        del self.data['Device'][device][delVector]
            self.app.sharedINDIDataLock.unlock()

        # receiving changes from vectors and updating them ins self.data['Device]
        elif isinstance(message, indiXML.SetSwitchVector) or \
                isinstance(message, indiXML.SetTextVector) or \
                isinstance(message, indiXML.SetLightVector) or \
                isinstance(message, indiXML.SetNumberVector):
            self.app.sharedINDIDataLock.lockForWrite()
            if device in self.data['Device']:
                if 'name' in message.attr:
                    setVector = message.attr['name']
                    if setVector not in self.data['Device'][device]:
                        self.data['Device'][device][setVector] = {}
                        self.logger.warning('SetVector before DefVector in INDI protocol, device: {0}, vector: {1}'.format(device, setVector))
                    if 'state' in message.attr:
                        self.data['Device'][device][setVector]['state'] = message.attr['state']
                    if 'timeout' in message.attr:
                        self.data['Device'][device][setVector]['timeout'] = message.attr['timeout']
                    for elt in message.elt_list:
                        self.data['Device'][device][setVector][elt.attr['name']] = elt.getValue()
            self.app.sharedINDIDataLock.unlock()

        # receiving all definitions for vectors in indi and building them up in self.data['Device']
        elif isinstance(message, indiXML.DefSwitchVector) or \
                isinstance(message, indiXML.DefTextVector) or \
                isinstance(message, indiXML.DefLightVector) or \
                isinstance(message, indiXML.DefNumberVector):
            self.app.sharedINDIDataLock.lockForWrite()
            if device not in self.data['Device']:
                # new device !
                self.data['Device'][device] = {}
                self.newDeviceQueue.put(device)
            if device in self.data['Device']:
                if 'name' in message.attr:
                    defVector = message.attr['name']
                    if defVector not in self.data['Device'][device]:
                        self.data['Device'][device][defVector] = {}
                    if 'state' in message.attr:
                        self.data['Device'][device][defVector]['state'] = message.attr['state']
                    if 'perm' in message.attr:
                        self.data['Device'][device][defVector]['perm'] = message.attr['perm']
                    if 'timeout' in message.attr:
                        self.data['Device'][device][defVector]['timeout'] = message.attr['timeout']
                    for elt in message.elt_list:
                        self.data['Device'][device][defVector][elt.attr['name']] = elt.getValue()
            self.app.sharedINDIDataLock.unlock()

        self.app.sharedINDIDataLock.lockForRead()
        if device in self.data['Device']:
            if 'DRIVER_INFO' in self.data['Device'][device]:
                if int(self.data['Device'][device]['DRIVER_INFO']['DRIVER_INTERFACE']) & self.CCD_INTERFACE:
                    self.app.INDIStatusQueue.put({'Name': 'CCD', 'value': device})
                elif int(self.data['Device'][device]['DRIVER_INFO']['DRIVER_INTERFACE']) & self.WEATHER_INTERFACE:
                    self.app.INDIStatusQueue.put({'Name': 'Environment', 'value': device})
                elif int(self.data['Device'][device]['DRIVER_INFO']['DRIVER_INTERFACE']) & self.DOME_INTERFACE:
                    self.app.INDIStatusQueue.put({'Name': 'Dome', 'value': device})
                elif int(self.data['Device'][device]['DRIVER_INFO']['DRIVER_INTERFACE']) & self.TELESCOPE_INTERFACE:
                    self.app.INDIStatusQueue.put({'Name': 'Telescope', 'value': device})
                elif int(self.data['Device'][device]['DRIVER_INFO']['DRIVER_INTERFACE']) & self.AUX_INTERFACE:
                    self.app.INDIStatusQueue.put({'Name': 'Aux', 'value': device})
        self.app.sharedINDIDataLock.unlock()

    @PyQt5.QtCore.pyqtSlot()
    def handleReadyRead(self):
        # Add starting tag if this is new message.
        # we have to check and keep the first XML tag
        if len(self.messageString) == 0:
            self.messageString = "<data>"
        # Get message from socket.
        while self.socket.bytesAvailable() and self.isRunning:
            # print(self.socket.bytesAvailable(), len(self.messageString))
            try:
                self.messageString += self.socket.read(100000).decode()
            except Exception as e:
                self.logger.error('Cannot decode, error:{0}'.format(e))
            finally:
                pass
        # Add closing tag.
        self.messageString += "</data>"
        # Try and parse the message !
        try:
            messages = ElementTree.fromstring(self.messageString)
            self.messageString = ""
            for message in messages:
                xmlMessage = indiXML.parseETree(message)
                self.processMessage.emit(xmlMessage)
        # Message is incomplete, remove </data> and try again with more data
        except ElementTree.ParseError:
            self.messageString = self.messageString[:-7]
        finally:
            pass

    @PyQt5.QtCore.pyqtSlot()
    def handleReadyReadNew(self):
        # Get message from socket.
        while self.socket.bytesAvailable() and self.isRunning:
            # decode message and catch error
            try:
                self.messageString += self.socket.read(10000).decode()
            except Exception as e:
                self.logger.error('INDI message raw decode, error:{0}'.format(e))
            finally:
                pass
        # get first tag frame
        if self.tagFrame == '':
            self.tagFrame = self.messageString[1:50].split(' ')[0]
            print('start: ', self.tagFrame, len(self.messageString))
        # checking if closing first tag is there
        if self.messageString.endswith('</' + self.tagFrame + '>') or self.messageString.endswith('</' + self.tagFrame + '>\n'):
            # last part of message, process now
            messageComplete = True
            print('finished: ' + self.tagFrame)
        else:
            # otherwise continue
            messageComplete = False
            print(len(self.messageString), self.messageString[len(self.messageString)-30:], ord(self.messageString[-2]), ord(self.messageString[-1]))

        if messageComplete:
            # adding frame tags for INDI
            self.messageString = "<data>" + self.messageString + "</data>"
            try:
                # decode INDI XML elements
                messages = ElementTree.fromstring(self.messageString)
                # clear message
                for message in messages:
                    # print('message: ', message)
                    xmlMessage = indiXML.parseETree(message)
                    self.processMessage.emit(xmlMessage)
            except ElementTree.ParseError:
                print('error parse')
                self.logger.error('INDI XML message parse error')
            finally:
                print('reset to next round')
                self.messageString = ''
                self.tagFrame = ''
        else:
            # move on
            pass

    def sendMessage(self, indiCommand):
        if self.socket.state() == PyQt5.QtNetwork.QAbstractSocket.ConnectedState:
            self.socket.write(indiCommand.toXML() + b'\n')
            self.socket.flush()
        else:
            self.logger.warning('Socket not connected')
