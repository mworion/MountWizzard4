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

from PyQt5 import QtCore
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket

from indi.alt.INDI import *
from indi.indibase.baseclient import BaseClient

import xml.etree.ElementTree
import logging
import base64
class BaseClientQt(QtCore.QObject, BaseClient):
    def __init__(self, parent=None, host='localhost', port=7624, mediator=None, logger=None):
        QtCore.QObject.__init__(self, parent)
        self.host=host
        self.port=port
        self.timeout=3
        self.is_connected=False
        self.client_socket=QTcpSocket()
        self.client_socket.readyRead.connect(self.listenINDI)
        self.client_socket.error.connect(self.processSocketError)
        self.parser=xml.etree.ElementTree.XMLPullParser(['start', 'end'])
        self.parser.feed('<fakeindiroot>')
        for event, elem in self.parser.read_events():
            pass
        self.current_chunk=[]
        self.current_depth=0

        self.devices=dict()
        self.blob_modes=dict()
        if not logger:
            self.logger=logging.getLogger('baseclientqt')
        else:
            self.logger=logger
        if not mediator:
            self.mediator=BaseMediator(self.logger)
        else:
            self.mediator=mediator
    def connect(self):
        if self.is_connected:
            return True
        self.client_socket.connectToHost(self.host.decode(), self.port)
        if not self.client_socket.waitForConnected(self.timeout * 1000):
            self.is_connected = False
            return False
        self.is_connected=True
        self.mediator.server_connected()
        self.client_socket.write(b'<getProperties version="'+INDI.INDIV+b'"/>')
        return True
    def disconnect(self):
        if not self.is_connected:
            return True
        self.client_socket.close()
        self.is_connected=False
        self.devices.clear()
        self.mediator.server_disconnected(0)
        return True
    @QtCore.pyqtSlot()
    def listenINDI(self):
        buf = self.client_socket.readAll()
        self.parser.feed(buf)
        for event, elem in self.parser.read_events():
            #print(event, elem.tag, elem.keys())
            if event=='start':
                self.current_depth+=1
            elif event=='end':
                self.current_depth-=1
            else:
                self.logger.error('Parser: unknown event')
            if self.current_depth==0:
                #print('Parsed a', elem.tag,'element')
                if not self.dispatch_command(elem):
                    self.logger.error('Parser: dispatchCmd failed for element '+ elem.tag)
    @QtCore.pyqtSlot(QAbstractSocket.SocketError)
    def processSocketError(self, SocketError):
        if not self.is_connected:
            return
        self.logger.error('INDI Server %s/%d disconnected.' % (self.host, self.port))
        self.client_socket.close()
        self.mediator.server_disconnected(-1)
    def send_string(self, s):
        if self.client_socket:
            self.client_socket.write(s.encode(encoding='ascii'))
    def send_one_blob(self, blob_name, blob_format, blobdata):
        if  not blobdata:
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
            self.client_socket.write(b64blob)
        self.send_string("  </oneBLOB>\n")
