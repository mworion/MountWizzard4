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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import re
import time

# external packages
from PyQt5.QtCore import pyqtSignal, QMutex, QTimer
import requests

# local imports
from base.driverDataClass import Signals


class RelaySignals(Signals):
    """
    """
    statusReady = pyqtSignal()


class KMRelay:
    """
    """

    __all__ = ['KMRelay']
    log = logging.getLogger(__name__)

    CYCLE_POLLING = 1000
    DEFAULT_PORT = 80
    TIMEOUT = 0.5
    PULSEWIDTH = 0.5

    def __init__(self):
        super().__init__()
        self.signals = RelaySignals()
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
        self.deviceConnected = False
        self.timerTask = QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.cyclePolling)

    def startCommunication(self):
        """
        :return: success
        """
        if not self.hostaddress:
            return False

        self.deviceConnected = False
        self.timerTask.start(self.CYCLE_POLLING)
        return True

    def stopCommunication(self):
        """
        :return: True for test purpose
        """
        self.timerTask.stop()
        self.deviceConnected = False
        return True

    def debugOutput(self, result=None):
        """
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

        try:
            result = requests.get(url, auth=auth, timeout=self.TIMEOUT)
        except requests.exceptions.Timeout:
            result = None
        except requests.exceptions.ConnectionError:
            result = None
        except Exception as e:
            result = None
            self.log.critical(f'Error in request: {e}')

        if debug:
            self.debugOutput(result=result)

        self.mutexPoll.unlock()
        return result

    def checkConnected(self, value):
        """
        :return: success
        """
        statusNotConnected = value is None or value.reason != 'OK'
        statusConnected = not statusNotConnected
        if self.deviceConnected:
            if statusNotConnected:
                self.signals.deviceDisconnected.emit('KMTronic')
                self.deviceConnected = False
                return False
            else:
                return True
        else:
            if statusConnected:
                self.signals.deviceConnected.emit('KMTronic')
                self.deviceConnected = True
                return True
            else:
                return False

    def cyclePolling(self):
        """
        :return: success
        """
        value = self.getRelay('/status.xml', debug=False)
        if not self.checkConnected(value):
            return False

        lines = value.text.splitlines()
        for line in lines:
            value = re.findall(r'\d', line)
            if not value:
                continue
            value = [int(s) for s in value]
            self.status[value[0] - 1] = value[1]

        self.signals.statusReady.emit()
        return True

    def getByte(self, relayNumber=0, state=False):
        """
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
