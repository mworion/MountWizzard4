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
import re
import time

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QMutex
from PyQt5.QtCore import QTimer
import requests

# local imports


class RelaySignals(QObject):
    """
    The RelaySignals class offers a list of signals to be used and instantiated by
    the Relay class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Relay class itself is subclassed from object
    """

    __all__ = ['RelaySignals']

    statusReady = pyqtSignal()

    serverConnected = pyqtSignal()
    serverDisconnected = pyqtSignal(object)
    deviceConnected = pyqtSignal(str)
    deviceDisconnected = pyqtSignal(str)


class KMRelay(QObject):
    """
    The class KMRelay inherits all information and handling of KMtronic relay board
    attributes of the connected board and provides the abstracted interface.

        >>> relay = KMRelay()

    """

    __all__ = ['KMRelay',
               ]

    log = logging.getLogger(__name__)

    # polling cycle for relay box
    CYCLE_POLLING = 1000
    # default port for KMTronic Relay
    DEFAULT_PORT = 80
    # timeout for requests
    TIMEOUT = 0.5
    # width for pulse
    PULSEWIDTH = 0.5

    def __init__(self):
        super().__init__()

        self.signals = RelaySignals()
        # minimum set for driver package built in
        self.framework = ''
        self.data = {}
        self.defaultConfig = {
            'framework': '',
            'frameworks': {
                'relay': {
                    'deviceName': 'KMRelay',
                    'hostaddress': '',
                    'user': '',
                    'password': '',
                }
            }
        }
        self.run = {
            'relay': self
        }

        self.mutexPoll = QMutex()
        self.deviceName = ''
        self.hostaddress = ''
        self.user = ''
        self.password = ''
        self.status = [0] * 8

        self.timerTask = QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.cyclePolling)

    def startCommunication(self, loadConfig=False):
        """
        startCommunication enables the cyclic timers for polling necessary relay data.

        :param loadConfig:
        :return: success
        """
        if not self.hostaddress:
            return False

        self.timerTask.start(self.CYCLE_POLLING)
        # self.signals.deviceConnected.emit('KMTronic')

        return True

    def stopCommunication(self):
        """
        stopCommunication disables the cyclic timers for polling necessary relay data.

        :return: True for test purpose
        """
        self.timerTask.stop()
        self.signals.deviceDisconnected.emit('KMTronic')

        return True

    def debugOutput(self, result=None):
        """
        debugOutput writes a nicely formed output for diagnosis in relay environment

        :param result: value from requests get commend
        :return: True for test purpose
        """

        if result is None:
            self.log.info('No valid result')
            return False

        text = result.text.replace('\r\n', ', ')
        reason = result.reason
        status = result.status_code
        url = result.url
        elapsed = result.elapsed

        self.log.trace(f'Result: {url}, {reason}, {status}, {elapsed}, {text}')

        return True

    def getRelay(self, url='/status.xml', debug=True):
        """
        getRelay sets and reads data from the given host ip using the given
        user and password

        :param url: web address of relay box
        :param debug: write extended debug output
        :return: result: return values from web interface of box
        """

        if self.hostaddress is None:
            return None

        if not self.mutexPoll.tryLock():
            return None

        auth = requests.auth.HTTPBasicAuth(self.user, self.password)
        url = f'http://{self.hostaddress}:80{url}'
        result = None

        try:
            result = requests.get(url, auth=auth, timeout=self.TIMEOUT)

        except requests.exceptions.Timeout:
            pass

        except requests.exceptions.ConnectionError:
            pass

        except Exception as e:
            self.log.critical(f'Error in request: {e}')

        if debug:
            self.debugOutput(result=result)

        self.mutexPoll.unlock()
        return result

    def cyclePolling(self):
        """
        cyclePolling reads the status of the relay status of each single relay.
        with success the statusReady single is sent.

        :return: success
        """

        value = self.getRelay('/status.xml', debug=False)

        if value is None:
            return False

        if value.reason != 'OK':
            return False

        lines = value.text.splitlines()

        for line in lines:
            value = re.findall(r'\d', line)
            if not value:
                continue
            value = [int(s) for s in value]
            self.status[value[0] - 1] = value[1]

        self.signals.statusReady.emit()
        self.signals.deviceConnected.emit('KMTronic')

        return True

    def getByte(self, relayNumber=0, state=False):
        """
        getByte generates the right bit mask for setting or resetting the relay mask

        :param relayNumber: relay number
        :param state: state to archive
        :return: bit mask for switching
        """

        byteStat = 0b0
        for i, status in enumerate(self.status):
            if status:
                byteStat = byteStat | 1 << i
        position = 1 << relayNumber
        byteOn = byteStat | position
        byteOff = byteOn & ~position

        if state:
            return byteOn
        else:
            return byteOff

    def pulse(self, relayNumber):
        """
        pulse switches a relay on for one second and off back.

        :param relayNumber: number of relay to be pulsed, counting from 0 onwards
        :return: success
        """

        self.log.debug(f'Pulse relay:{relayNumber}')
        byteOn = self.getByte(relayNumber=relayNumber, state=True)
        byteOff = self.getByte(relayNumber=relayNumber, state=False)
        value1 = self.getRelay(f'/FFE0{byteOn:02X}')
        time.sleep(self.PULSEWIDTH)
        value2 = self.getRelay(f'/FFE0{byteOff:02X}')

        if value1 is None or value2 is None:
            self.log.warning(f'Relay:{relayNumber}')
            return False
        elif value1.reason != 'OK' or value2.reason != 'OK':
            self.log.warning(f'Relay:{relayNumber}')
            return False

        return True

    def switch(self, relayNumber):
        """
        switch toggles the relay status (on, off)

        :param relayNumber: number of relay to be pulsed, counting from 0 onwards
        :return: success
        """

        self.log.debug(f'Switch relay:{relayNumber}')
        value = self.getRelay('/relays.cgi?relay={0:1d}'.format(relayNumber + 1))

        if value is None:
            self.log.warning(f'Relay:{relayNumber}')
            return False
        elif value.reason != 'OK':
            self.log.warning(f'Relay:{relayNumber}')
            return False

        return True

    def set(self, relayNumber, value):
        """
        set toggles the relay status to the desired value (on, off)

        :param relayNumber: number of relay to be pulsed, counting from 0 onwards
        :param value: relay state.
        :return: success
        """

        self.log.debug(f'Set relay:{relayNumber}')
        byteOn = self.getByte(relayNumber=relayNumber, state=value)
        value = self.getRelay(f'/FFE0{byteOn:02X}')

        if value is None:
            self.log.warning(f'Relay:{relayNumber}')
            return False
        elif value.reason != 'OK':
            self.log.warning(f'Relay:{relayNumber}')
            return False

        return True
