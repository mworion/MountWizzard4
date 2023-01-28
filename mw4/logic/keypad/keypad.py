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

# external packages
import websocket
import numpy as np

# local imports


class KeyPad:
    """
    """
    __all__ = ['KeyPad']
    log = logging.getLogger(__name__)

    keyCodesA = {
        48: 82,
        49: 92,
        50: 94,
        51: 98,
        52: 32,
        53: 34,
        54: 38,
        55: 22,
        56: 24,
        57: 28,
        27: 84,
        13: 106,
        114: 96,
        113: 88,
        187: 36,
        189: 46,
        38: 11,
        37: 14,
        40: 12,
        39: 18,
        8: 118
    }

    keyCodesB = {
        'a': 13,
        'b': 15,
        'c': 16,
        'd': 17,
        'e': 19,
        'f': 20,
        'g': 21,
        'h': 23,
        'i': 25,
        'j': 26,
        'k': 27,
        'l': 29,
        'm': 30,
        'n': 31,
        'o': 33,
        'p': 35,
        'q': 37,
        'r': 39,
        's': 40,
        't': 41,
        'u': 43,
        'v': 45,
        'w': 47,
        'x': 50,
        'y': 51,
        'z': 52,
        ' ': 53,
        'A': 54,
        'B': 55,
        'C': 57,
        'D': 58,
        'E': 59,
        'F': 60,
        'G': 61,
        'H': 62,
        'I': 63,
        'J': 64,
        'K': 65,
        'L': 66,
        'M': 67,
        'N': 68,
        'O': 69,
        'P': 70,
        'Q': 71,
        'R': 72,
        'S': 73,
        'T': 74,
        'U': 75,
        'V': 76,
        'W': 77,
        'X': 78,
        'Y': 79,
        'Z': 80,
        '.': 81,
        ',': 83,
        ';': 85,
        ':': 86,
        '_': 87,
        '(': 89,
        ')': 90,
        '"': 91,
        "'": 93,
        # '"': 95, is in the javascript, but duplicate
        '/': 97,
        '|': 99,
        '\\': 100,
        '%': 101,
        '&': 103,
        '@': 105,
        '=': 107,
        '?': 109,
        '[': 110,
        ']': 111,
        '<': 112,
        '>': 113,
        '0': 82,
        '1': 92,
        '2': 94,
        '3': 98,
        '4': 32,
        '5': 34,
        '6': 38,
        '7': 22,
        '8': 24,
        '9': 28,
        '\x1b': 84,
        '\r': 106,
        '+': 36,
        '-': 46,
    }

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
        self.signals.keyUp.connect(self.keyUp)
        self.signals.keyDown.connect(self.keyDown)
        self.signals.mousePressed.connect(self.mousePressed)
        self.signals.mouseReleased.connect(self.mouseReleased)

    @staticmethod
    def expand7to8(value, fill=False):
        """
        :param value:
        :param fill:
        :return:
        """
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
        """
        :param inChar:
        :return:
        """
        if inChar in self.charTrans:
            outChar = self.charTrans[inChar]
        else:
            outChar = inChar
        return outChar

    def dispText(self, value):
        """
        :param value:
        :return:
        """
        row = np.zeros(16, dtype=np.uint8)
        for i in range(value[3]):
            if value[4 + i] != 0:
                row[value[1] + i - 1] = self.convertChar(value[4 + i])
        text = ''.join([chr(x) for x in row])
        self.signals.textRow.emit(value[2] - 1, text)
        return True

    def drawPixel(self, value):
        """
        :param value:
        :return:
        """
        imaArr = np.zeros([8, 8, 3], dtype=np.uint8)
        for i in range(8):
            for j in range(8):
                flag = (value[3 + j] & 128 >> i) != 0
                if flag:
                    imaArr[i, j] = [255, 255, 255]
                else:
                    imaArr[i, j] = [0, 0, 0]
        self.signals.imgChunk.emit(imaArr,
                                   8 * (value[2] - 1),
                                   8 * (value[1] - 1))
        return True

    def deletePixel(self, value):
        """
        :param value:
        :return:
        """
        imaArr = np.zeros([8, 12, 3], dtype=np.uint8)
        for i in range(12):
            for j in range(8):
                flag = (value[3 + i] & 1 << j) != 0
                if flag:
                    imaArr[j, i] = [255, 255, 255]
                else:
                    imaArr[j, i] = [0, 0, 0]
        self.signals.imgChunk.emit(imaArr,
                                   8 * (value[2] - 1),
                                   12 * (value[1] - 1))
        return True

    def dispatch(self, value):
        """
        :param value:
        :return:
        """
        value = self.expand7to8(value, False)
        if len(value) <= 0:
            return False
        if value[0] == 1:
            self.dispText(value)
        elif value[0] == 2:
            self.drawPixel(value)
        elif value[0] == 3:
            self.deletePixel(value)
        elif value[0] == 5:
            # setting cursor position
            self.signals.cursorPos.emit(value[2] - 1, value[1] - 1)
        elif value[0] == 6:
            self.signals.clearCursor.emit()
        elif value[0] == 11:
            pass
            # print('select 11')
        elif value[0] == 12:
            pass
            # print('select 12')
        return True

    def checkDispatch(self, value):
        """
        :param value:
        :return:
        """
        if value[0] == 0:
            self.dispatch(value[1:])
        return True

    @staticmethod
    def calcChecksum(value):
        """
        :param value:
        :return:
        """
        checksum = 0
        for i in range(len(value)):
            checksum = checksum ^ value[i]
        if checksum < 10:
            checksum = checksum + 10
        return checksum

    def mousePressed(self, key):
        """
        :param key:
        :return:
        """
        key = self.buttonCodes.get(key, None)
        if key is None:
            return False

        message = [2, 6, key]
        message = message + [self.calcChecksum(message)]
        message = message + [3]
        self.ws.send(message, websocket.ABNF.OPCODE_BINARY)
        return True

    def mouseReleased(self, key):
        """
        :param key:
        :return:
        """
        key = self.buttonCodes.get(key, None)
        if key is None:
            return False

        message = [2, 5, key]
        message = message + [self.calcChecksum(message)]
        message = message + [3]
        self.ws.send(message, websocket.ABNF.OPCODE_BINARY)
        return True

    def keyDown(self, key):
        """
        :param key:
        :return:
        """
        key = self.keyCodesA.get(key, None)
        if key is None:
            return False

        message = [2, 6, key]
        message = message + [self.calcChecksum(message)]
        message = message + [3]
        self.ws.send(message, websocket.ABNF.OPCODE_BINARY)
        return True

    def keyUp(self, key):
        """
        :param key:
        :return:
        """
        key = self.keyCodesA.get(key, None)
        if key is None:
            return False

        message = [2, 5, key]
        message = message + [self.calcChecksum(message)]
        message = message + [3]
        self.ws.send(message, websocket.ABNF.OPCODE_BINARY)
        return True

    def keyPressed(self, key):
        """
        :param key:
        :return:
        """
        if key > 255:
            return False

        key = self.keyCodesB.get(chr(key), None)
        if key is None:
            return False

        message = [2, 6, key]
        message = message + [self.calcChecksum(message)]
        message = message + [3]
        self.ws.send(message, websocket.ABNF.OPCODE_BINARY)
        message = [2, 5, key]
        message = message + [self.calcChecksum(message)]
        message = message + [3]
        self.ws.send(message, websocket.ABNF.OPCODE_BINARY)
        return True

    def on_data(self, ws, data, typeOpcode, cont):
        """
        :param ws:
        :param data:
        :param typeOpcode:
        :param cont:
        :return:
        """
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
                        if self.calcChecksum([2] + result[:-1]) == result[-1]:
                            self.checkDispatch(result)
                else:
                    if started:
                        result.append(data[i])
        return True

    def on_close(self, ws, close_status_code, close_msg):
        """
        :param ws:
        :param close_status_code:
        :param close_msg:
        :return:
        """
        self.ws = None
        return True

    def workerWebsocket(self, host=None):
        """
        :param host:
        :return:
        """
        if host is None:
            return False
        if not isinstance(host, tuple):
            return False
        if self.ws is not None:
            return False

        ipaddress = host[0]
        websocket.setdefaulttimeout(3)
        self.ws = websocket.WebSocketApp(f'ws://{ipaddress}:8000/',
                                         on_data=self.on_data,
                                         on_close=self.on_close,
                                         subprotocols=["binary"])
        self.ws.run_forever()
        return True

    def closeWebsocket(self):
        """
        :return:
        """
        if self.ws is not None:
            self.ws.close()
        return True
