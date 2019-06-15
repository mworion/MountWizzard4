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
# Python  v3.7.3
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import re
import time
# external packages
import PyQt5
import requests
# local imports


class KMRelay(PyQt5.QtCore.QObject):
    """
    The class KMRelay inherits all information and handling of KMtronic relay board
    attributes of the connected board and provides the abstracted interface.

        >>> fw = KMRelay(
        >>>                 host=host
        >>>                 user=user
        >>>                 password=password
        >>>              )
    """

    __all__ = ['KMRelay',
               'startTimers',
               'stopTimers',
               'cyclePolling',
               'pulse',
               'switch',
               'set',
               ]

    version = '0.5'
    logger = logging.getLogger(__name__)

    # polling cycle for relay box
    CYCLE_POLLING = 1000
    # default port for KMTronic Relay
    DEFAULT_PORT = 80
    # timeout for requests
    TIMEOUT = 0.5
    # width for pulse
    PULSEWIDTH = 0.5
    # signal if correct status received and decoded
    statusReady = PyQt5.QtCore.pyqtSignal()

    def __init__(self,
                 host=None,
                 user=None,
                 password=None,
                 ):
        super().__init__()

        self.host = host
        self.mutexPoll = PyQt5.QtCore.QMutex()
        self.user = user
        self.password = password
        self.status = [0] * 8

        self.timerTask = PyQt5.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.cyclePolling)

    @property
    def host(self):
        return self._host

    def checkFormat(self, value):
        # checking format
        if not value:
            self.logger.error(f'Wrong host value: {value}')
            return None
        if not isinstance(value, (tuple, str)):
            self.logger.error(f'Wrong host value: {value}')
            return None
        # now we got the right format
        if isinstance(value, str):
            value = (value, self.DEFAULT_PORT)
        return value

    @host.setter
    def host(self, value):
        value = self.checkFormat(value)
        self._host = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    def startTimers(self):
        """
        startTimers enables the cyclic timers for polling necessary relay data.

        :return: success
        """

        if self._host is None:
            return False
        if not self._host[0]:
            return False
        if not self._host[1]:
            return False

        self.timerTask.start(self.CYCLE_POLLING)

        return True

    def stopTimers(self):
        """
        stopTimers disables the cyclic timers for polling necessary relay data.

        :return: success
        """

        self.timerTask.stop()

        return True

    def _debugOutput(self, result=None):
        """
        _debugOutput writes a nicely formed output for diagnosis in relay environment

        :param result: value from requests get commend
        :return: True fir test purpose
        """

        if result is None:
            self.logger.debug('No valid result')
            return False

        text = result.text.replace('\r\n', ', ')
        reason = result.reason
        status = result.status_code
        url = result.url
        code = result.apparent_encoding
        elapsed = result.elapsed

        self.logger.debug(f'Result: {url}, {reason}, {status}, {code}, {elapsed}, {text}')

        return True

    def getRelay(self, url='/status.xml', debug=True):
        """
        getRelay sets and reads data from the given host ip using the given
        user and password

        :param url: web address of relay box
        :param debug: write extended debug output
        :return: result: return values from web interface of box
        """

        if self._host is None:
            return None

        if not self.mutexPoll.tryLock():
            return None

        auth = requests.auth.HTTPBasicAuth(self._user,
                                           self._password,
                                           )
        url = f'http://{self._host[0]}:{self._host[1]}{url}'
        result = None

        try:
            result = requests.get(url, auth=auth, timeout=self.TIMEOUT)
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except Exception as e:
            self.logger.error(f'Error in request: {e}')

        if debug:
            self._debugOutput(result=result)

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
            self.logger.error('Polling error')
            return False
        if value.reason != 'OK':
            self.logger.error('Polling error')
            return False

        lines = value.text.splitlines()
        for line in lines:
            value = re.findall(r'\d', line)
            if not value:
                continue
            value = [int(s) for s in value]
            self.status[value[0] - 1] = value[1]

        self.statusReady.emit()
        return True

    def _getByte(self, relayNumber=0, state=False):
        """
        _getByte generates the right bit mask for setting or resetting the relay mask

        :param number: relay number
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

        self.logger.info(f'Pulse relay:{relayNumber}')
        byteOn = self._getByte(relayNumber=relayNumber, state=True)
        byteOff = self._getByte(relayNumber=relayNumber, state=False)
        value1 = self.getRelay(f'/FFE0{byteOn:02X}')
        time.sleep(self.PULSEWIDTH)
        value2 = self.getRelay(f'/FFE0{byteOff:02X}')

        if value1 is None or value2 is None:
            self.logger.error(f'Relay:{relayNumber}')
            return False
        elif value1.reason != 'OK' or value2.reason != 'OK':
            self.logger.error(f'Relay:{relayNumber}')
            return False

        return True

    def switch(self, relayNumber):
        """
        switch toggles the relay status (on, off)

        :param relayNumber: number of relay to be pulsed, counting from 0 onwards
        :return: success
        """

        self.logger.info(f'Switch relay:{relayNumber}')
        value = self.getRelay('/relays.cgi?relay={0:1d}'.format(relayNumber + 1))

        if value is None:
            self.logger.error(f'Relay:{relayNumber}')
            return False
        elif value.reason != 'OK':
            self.logger.error(f'Relay:{relayNumber}')
            return False

        return True

    def set(self, relayNumber, value):
        """
        set toggles the relay status to the desired value (on, off)

        :param relayNumber: number of relay to be pulsed, counting from 0 onwards
        :param value: relay state.
        :return: success
        """

        self.logger.info(f'Set relay:{relayNumber}')
        byteOn = self._getByte(relayNumber=relayNumber, state=value)
        value = self.getRelay(f'/FFE0{byteOn:02X}')

        if value is None:
            self.logger.error(f'Relay:{relayNumber}')
            return False
        elif value.reason != 'OK':
            self.logger.error(f'Relay:{relayNumber}')
            return False

        return True
