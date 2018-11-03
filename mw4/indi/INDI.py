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
import enum
import re
from collections import OrderedDict
# external packages
# local imports


class INDI:
    MAXINDIFILENAME = 64
    MAXINDIBUF = 49152
    INDIV = '1.7'

    _lf_pattern = '[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
    _pattern = '('+_lf_pattern+')[^0-9]?('+_lf_pattern+')?[^0-9]?('+_lf_pattern+')?'
    _reg_exp_sexa = re.compile(_pattern)

    class SP:
        CONNECTION = 'CONNECTION'
        DEVICE_PORT = 'DEVICE_PORT'
        DEVICE_AUTO_SEARCH = 'DEVICE_AUTO_SEARCH'
        DEVICE_BAUD_RATE = 'DEVICE_BAUD_RATE'
        DEVICE_TCP_ADDRESS = 'DEVICE_TCP_ADDRESS'

    class ISState(enum.Enum):
        ISS_OFF = 'Off'
        ISS_ON = 'On'

    class IPState(enum.Enum):
        IPS_IDLE = 'Idle'
        IPS_OK = 'Ok'
        IPS_BUSY = 'Busy'
        IPS_ALERT = 'Alert'

    class ISRule(enum.Enum):
        ISR_1OFMANY = 'OneOfMany'
        ISR_ATMOST1 = 'AtMostOne'
        ISR_NOFMANY = 'AnyOfMany'

    class IPerm(enum.Enum):
        IP_RO='ro'
        IP_WO='wo'
        IP_RW='rw'

    class BLOBHandling(enum.Enum):
        B_NEVER = 'Never'
        B_ALSO = 'Also'
        B_ONLY = 'Only'

    class INDI_PROPERTY_TYPE(enum.Enum):
        INDI_NUMBER = 'INDI_NUMBER'
        INDI_SWITCH = 'INDI_SWITCH'
        INDI_TEXT = 'INDI_TEXT'
        INDI_LIGHT = 'INDI_LIGHT'
        INDI_BLOB = 'INDI_BLOB'
        INDI_UNKNOWN = 'INDI_UNKNOWN'

    class INDI_ERROR_TYPE(enum.IntEnum):
        INDI_DEVICE_NOT_FOUND = -1
        INDI_PROPERTY_INVALID = -2
        INDI_PROPERTY_DUPLICATED = -3
        INDI_DISPATCH_ERROR = -4

    class DRIVER_INTERFACE(enum.IntEnum):
        GENERAL_INTERFACE = 0
        TELESCOPE_INTERFACE = (1 << 0)
        CCD_INTERFACE = (1 << 1)
        GUIDER_INTERFACE = (1 << 2)
        FOCUSER_INTERFACE = (1 << 3)
        FILTER_INTERFACE = (1 << 4)
        DOME_INTERFACE = (1 << 5)
        GPS_INTERFACE = (1 << 6)
        WEATHER_INTERFACE = (1 << 7)
        AO_INTERFACE = (1 << 8)
        DUSTCAP_INTERFACE = (1 << 9)
        LIGHTBOX_INTERFACE = (1 << 10)
        DETECTOR_INTERFACE = (1 << 11)
        AUX_INTERFACE = (1 << 15)

    @staticmethod
    def crackIndi(s, c):
        for p in c:
            if s == p.value:
                return p
        return None

    @staticmethod
    def f_scan_sexa(s):
        if not s or s == '':
            return None
        m = INDI._reg_exp_sexa.match(s)
        if m.lastindex == 1:
            return float(m.group(1))
        elif m.lastindex == 2:
            return float(m.group(1)) + (float(m.group(2))/60.0)
        elif m.lastindex == 3:
            return float(m.group(1)) + (float(m.group(2))/60.0) + (float(m.group(3))/3600.0)
        else:
            return None

    @staticmethod
    def fs_sexa(a, w, fracbase):
        out = ''
        isneg = a < 0
        if isneg:
            a = -a
        n = int(a * fracbase + 0.5)
        d = n // fracbase
        f = n % fracbase
        if isneg and d == 0:
            out += '%*s-0' % (w-2, '')
        else:
            out += '%*d' % (w, -d if isneg else d)
        if fracbase == 60:
            m = f // (fracbase // 60)
            out += ':%02d' % m
        elif fracbase == 600:
            out += ':%02d.%1d' % (f // 10, f % 10)
        elif fracbase == 3600:
            m = f / (fracbase // 60)
            s = f % (fracbase // 60)
            out += ':%02d:%02d' % (m, s)
        elif fracbase == 36000:
            m = f / (fracbase // 60)
            s = f % (fracbase // 60)
            out += ':%02d:%02d.%1d' % (m, s // 10, s % 10)
        elif fracbase == 360000:
            m = f / (fracbase // 60)
            s = f % (fracbase // 60)
            out += ':%02d:%02d.%02d' % (m, s // 100, s % 100)
        else:
            return None
        return out

    @staticmethod
    def numberFormat(fmt, value):
        if fmt[0] != '%':
            raise ValueError
        m = fmt[-1]
        l = fmt[1:-1].split('.')
        if len(l) == 2 and m == 'm':
            cbase = {9: 360000, 8: 36000, 6: 3600, 5: 600}
            w = int(l[0])
            f = int(l[1])
            s = 60
            if f in cbase:
                s = cbase[f]
            return INDI.fs_sexa(value, w - f, s)
        else:
            return fmt % value

    @staticmethod
    def IUFindText(tvp, name):
        return tvp.vp.get(name, None)

    @staticmethod
    def IUFindNumber(nvp, name):
        return nvp.vp.get(name, None)

    @staticmethod
    def IUFindLight(lvp, name):
        return lvp.vp.get(name, None)

    @staticmethod
    def IUFindBLOB(bvp, name):
        return bvp.vp.get(name, None)

    @staticmethod
    def IUFindSwitch(svp, name):
        return svp.vp.get(name, None)

    @staticmethod
    def IUFindOnSwitch(svp):
        for sp in svp.vp.values():
            if sp.state == INDI.ISState.ISS_ON:
                return sp
        return None

    @staticmethod
    def IUFindOnSwitchIndex(svp):
        index = 0
        for sp in svp.vp.values():
            if sp.state == INDI.ISState.ISS_ON:
                return index
            index += 1
        return -1

    @staticmethod
    def IUResetSwitch(svp):
        for sp in svp.vp.values():
            sp.state = INDI.ISState.ISS_OFF


class IText:
    def __init__(self, name, label, text, parent, aux0=None, aux1=None):
        self.name = name
        self.label = label
        self.text = text
        self.tvp = parent
        self.aux0 = aux0
        self.aux1 = aux1

    def __str__(self):
        return self.text


class INumber:
    def __init__(self, name, label, numformat, minvalue, maxvalue, stepvalue, value, parent, aux0=None, aux1=None):
        self.name = name
        self.label = label
        self.format = numformat
        self.min = minvalue
        self.max = maxvalue
        self.step = stepvalue
        self.value = value
        self.nvp = parent
        self.aux0 = aux0
        self.aux1 = aux1

    def __str__(self):
        return str(self.value)


class ISwitch:
    def __init__(self, name, label, state, parent, aux=None):
        self.name = name
        self.label = label
        self.state = state
        self.svp = parent
        self.aux = aux

    def __str__(self):
        return self.state.value


class ILight:
    def __init__(self, name, label, state, parent, aux=None):
        self.name = name
        self.label = label
        self.state = state
        self.lvp = parent
        self.aux = aux

    def __str__(self):
        return self.state.value


class IBLOB:
    def __init__(self, name, label, blobformat, blob, bloblen, size, parent, aux0=None, aux1=None, aux2=None):
        self.name = name
        self.label = label
        self.format = blobformat
        self.blob = blob
        self.bloblen = bloblen
        self.size = size
        self.bvp = parent
        self.aux0 = aux0
        self.aux1 = aux1
        self.aux2 = aux2

    def __str__(self):
        return self.blob


class IVectorProperty:
    def __init__(self, device, name, label, group, perm, rule, timeout, state, prop_type, timestamp):
        self.device = device
        self.name = name
        self.label = label
        self.group = group
        self.perm = perm
        self.rule = rule
        self.timeout = timeout
        self.state = state
        self.type = prop_type
        self.vp = OrderedDict()
        self.timestamp = timestamp
        self.aux = None

    def __str__(self):
        fmt = '<IVectorProperty: {0}, type: {1}, device: {2}>'
        return fmt.format(self.name, self.type.value, self.device.name)

    def getGroupName(self):
        return self.group

    def getDeviceName(self):
        return self.device.getDeviceName()

    def getName(self):
        return self.name

    def getLabel(self):
        return self.label

    def getTimestamp(self):
        return self.timestamp

    def getState(self):
        return self.state

    def getType(self):
        return self.type

    def getPermission(self):
        return self.perm
