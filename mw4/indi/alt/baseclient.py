# Copyright 2017 geehalel@gmail.com
#
# This file is part of npindi.
#
#    npindi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    npindi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with npindi.  If not, see <http://www.gnu.org/licenses/>.

import base64
import datetime

from indi.alt.INDI import INDI
from indi.indibase.basedevice import BaseDevice


class BaseClient:
    _prop_tags={
        INDI.INDI_PROPERTY_TYPE.INDI_TEXT: 'TextVector',
        INDI.INDI_PROPERTY_TYPE.INDI_NUMBER: 'NumberVector',
        INDI.INDI_PROPERTY_TYPE.INDI_SWITCH: 'SwitchVector',
        INDI.INDI_PROPERTY_TYPE.INDI_LIGHT: 'LightVector',
        INDI.INDI_PROPERTY_TYPE.INDI_BLOB: 'BLOBVector'
    }
    _elem_tags={
        INDI.INDI_PROPERTY_TYPE.INDI_TEXT: 'oneText',
        INDI.INDI_PROPERTY_TYPE.INDI_NUMBER: 'oneNumber',
        INDI.INDI_PROPERTY_TYPE.INDI_SWITCH: 'oneSwitch',
        INDI.INDI_PROPERTY_TYPE.INDI_LIGHT: 'oneLight',
        INDI.INDI_PROPERTY_TYPE.INDI_BLOB: 'oneBLOB'
    }

    def clear(self):
        for d in self.devices:
            del(self.devices[d])
        self.devices = dict()
        for d in self.blob_modes:
            del(self.blob_modes[d])
        self.blob_modes = dict()
    def getDevice(self, deviceName):
        return self.devices.get(deviceName, None)
    def getDevices(self, deviceList, driverInterface):
        for dname, device in self.devices:
            if device._getDriverInterface() | driverInterface:
                deviceList.append(device)
        return len(deviceList) > 0
    def message_cmd(self, elem):
        if elem.tag=='message':
            device_name=elem.get('device')
            if device_name in self.devices:
                return self.devices[device_name].checkMessage(elem)
            # Universal message
            message=elem.get('message')
            if message=='':
                return True
            timestamp=elem.get('timestamp')
            if not timestamp or timestamp=='':
                timestamp=time.strftime('%Y-%m-%dT%H:%M:%S')
            if self.mediator:
                self.mediator.new_universal_message(timestamp+': '+message)
            else:
                self.logger.info(timestamp+': '+message)
        return True
    def delete_device(self, device):
        if not device or not device.name or not device.name in self.devices:
            self.logger.warn('delDevice: device not found')
            return INDI.INDI_ERROR_TYPE.INDI_DEVICE_NOT_FOUND
        self.mediator.remove_device(device)
        self.logger.info('Deleting device '+device.name)
        del(self.device[device.name])
    def del_property_cmd(self, elem):
        device_name=elem.get('device')
        if not device_name or device_name=='' or not device_name in self.devices:
            self.logger.warn('delProperty: device not found')
            return INDI.INDI_ERROR_TYPE.INDI_DEVICE_NOT_FOUND
        device=self.devices[device_name]
        device.checkMessage(elem)
        prop_name=elem.get('name')
        if not prop_name is None:
            if prop_name=='' or not prop_name in device.properties:
                self.logger.warn('Can not delete property \''+prop_name+'\' as it is not defined yet. Check driver.')
                return INDI.INDI_ERROR_TYPE.INDI_PROPERTY_INVALID
            prop=device.properties[prop_name]
            self.mediator.remove_property(prop)
            #self.logger.info('Deleting property '+prop.name+' in device '+device.name)
            del(device.properties[prop_name])
            return True
        else:
            return self.delete_device(device)
        return True
    def dispatch_command(self, elem):
        if elem.tag=='message':
            return self.message_cmd(elem)
        elif elem.tag=='delProperty':
            return self.del_property_cmd(elem)
        elif elem.tag=='getProperties' or elem.tag[:3]=='new':
            return True
        device_name=elem.get('device')
        if device_name=='':
            self.logger.warn('_dispatchCmd: device name is empty')
            return False
        if not device_name in self.devices:
            device=BaseDevice()
            device.name=device_name
            device.mediator=self.mediator
            device.logger=self.logger
            self.devices[device_name]=device
            self.mediator.new_device(device)
        else:
            device=self.devices[device_name]
        cmd=elem.tag[:3]
        if cmd == 'def':
            return device.buildProp(elem)
        elif cmd == 'set':
            return device.setValue(elem)
        return False
    def send_string(self, s):
        if self.client_socket:
            self.client_socket.sendall(s.encode(encoding='ascii'))
    def send_new_property(self, p):
        self.send_string("<new"+BaseClient._prop_tags[p.type]+"\n  device='"+p.device.name+"'\n  name='"+p.name+"'>\n")
        for ename, elem in p.vp.items():
            self.send_string("<"+BaseClient._elem_tags[p.type]+" name='"+ename+"'>"+str(elem)+"</"+BaseClient._elem_tags[p.type]+">\n")
        self.send_string("</new"+BaseClient._prop_tags[p.type]+">\n")
    def send_new_elem(self, p, e): # we need porperty p to simplify as it is in the parent e.{stnbl}vp member
        self.send_string("<new"+BaseClient._prop_tags[p.type]+"\n  device='"+p.device.name+"'\n  name='"+p.name+"'>\n")
        self.send_string("<"+BaseClient._elem_tags[p.type]+" name='"+e.name+"'>"+str(e)+"</"+BaseClient._elem_tags[p.type]+">\n")
        self.send_string("</new"+BaseClient._prop_tags[p.type]+">\n")
    def start_blob(self, device_name, blobv_name, timestamp):
        self.send_string("<newBLOBVector\n")
        self.send_string("  device='"+device_name+"'\n")
        self.send_string("  name='"+blobv_name+"'\n")
        self.send_string("  timestamp='"+timestamp+"'>\n")
    def finish_blob(self):
        self.send_string("</newBLOBVector>\n")
    def send_one_blob(self, blob_name, blob_format, blobdata):
        if not blobdata:
            blobdata = b''
        b64blob=base64.encodebytes(blobdata)
        if not blob_format:
            blob_format = ''
        self.send_string("  <oneBLOB\n")
        self.send_string("    name='"+blob_name+"'\n")
        self.send_string("    size='"+str(len(blobdata))+"'\n")
        self.send_string("    enclen='"+str(len(b64blob))+"'\n")
        self.send_string("    format='"+blob_format+"'>\n")
        if self.client_socket:
            self.client_socket.sendall(b64blob)
        self.send_string("  </oneBLOB>\n")
    def send_blob(self, blob):
        self.start_blob(blob.device.name, blob.name, datetime.datetime.now().isoformat())
        for b in blob.vp.values():
            self.send_one_blob(b.name, b.format, b.blob)
        self.finish_blob()
    def find_blob_mode(self, device, prop):
        if type(device)==str and device != "":
            device_name=device
        elif type(device)==str and device == "":
            return None
        else:
            device_name=device.name
        if type(prop)==str:
            prop_name=prop
        elif prop is not None:
            prop_name=prop.name
        else:
            prop_name=""
        if device_name+prop_name in self.blob_modes:
            return self.blob_modes[device_name+prop_name]
        elif device_name in self.blob_modes:
            return self.blob_modes[device_name]
        else:
            return None
    def get_blob_mode(self, device, prop):
        bhandle=INDI.BLOBHandling.B_ALSO
        bmode=self.find_blob_mode(device, prop)
        if bmode: bhandle = bmode
        return bhandle
    def set_blob_mode(self, blob_handling, device, prop):
        if device is None or device == "": return
        bmode=self.find_blob_mode(device, prop)
        if type(device)==str:
            device_name=device
        else:
            device_name=device.name
        if type(prop)==str:
            prop_name=prop
        elif prop is not None:
            prop_name=prop.name
        else:
            prop_name=""
        if not bmode:
            self.blob_modes[device_name+prop_name]=blob_handling
        else:
            if device_name+prop_name in self.blob_modes and blob_handling != self.blob_modes[device_name+prop_name]:
                self.blob_modes[device_name+prop_name]=blob_handling
            elif not device_name+prop_name in self.blob_modes:
                self.blob_modes[device_name+prop_name]=blob_handling
            else:
                return
        if prop_name != "":
            self.send_string("<enableBLOB device='"+device_name+"' name='"+prop_name+"'>"+str(blob_handling.value)+"</enableBLOB>\n")
        else:
            self.send_string("<enableBLOB device='"+device_name+"'>"+str(blob_handling.value)+"</enableBLOB>\n")

     def set_driver_connection(self, status, device_name):
        if not device_name or device_name=='' or not device_name in self.devices:
            self.logger.warn('setDriverConnection: device not found')
            return INDI.INDI_ERROR_TYPE.INDI_DEVICE_NOT_FOUND
        device=self.devices[device_name]
        if not INDI.SP.CONNECTION in device.properties: return False
        prop_connection=device.properties[INDI.SP.CONNECTION]
        if status:
            if prop_connection.vp['CONNECT'].s == INDI.ISState.ISS_ON: return True
            prop_connection.s = INDI.IPState.IPS_BUSY
            prop_connection.vp['CONNECT'].s = INDI.ISState.ISS_ON
            prop_connection.vp['DISCONNECT'].s = INDI.ISState.ISS_OFF
            self.send_new_property(prop_connection)
            return True
        else:
            if prop_connection.vp['DISCONNECT'].s == INDI.ISState.ISS_ON: return True
            prop_connection.s = INDI.IPState.IPS_BUSY
            prop_connection.vp['CONNECT'].s = INDI.ISState.ISS_OFF
            prop_connection.vp['DISCONNECT'].s = INDI.ISState.ISS_ON
            self.send_new_property(prop_connection)
            return True
    def connect_device(self, device_name):
        return self.set_driver_connection(True, device_name)
    def disconnect_device(self, device_name):
        return self.set_driver_connection(False, device_name)
