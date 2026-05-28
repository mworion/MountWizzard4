############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
from dataclasses import dataclass
from mw4.mountcontrol.jdParamMixin import JdParamsMixin
from skyfield.api import load


class ObsSite:
    UTC2TT = 69
    ts = load.timescale()


@dataclass
class ConcreteParams(JdParamsMixin):
    obsSite: ObsSite


def testJdStartDefault():
    params = ConcreteParams(ObsSite())
    assert params.jdStart is not None


def testJdStartZero():
    params = ConcreteParams(ObsSite())
    params.jdStart = 0
    assert params.jdStart.tt == 69


def testJdStartValue():
    params = ConcreteParams(ObsSite())
    params.jdStart = 100
    assert params.jdStart.tt == 169


def testJdEndDefault():
    params = ConcreteParams(ObsSite())
    assert params.jdEnd is not None


def testJdEndZero():
    params = ConcreteParams(ObsSite())
    params.jdEnd = 0
    assert params.jdEnd.tt == 69


def testJdEndValue():
    params = ConcreteParams(ObsSite())
    params.jdEnd = 100
    assert params.jdEnd.tt == 169
