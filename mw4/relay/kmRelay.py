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
import re
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
        >>>              )
    """

    __all__ = ['KMRelay',
               ]
    version = '0.1'
    logger = logging.getLogger(__name__)

    # polling cycle for relay box
    CYCLE_POLLING = 1000

    # default port for KMTronic Relay
    DEFAULT_PORT = 80

    # timeout for requests
    TIMEOUT = 0.5

    # signal if correct status received and decoded
    statusReady = PyQt5.QtCore.pyqtSignal()

    def __init__(self,
                 host=None,
                 ):
        super().__init__()

        self.host = host
        self._user = None
        self._password = None
        self.status = [0]*8

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

    def geturl(self, url):
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
        else:
            result = result.content.decode()
        return result

    def cyclePolling(self):
        result = self.geturl('/status.xml')
        if result is None:
            return
        lines = result.splitlines()
        for line in lines:
            value = re.findall(r'\d', line)
            if not value:
                continue
            value = [int(s) for s in value]
            self.status[value[0]-1] = value[1]
        self.statusReady.emit()

    def pulse(self, relayNumber):
        try:
            self.geturl('/FF0{0:1d}01'.format(relayNumber))
            time.sleep(1)
            self.geturl('/FF0{0:1d}00'.format(relayNumber))
        except Exception as e:
            self.logger.error('Relay:{0}, error:{1}'.format(relayNumber, e))
        finally:
            pass

    def switch(self, relayNumber):
        try:
            self.geturl('/relays.cgi?relay={0:1d}'.format(relayNumber))
        except Exception as e:
            self.logger.error('Relay:{0}, error:{1}'.format(relayNumber, e))
        finally:
            pass
