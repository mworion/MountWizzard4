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
import websocket
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

    def dispatch(self, value):
        """
        :param value:
        :return:
        """
        value = self.expand7to8(value, False)
        if len(value) <= 0:
            return False

        if value[0] == 1:
            # writing text in rows
            row = np.zeros(16, dtype=np.uint8)
            for i in range(value[3]):
                if value[4 + i] != 0:
                    row[value[1] + i - 1] = self.convertChar(value[4 + i])
            text = ''.join([chr(x) for x in row])
            self.signals.textRow.emit(value[2] - 1, text)

        elif value[0] == 2:
            # drawing pixel
            imaArr = np.zeros([8, 8, 3], dtype=np.uint8)
            for i in range(8):
                for j in range(8):
                    flag = (value[3 + j] & 128 >> i) != 0
                    if flag:
                        imaArr[i, j] = [255, 255, 255]
                    else:
                        imaArr[i, j] = [0, 0, 0]
            self.signals.imgChunk.emit(imaArr, 8 * (value[2] - 1),
                                       8 * (value[1] - 1))

        elif value[0] == 3:
            # drawing pixel
            imaArr = np.zeros([8, 12, 3], dtype=np.uint8)
            for i in range(12):
                for j in range(8):
                    flag = (value[3 + i] & 1 << j) != 0
                    if flag:
                        imaArr[j, i] = [255, 255, 255]
                    else:
                        imaArr[j, i] = [0, 0, 0]
            self.signals.imgChunk.emit(imaArr, 8 * (value[2] - 1),
                                       12 * (value[1] - 1))
        elif value[0] == 5:
            # setting cursor position
            self.signals.cursorPos.emit(value[2] - 1, value[1] - 1)

        elif value[0] == 6:
            pass
            # print('select 6')

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
        self.mousePressed(key)
        self.mouseReleased(key)
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
