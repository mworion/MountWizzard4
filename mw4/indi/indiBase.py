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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import base64
# external packages
import PyQt5
import PyQt5.QtNetwork
import xml.etree.ElementTree
# local import
from mw4.indi import indiXML


class IndiBase(PyQt5.QtCore.QObject):
    """
    """

    __all__ = ['IndiBase',
               'getDevice',
               'getDevices',
               'connect',
               'disconnect',
               'sendCmd',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

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

    # default port indi servers
    DEFAULT_PORT = 7624
    # timeout for server
    CONNECTION_TIMEOUT = 2000

    # signals
    newDevice = PyQt5.QtCore.pyqtSignal(str)
    delDevice = PyQt5.QtCore.pyqtSignal(str)
    newProperty = PyQt5.QtCore.pyqtSignal(str)
    delProperty = PyQt5.QtCore.pyqtSignal(str)
    newVector = PyQt5.QtCore.pyqtSignal(str)
    connected = PyQt5.QtCore.pyqtSignal()
    disconnected = PyQt5.QtCore.pyqtSignal()

    def __init__(self,
                 host=None,
                 ):
        super().__init__()

        self.host = host

        self.isConnected = False
        self.devices = dict()

        self.socket = PyQt5.QtNetwork.QTcpSocket()
        self.socket.readyRead.connect(self._handleReadyRead)
        self.socket.error.connect(self._handleError)

        self.parser = xml.etree.ElementTree.XMLPullParser(['start', 'end'])
        self.parser.feed('<fakeindiroot>')
        # clear the event queue of parser, because we fed a fake root
        for _, _ in self.parser.read_events():
            pass

        # link signals
        self.newDevice.connect(self.logNewDevice)
        self.newProperty.connect(self.logNewProperty)
        self.delProperty.connect(self.logDelProperty)
        self.newVector.connect(self.logNewVector)

    @property
    def host(self):
        return self._host

    def checkFormat(self, value):
        # checking format
        if not value:
            self.logger.error('wrong host value: {0}'.format(value))
            return None
        if not isinstance(value, (tuple, str)):
            self.logger.error('wrong host value: {0}'.format(value))
            return None
        # now we got the right format
        if isinstance(value, str):
            value = (value, self.DEFAULT_PORT)
        return value

    @host.setter
    def host(self, value):
        value = self.checkFormat(value)
        self._host = value

    def connect(self, device=''):
        if self.isConnected:
            return True
        self.socket.connectToHost(*self._host)
        if not self.socket.waitForConnected(self.CONNECTION_TIMEOUT):
            self.isConnected = False
            return False
        self.isConnected = True
        data = indiXML.clientGetProperties(indi_attr={'version': '1.7',
                                                      'device': device})
        self.sendCmd(data)
        self.connected.emit()
        return True

    def disconnect(self):
        if not self.isConnected:
            return True
        self.socket.close()
        self.isConnected = False
        self._clearDevices()
        self.disconnected.emit()
        return True

    def _getDriverInterface(self, device):
        val = self.devices[device].get('DRIVER_INFO', '')
        if val:
            interface = self.devices[device]['DRIVER_INFO'].get('DRIVER_INTERFACE', '')
            return int(interface)
        else:
            return 0

    def getDevice(self, device):
        return self.devices[device]

    def getDevices(self, driverInterface):
        deviceList = list()
        for device in self.devices:
            if self._getDriverInterface(device) & driverInterface:
                deviceList.append(device)
        return deviceList

    def _clearDevices(self):
        for device in self.devices:
            del self.devices[device]
            self.delDevice.emit(device)

    def _dispatchCmd(self, elem):
        elem = indiXML.parseETree(elem)
        if 'device' not in elem.attr:
            self.logger.error('No device in elem: {0}'.format(elem))
            return False

        device = elem.attr['device']
        if device not in self.devices:
            self.devices[device] = {}
            self.newDevice.emit(device)

        # deleting properties from devices
        if isinstance(elem, indiXML.DelProperty):
            if device not in self.devices:
                return False
            if 'name' not in elem.attr:
                return False
            delVector = elem.attr['name']
            if delVector in self.devices[device]:
                del self.devices[device][delVector]
                self.delProperty.emit(delVector)

        # receiving changes from vectors and updating them them up in self.devices
        elif isinstance(elem, (indiXML.SetSwitchVector,
                               indiXML.SetTextVector,
                               indiXML.SetLightVector,
                               indiXML.SetNumberVector,
                               )
                        ):
            if device not in self.devices:
                return False
            if 'name' not in elem.attr:
                return False
            setVector = elem.attr['name']
            self.newVector.emit(setVector)
            if setVector not in self.devices[device]:
                self.devices[device][setVector] = {}
            self.devices[device][setVector]['label'] = elem.attr.get('label', '')
            self.devices[device][setVector]['group'] = elem.attr.get('group', '')
            self.devices[device][setVector]['state'] = elem.attr.get('state', '')
            self.devices[device][setVector]['perm'] = elem.attr.get('perm', '')
            self.devices[device][setVector]['timeout'] = elem.attr.get('timeout', '')
            self.devices[device][setVector]['timestamp'] = elem.attr.get('timestamp', '')
            self.devices[device][setVector]['message'] = elem.attr.get('message', '')
            for elt in elem.elt_list:
                self.devices[device][setVector][elt.attr['name']] = elt.getValue()

        # receiving all definitions for vectors in indi and building them up in self.devices
        elif isinstance(elem, (indiXML.DefSwitchVector,
                               indiXML.DefTextVector,
                               indiXML.DefLightVector,
                               indiXML.DefNumberVector,
                               )
                        ):
            if device not in self.devices:
                return False
            if 'name' not in elem.attr:
                return False
            defVector = elem.attr['name']
            self.newProperty.emit(defVector)
            if defVector not in self.devices[device]:
                self.devices[device][defVector] = {}
            self.devices[device][defVector]['label'] = elem.attr.get('label', '')
            self.devices[device][defVector]['group'] = elem.attr.get('group', '')
            self.devices[device][defVector]['state'] = elem.attr.get('state', '')
            self.devices[device][defVector]['perm'] = elem.attr.get('perm', '')
            self.devices[device][defVector]['timeout'] = elem.attr.get('timeout', '')
            self.devices[device][defVector]['timestamp'] = elem.attr.get('timestamp', '')
            self.devices[device][defVector]['message'] = elem.attr.get('message', '')
            for elt in elem.elt_list:
                self.devices[device][defVector][elt.attr['name']] = elt.getValue()

    @PyQt5.QtCore.pyqtSlot()
    def _handleReadyRead(self):
        buf = self.socket.readAll()
        self.parser.feed(buf)
        for event, elem in self.parser.read_events():
            # print(self.curDepth, event, elem.tag, elem.keys(), '\n')
            if event == 'start':
                self.curDepth += 1
            elif event == 'end':
                self.curDepth -= 1
            else:
                self.logger.error('Problem parsing event: {0}'.format(event))
            if self.curDepth > 0:
                continue
            # print('Parsed ', elem.tag)
            self._dispatchCmd(elem)

    @PyQt5.QtCore.pyqtSlot(PyQt5.QtNetwork.QAbstractSocket.SocketError)
    def _handleError(self, socketError):
        if not self.isConnected:
            return
        self.logger.warning('INDI client connection fault, error: {0}'.format(socketError))
        self.socket.close()

    def sendCmd(self, indiCommand):
        if self.socket:
            self.socket.write(indiCommand.toXML() + b'\n')
            self.socket.flush()

    @PyQt5.QtCore.pyqtSlot(str)
    def logNewDevice(self, name):
        print('new device: ', name)

    @PyQt5.QtCore.pyqtSlot(str)
    def logNewProperty(self, name):
        print('new property: ', name)

    @PyQt5.QtCore.pyqtSlot(str)
    def logDelProperty(self, name):
        print('del property: ', name)

    @PyQt5.QtCore.pyqtSlot(str)
    def logNewVector(self, name):
        print('new vector: ', name)
