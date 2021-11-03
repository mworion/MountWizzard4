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
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
from websocket import ABNF, WebSocketApp
import numpy as np

# local imports


class KeyPad:
    """
    """
    __all__ = ['KeyPad']
    log = logging.getLogger(__name__)

    buttonCodes = {
        'key_0': 82,
        'key_1': 92,
        'key_2': 94,
        'key_3': 98,
        'key_4': 32,
        'key_5': 34,
        'key_6': 38,
        'key_7': 22,
        'key_8': 24,
        'key_9': 28,
        'key_esc': 84,
        'key_enter': 106,
        'key_stop': 96,
        'key_menu': 88,
        'key_plus': 36,
        'key_minus': 46,
        'key_up': 11,
        'key_left': 14,
        'key_down': 12,
        'key_right': 18,
    }
    charTrans = {
        223: 176,
    }

    def __init__(self, signals):
        self.signals = signals
        self.ws = None
        self.signals.keyPressed.connect(self.keyPressed)

    @staticmethod
    def expand7to8(value, fill=False):
        result = []
        n = 0
        o = 0
        for r in range(0, len(value)):
            n += 7
            o = (value[r] & 127) | (o << 7)
            if n >= 8:
                u = (o >> (n - 8)) & 255
                n -= 8
                result.append(u)
        if fill and n > 0:
            u = (o << (8 - n)) & 255
            result.append(u)
        return result

    def convertChar(self, inChar):
        if inChar in self.charTrans:
            outChar = self.charTrans[inChar]
        else:
            outChar = inChar
        return outChar

    def dispatch(self, value):
        value = self.expand7to8(value, False)
        if len(value) <= 0:
            return
        if value[0] == 1:
            row = np.zeros(16, dtype=np.uint8)
            for i in range(value[3]):
                if value[4 + i] != 0:
                    row[value[1] + i - 1] = self.convertChar(value[4 + i])
            text = ''.join([chr(x) for x in row])
            # print(row, '\n', text)
            self.signals.textRow.emit(value[2] - 1, text)

        elif value[0] == 2:
            imaArr = np.zeros([8, 8, 3], dtype=np.uint8)
            for i in range(8):
                for j in range(8):
                    flag = (value[3 + j] & 128 >> i) != 0
                    if flag:
                        imaArr[i, j] = [255, 255, 255]
                    else:
                        imaArr[i, j] = [0, 0, 0]
            self.signals.imgChunk.emit(imaArr, 8 * (value[i] - 1),
                                       8 * (value[j] - 1))

        elif value[0] == 3:
            imaArr = np.zeros([12, 8, 3], dtype=np.uint8)
            for i in range(12):
                for j in range(8):
                    flag = (value[3 + i] & 1 << j) != 0
                    if flag:
                        imaArr[i, j] = [255, 255, 255]
                    else:
                        imaArr[i, j] = [0, 0, 0]
            self.signals.imgChunk.emit(imaArr, 12 * (value[i] - 1),
                                       8 * (value[j] - 1))

    def checkDispatch(self, value):
        if value[0] == 0:
            self.dispatch(value[1:])

    @staticmethod
    def calcChecksum1(value):
        checksum = 0
        for i in range(len(value)):
            checksum = checksum ^ value[i]
        if checksum < 10:
            checksum = checksum + 10
        return checksum

    @staticmethod
    def xor(a, b):
        return (a and not b) or (not a and b)

    def calcChecksum(self, value):
        checksum = 0
        for i in range(len(value)):
            checksum = self.xor(checksum, value[i])
        if checksum < 10:
            checksum = checksum + 10
        return checksum

    def mousePressed(self, key):
        message = [2, 6, key]
        message = message + [self.calcChecksum1(message)]
        message = message + [3]
        self.ws.send(message, ABNF.OPCODE_BINARY)

    def mouseReleased(self, key):
        message = [2, 5, key]
        message = message + [self.calcChecksum1(message)]
        message = message + [3]
        self.ws.send(message, ABNF.OPCODE_BINARY)

    def keyPressed(self, key):
        self.mousePressed(key)
        self.mouseReleased(key)

    def on_data(self, ws, data, typeOpcode, cont):
        result = []
        started = False
        for i in range(len(data)):
            if data[i] == 2:
                result = []
                started = True
            else:
                if data[i] == 3:
                    started = False
                    if len(result) > 1:
                        if self.calcChecksum([2] + result) == result[-1]:
                            self.checkDispatch(result)
                else:
                    if started:
                        result.append(data[i])

    def on_open(self, ws, message):
        self.log.info(message)

    def on_error(self, ws, message):
        self.log.error(message)

    def on_close(self, ws, message):
        self.log.info(message)

    def workerWebsocket(self, host=None):
        if host is None:
            return False
        if not isinstance(host, tuple):
            return False
        ipaddress = host[0]
        self.ws = WebSocketApp(f'ws://{ipaddress}:8000/',
                               on_data=self.on_data,
                               on_open=self.on_open,
                               on_error=self.on_error,
                               on_close=self.on_close,
                               subprotocols=["binary"])
        self.ws.run_forever()

    def closeWebsocket(self):
        if self.ws is not None:
            self.ws.close()
