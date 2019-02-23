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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
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

    version = '0.1'
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
        self.user = user
        self.password = password
        self.status = [0] * 8

        self.timer = PyQt5.QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.cyclePolling)

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

        :return: nothing
        """
        self.timer.start(self.CYCLE_POLLING)

    def stopTimers(self):
        """
        stopTimers disables the cyclic timers for polling necessary relay data.

        :return: nothing
        """
        self.timer.stop()

    def getRelay(self, url):
        """
        getRelay sets and reads data from the given host ip using the given
        user and password

        :param url: web address of relay box
        :return: result: return values from web interface of box
        """

        if self._host is None:
            return None
        auth = requests.auth.HTTPBasicAuth(self._user,
                                           self._password)
        url = 'http://' + self._host[0] + ':' + str(self._host[1]) + url
        try:
            result = requests.get(url, auth=auth, timeout=self.TIMEOUT)
        except requests.exceptions.Timeout:
            return None
        except Exception as e:
            self.logger.error('Error in request: {0}'.format(e))
            return None
        return result.text

    def cyclePolling(self):
        """
        cyclePolling reads the status of the relay status of each single relay.
        with success the statusReady single is sent.

        :return: nothing
        """
        result = self.getRelay('/status.xml')
        if result is None:
            return
        lines = result.splitlines()
        for line in lines:
            value = re.findall(r'\d', line)
            if not value:
                continue
            value = [int(s) for s in value]
            self.status[value[0] - 1] = value[1]
        self.statusReady.emit()
        return True

    def pulse(self, relayNumber):
        """
        pulse switches a relay on for one second and off back.

        :param relayNumber: number of relay to be pulsed, counting from 0 onwards
        :return: nothing
        """

        value1 = self.getRelay('/FF0{0:1d}01'.format(relayNumber + 1))
        time.sleep(self.PULSEWIDTH)
        value2 = self.getRelay('/FF0{0:1d}00'.format(relayNumber + 1))
        if value1 is None or value2 is None:
            self.logger.error('Relay:{0}'.format(relayNumber))
            return False
        else:
            if value1.startswith('401 Unauthorized:'):
                self.logger.error('Relay:{0} unauthorized'.format(relayNumber))
                return False
            else:
                return True

    def switch(self, relayNumber):
        """
        switch toggles the relay stat (on, off)

        :param relayNumber: number of relay to be pulsed, counting from 0 onwards
        :return: nothing
        """

        value = self.getRelay('/relays.cgi?relay={0:1d}'.format(relayNumber + 1))
        if value is None:
            self.logger.error('Relay:{0}'.format(relayNumber))
            return False
        else:
            if value.startswith('401 Unauthorized:'):
                self.logger.error('Relay:{0} unauthorized'.format(relayNumber))
                return False
            else:
                return True

    def set(self, relayNumber, value):
        """
        set toggles the relay stat to the desired value (on, off)

        :param relayNumber: number of relay to be pulsed, counting from 0 onwards
        :param value: relay state.
        :return: nothing
        """

        if value:
            outputFormat = '/FF0{0:1d}01'
        else:
            outputFormat = '/FF0{0:1d}00'
        value = self.getRelay(outputFormat.format(relayNumber + 1))
        if value is None:
            self.logger.error('Relay:{0}'.format(relayNumber))
            return False
        else:
            if value.startswith('401 Unauthorized:'):
                self.logger.error('Relay:{0} unauthorized'.format(relayNumber))
                return False
            else:
                return True
