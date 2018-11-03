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
from PyQt5 import QtCore
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket
import xml.etree.ElementTree
# local import
from mw4.indi import INDI
from mw4.indi import indiBaseMediator


class IndiBaseClient(PyQt5.QtCore.QObject):
    """
    """

    __all__ = ['IndiBaseClient',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    # default port indi servers
    DEFAULT_PORT = 7624
    # timeout for server
    CONNECTION_TIMEOUT = 2000

    _prop_tags = {
        INDI.INDI_PROPERTY_TYPE.INDI_TEXT: 'TextVector',
        INDI.INDI_PROPERTY_TYPE.INDI_NUMBER: 'NumberVector',
        INDI.INDI_PROPERTY_TYPE.INDI_SWITCH: 'SwitchVector',
        INDI.INDI_PROPERTY_TYPE.INDI_LIGHT: 'LightVector',
        INDI.INDI_PROPERTY_TYPE.INDI_BLOB: 'BLOBVector'
    }
    _elem_tags = {
        INDI.INDI_PROPERTY_TYPE.INDI_TEXT: 'oneText',
        INDI.INDI_PROPERTY_TYPE.INDI_NUMBER: 'oneNumber',
        INDI.INDI_PROPERTY_TYPE.INDI_SWITCH: 'oneSwitch',
        INDI.INDI_PROPERTY_TYPE.INDI_LIGHT: 'oneLight',
        INDI.INDI_PROPERTY_TYPE.INDI_BLOB: 'oneBLOB'
    }

    def __init__(self,
                 host=None,
                 mediator=None,
                 ):
        super().__init__()

        self._host = host
        if not mediator:
            self.mediator = IndiBaseMediator(self.logger)
        else:
            self.mediator = mediator

        self.isConnected = False
        self.devices = dict()
        self.blob_modes = dict()
        self.curChunk = []
        self.curDepth = 0

        self.socket = QTcpSocket()
        self.socket.readyRead.connect(self.handleReadyRead)
        self.socket.error.connect(self.handleError)

        self.parser = xml.etree.ElementTree.XMLPullParser(['start', 'end'])
        self.parser.feed('<fakeindiroot>')

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

    def connect(self):
        if self.isConnected:
            return True
        self.socket.connectToHost(self.host.decode(), self.port)
        if not self.socket.waitForConnected(self.CONNECTION_TIMEOUT):
            self.isConnected = False
            return False
        self.isConnected = True
        self.socket.write(b'<getProperties version="'+INDI.INDIV+b'"/>')
        return True

    def disconnect(self):
        if not self.isConnected:
            return True
        self.socket.close()
        self.isConnected = False
        self.devices.clear()
        return True

    @QtCore.pyqtSlot()
    def handleReadyRead(self):
        buf = self.socket.readAll()
        self.parser.feed(buf)
        for event, elem in self.parser.read_events():
            # print(event, elem.tag, elem.keys())
            if event == 'start':
                self.curDepth += 1
            elif event == 'end':
                self.curDepth -= 1
            else:
                self.logger.error('Problem parsing event: {0}'.format(event))
            if self.curDepth != 0:
                continue
            if not self.dispatchCmd(elem):
                self.logger.error('Problem parsing element {0}'.format(elem.tag))

    @PyQt5.QtCore.pyqtSlot(PyQt5.QtNetwork.QAbstractSocket.SocketError)
    def handleError(self, socketError):
        if not self.isConnected:
            return
        self.logger.warning('INDI client connection fault, error: {0}'.format(socketError))
        self.socket.close()

    def sendString(self, s):
        if self.socket:
            self.socket.write(s.encode(encoding='ascii'))

    def send_one_blob(self, blob_name, blob_format, blobdata):
        if not blobdata:
            blobdata = b''
        b64blob = base64.encodebytes(blobdata)
        if not blob_format:
            blob_format = ''
        self.sendString("  <oneBLOB\n")
        self.sendString("    name='" + blob_name + "'\n")
        self.sendString("    size='" + str(len(blobdata)) + "'\n")
        self.sendString("    enclen='" + str(len(b64blob)) + "'\n")
        self.sendString("    format='" + blob_format + "'>\n")
        if self.socket:
            self.socket.write(b64blob)
        self.sendString("  </oneBLOB>\n")

    def clear(self):
        for d in self.devices:
            del (self.devices[d])
        self.devices = dict()
        for d in self.blob_modes:
            del (self.blob_modes[d])
        self.blob_modes = dict()

    def getDevice(self, deviceName):
        return self.devices.get(deviceName, None)

    def getDevices(self, deviceList, driverInterface):
        for dname, device in self.devices:
            if device.getDriverInterface() | driverInterface:
                deviceList.append(device)
        return len(deviceList) > 0

    def messageCmd(self, elem):
        if elem.tag == 'message':
            device_name = elem.get('device')
            if device_name in self.devices:
                return self.devices[device_name].check_message(elem)
            # Universal message
            message = elem.get('message')
            if message == '':
                return True
            timestamp = elem.get('timestamp')
            if not timestamp or timestamp == '':
                timestamp = time.strftime('%Y-%m-%dT%H:%M:%S')
            if self.mediator:
                self.mediator.new_universal_message(timestamp + ': ' + message)
            else:
                self.logger.info(timestamp + ': ' + message)
        return True

    def delDevice(self, device):
        if not device or not device.name or device.name not in self.devices:
            self.logger.info('delDevice: device not found')
            return INDI.INDI_ERROR_TYPE.INDI_DEVICE_NOT_FOUND
        self.mediator.remove_device(device)
        self.logger.info('Deleting device ' + device.name)
        del (self.device[device.name])

    def delProperty(self, elem):
        device_name = elem.get('device')
        if not device_name or device_name == '' or device_name not in self.devices:
            self.logger.info('delProperty: device not found')
            return INDI.INDI_ERROR_TYPE.INDI_DEVICE_NOT_FOUND
        device = self.devices[device_name]
        device.check_message(elem)
        prop_name = elem.get('name')
        if prop_name is not None:
            if prop_name == '' or prop_name not in device.properties:
                self.logger.info('Cannot delete property {0}'.format(prop_name))
                return INDI.INDI_ERROR_TYPE.INDI_PROPERTY_INVALID
            prop = device.properties[prop_name]
            self.mediator.remove_property(prop)
            # self.logger.info('Deleting property '+prop.name+' in device '+device.name)
            del (device.properties[prop_name])
            return True
        else:
            return self.delDevice(device)

    def dispatchCmd(self, elem):
        if elem.tag == 'message':
            return self.messageCmd(elem)
        elif elem.tag == 'delProperty':
            return self.delProperty(elem)
        elif elem.tag == 'getProperties' or elem.tag[:3] == 'new':
            return True
        device_name = elem.get('device')
        if device_name == '':
            self.logger.info('dispatchCmd: device name is empty')
            return False
        if device_name not in self.devices:
            device = BaseDevice()
            device.name = device_name
            device.mediator = self.mediator
            device.logger = self.logger
            self.devices[device_name] = device
            self.mediator.new_device(device)
        else:
            device = self.devices[device_name]
        cmd = elem.tag[:3]
        if cmd == 'def':
            return device.build_prop(elem)
        elif cmd == 'set':
            return device.set_value(elem)
        return False

    def send_string(self, s):
        if self.client_socket:
            self.client_socket.sendall(s.encode(encoding='ascii'))

    def sendNewProperty(self, p):
        self.send_string("<new" + self._prop_tags[
            p.type] + "\n  device='" + p.device.name + "'\n  name='" + p.name + "'>\n")
        for ename, elem in p.vp.items():
            self.send_string(
                "<" + self._elem_tags[p.type] + " name='" + ename + "'>" + str(
                    elem) + "</" + self._elem_tags[p.type] + ">\n")
        self.send_string("</new" + self._prop_tags[p.type] + ">\n")

    def sendNewElem(self, p, e):
        # we need property p to simplify as it is in the parent e.{stnbl}vp member
        self.send_string("<new" + self._prop_tags[
            p.type] + "\n  device='" + p.device.name + "'\n  name='" + p.name + "'>\n")
        self.send_string(
            "<" + self._elem_tags[p.type] + " name='" + e.name + "'>" + str(e) + "</" +
            self._elem_tags[p.type] + ">\n")
        self.send_string("</new" + self._prop_tags[p.type] + ">\n")

    def startBlob(self, device_name, blobv_name, timestamp):
        self.send_string("<newBLOBVector\n")
        self.send_string("  device='" + device_name + "'\n")
        self.send_string("  name='" + blobv_name + "'\n")
        self.send_string("  timestamp='" + timestamp + "'>\n")

    def finish_blob(self):
        self.send_string("</newBLOBVector>\n")

    def send_blob(self, blob):
        self.startBlob(blob.device.name, blob.name, datetime.datetime.now().isoformat())
        for b in blob.vp.values():
            self.send_one_blob(b.name, b.format, b.blob)
        self.finish_blob()

    def find_blob_mode(self, device, prop):
        if type(device) == str and device != "":
            device_name = device
        elif type(device) == str and device == "":
            return None
        else:
            device_name = device.name
        if type(prop) == str:
            prop_name = prop
        elif prop is not None:
            prop_name = prop.name
        else:
            prop_name = ""
        if device_name + prop_name in self.blob_modes:
            return self.blob_modes[device_name + prop_name]
        elif device_name in self.blob_modes:
            return self.blob_modes[device_name]
        else:
            return None

    def getBlobMode(self, device, prop):
        bhandle = INDI.BLOBHandling.B_ALSO
        bmode = self.find_blob_mode(device, prop)
        if bmode:
            bhandle = bmode
        return bhandle

    def setBlobMode(self, blob_handling, device, prop):
        if device is None or device == "":
            return
        bmode = self.find_blob_mode(device, prop)
        if type(device) == str:
            device_name = device
        else:
            device_name = device.name
        if type(prop) == str:
            prop_name = prop
        elif prop is not None:
            prop_name = prop.name
        else:
            prop_name = ""
        if not bmode:
            self.blob_modes[device_name + prop_name] = blob_handling
        else:
            name = device_name + prop_name
            if name in self.blob_modes and blob_handling != self.blob_modes[name]:
                self.blob_modes[name] = blob_handling
            elif not device_name + prop_name in self.blob_modes:
                self.blob_modes[name] = blob_handling
            else:
                return
        if prop_name != "":
            self.send_string(
                "<enableBLOB device='" + device_name + "' name='" + prop_name + "'>" + str(
                    blob_handling.value) + "</enableBLOB>\n")
        else:
            self.send_string("<enableBLOB device='" + device_name + "'>" + str(
                blob_handling.value) + "</enableBLOB>\n")
