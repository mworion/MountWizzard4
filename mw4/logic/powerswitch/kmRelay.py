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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import re
import time

# external packages
from PySide6.QtCore import Signal, QMutex, QTimer
import requests

# local imports
from base.signalsDevices import Signals


class RelaySignals(Signals):
    """ """

    statusReady = Signal()


class KMRelay:
    """ """

    log = logging.getLogger("MW4")

    CYCLE_POLLING = 1000
    DEFAULT_PORT = 80
    TIMEOUT = 0.5
    PULSEWIDTH = 0.5

    def __init__(self):
        super().__init__()
        self.signals = RelaySignals()
        self.framework = ""
        self.data = {}
        self.defaultConfig = {
            "framework": "",
            "frameworks": {
                "relay": {
                    "deviceName": "KMRelay",
                    "hostaddress": "",
                    "user": "",
                    "password": "",
                }
            },
        }
        self.run = {"relay": self}

        self.mutexPoll = QMutex()
        self.deviceName = ""
        self.hostaddress = ""
        self.user = ""
        self.password = ""
        self.status = [0] * 8
        self.deviceConnected = False
        self.timerTask = QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.cyclePolling)

    def startCommunication(self) -> None:
        """ """
        if not self.hostaddress:
            return

        self.deviceConnected = False
        self.timerTask.start(self.CYCLE_POLLING)

    def stopCommunication(self) -> None:
        """ """
        self.timerTask.stop()
        self.deviceConnected = False

    def debugOutput(self, result: object) -> None:
        """ """
        if not result:
            self.log.info("No valid result")
            return

        text = result.text.replace("\r\n", ", ")
        reason = result.reason
        status = result.status_code
        url = result.url
        elapsed = result.elapsed
        self.log.trace(f"Result: {url}, {reason}, {status}, {elapsed}, {text}")

    def getRelay(self, url: str, debug: bool) -> str:
        """ """
        if self.hostaddress is None:
            return ""
        if not self.mutexPoll.tryLock():
            return ""

        auth = requests.auth.HTTPBasicAuth(self.user, self.password)
        url = f"http://{self.hostaddress}:80{url}"

        try:
            result = requests.get(url, auth=auth, timeout=self.TIMEOUT)
        except Exception as e:
            result = ""
            self.log.critical(f"Error in request: {e}")

        if debug:
            self.debugOutput(result=result)

        self.mutexPoll.unlock()
        return result

    def checkConnected(self, value: object) -> bool:
        """
        :return: success
        """
        statusNotConnected = value is None or value.reason != "OK"
        statusConnected = not statusNotConnected
        if self.deviceConnected:
            if statusNotConnected:
                self.signals.deviceDisconnected.emit("KMTronic")
                self.deviceConnected = False
                return False
            else:
                return True
        else:
            if statusConnected:
                self.signals.deviceConnected.emit("KMTronic")
                self.deviceConnected = True
                return True
            else:
                return False

    def cyclePolling(self) -> None:
        """ """
        value = self.getRelay("/status.xml", debug=False)
        if not self.checkConnected(value):
            return

        lines = value.text.splitlines()
        for line in lines:
            value = re.findall(r"\d", line)
            if not value:
                continue
            value = [int(s) for s in value]
            self.status[value[0] - 1] = value[1]

        self.signals.statusReady.emit()

    def getByte(self, relayNumber: int, state: bool) -> bool:
        """ """
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

    def pulse(self, relayNumber: int) -> None:
        """ """
        self.log.debug(f"Pulse relay:{relayNumber}")
        byteOn = self.getByte(relayNumber=relayNumber, state=True)
        byteOff = self.getByte(relayNumber=relayNumber, state=False)
        value1 = self.getRelay(f"/FFE0{byteOn:02X}")
        time.sleep(self.PULSEWIDTH)
        value2 = self.getRelay(f"/FFE0{byteOff:02X}")

        if value1 is None or value2 is None:
            self.log.warning(f"Relay:{relayNumber}")
            return
        elif value1.reason != "OK" or value2.reason != "OK":
            self.log.warning(f"Relay:{relayNumber}")
            return

    def switch(self, relayNumber: int) -> None:
        """ """
        self.log.debug(f"Switch relay:{relayNumber}")
        value = self.getRelay("/relays.cgi?relay={0:1d}".format(relayNumber + 1))
        if value is None:
            self.log.warning(f"Relay:{relayNumber}")
            return
        elif value.reason != "OK":
            self.log.warning(f"Relay:{relayNumber}")
            return

    def set(self, relayNumber: int, value: bool) -> None:
        """ """
        self.log.debug(f"Set relay:{relayNumber}")
        byteOn = self.getByte(relayNumber=relayNumber, state=value)
        value = self.getRelay(f"/FFE0{byteOn:02X}")
        if value is None or value.reason != "OK":
            self.log.warning(f"Relay:{relayNumber}")
