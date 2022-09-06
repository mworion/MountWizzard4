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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
# 10 micron mount simulator
#
###########################################################
# standard imports

# package imports

# local imports


class Server:
    pass


class GUI:
    pass


class Coordinates:
    def __init__(self):
        pass

    self._actRa = 0
    self._actDec = 0
    self._actAlt = 0
    self._actAz = 0
    self._targetRa = 0
    self._targetDec = 0
    self._targetAlt = 0
    self._targetAz = 0
    self._actAngRa = 0
    self._actAngDec = 0
    self._targetAngRa = 0
    self._tragetAngDec = 0
    
    @property
    def actRa(self):
        return self._actRa

    @actRa.setter
    def actRa(self, value):
        self._actRa = valueToAngle(value)
    
    @property
    def actDec(self):
        return self._actDec

    @actDec.setter
    def actDec(self, value):
        self._actDec = valueToAngle(value)

    @property
    def actAlt(self):
        return self._actAlt

    @actAlt.setter
    def actAlt(self, value):
        self._actAlt = valueToAngle(value)
    
    @property
    def actAz(self):
        return self._actAz

    @actAz.setter
    def actAz(self, value):
        self._actAz = valueToAngle(value)

    @property
    def targetRa(self):
        return self._targetRa

    @targetRa.setter
    def targetRa(self, value):
        self._targetRa = valueToAngle(value)
    
    @property
    def targetDec(self):
        return self._targetDec

    @targetDec.setter
    def targetDec(self, value):
        self._targetDec = valueToAngle(value)

    @property
    def targetAlt(self):
        return self._targetAlt

    @targetAlt.setter
    def targetAlt(self, value):
        self._targetAlt = valueToAngle(value)
    
    @property
    def targetAz(self):
        return self._targetAz

    @targetAz.setter
    def targetAz(self, value):
        self._targetAz = valueToAngle(value)

    @property
    def actAngRa(self):
        return self._actAngRa

    @actAngRa.setter
    def actAngRa(self, value):
        self._actAngRa = valueToAngle(value)
    
    @property
    def actAngDec(self):
        return self._actAngDec

    @actAngDec.setter
    def actAngDec(self, value):
        self._actAngDec = valueToAngle(value)

    @property
    def targetAngRa(self):
        return self._targetAngRa

    @targetAngRa.setter
    def targetAngRa(self, value):
        self._actAngRa = valueToAngle(value)
    
    @property
    def targetAngDec(self):
        return self._targetAngDec

    @targetAngDec.setter
    def targetAngDec(self, value):
        self._targetAngDec = valueToAngle(value)
    
    @property
    def pierside(self):
        return self._pierside

    @pierside.setter
    def pierside(self, value):
        self._pierside = value
