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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import numpy as np
from skyfield import almanac

# local import


def findSunlit(sat, ephemeris, tEvent):
    """
    :param sat:
    :param ephemeris:
    :param tEvent:
    :return:
    """
    sunlit = sat.at(tEvent).is_sunlit(ephemeris)
    return sunlit


def findSatUp(sat, loc, tStart, tEnd, alt):
    """
    :param sat:
    :param loc:
    :param tStart:
    :param tEnd:
    :param alt:
    :return:
    """
    t, events = sat.find_events(loc, tStart, tEnd, altitude_degrees=alt)
    if 1 in events:
        return True, t[np.equal(events, 1)]
    else:
        return False, []


def checkTwilight(ephemeris, loc, data):
    """
    :param ephemeris:
    :param loc:
    :param data:
    :return:
    """
    isUp = data[0]
    if not isUp:
        return 4

    satTime = data[1][0]
    f = almanac.dark_twilight_day(ephemeris, loc)
    twilight = int(f(satTime))
    return twilight


def findRangeRate(sat, loc, tEv):
    """
    :param sat:
    :param loc:
    :param tEv:
    :return:
    """
    pos = (sat - loc).at(tEv)
    _, _, satRange, latRate, lonRate, radRate = pos.frame_latlon_and_rates(loc)
    return (satRange.km,
            radRate.km_per_s,
            latRate.degrees.per_second,
            lonRate.degrees.per_second)


def calcSatSunPhase(sat, loc, ephemeris, tEv):
    """
    https://stackoverflow.com/questions/19759501
        /calculating-the-phase-angle-between-the-sun-iss-and-an-observer-on-the
        -earth
    https://space.stackexchange.com/questions/26286
        /how-to-calculate-cone-angle-between-two-satellites-given-their-look-angles
    :param sat:
    :param loc:
    :param ephemeris:
    :param tEv:
    :return:
    """
    earth = ephemeris['earth']

    vecObserverSat = (sat - loc).at(tEv)
    vecSunSat = (earth + sat).at(tEv)
    phase = vecObserverSat.separation_from(vecSunSat)
    return phase


def calcAppMag(sat, loc, ephemeris, satRange, tEv):
    """
    solution base on the work from:
    https://astronomy.stackexchange.com/questions/28744
        /calculating-the-apparent-magnitude-of-a-satellite/28765#28765
    https://astronomy.stackexchange.com/q/28744/7982
    https://www.researchgate.net/publication
        /268194552_Large_phase_angle_observations_of_GEO_satellites
    https://amostech.com/TechnicalPapers/2013/POSTER/COGNION.pdf
    https://apps.dtic.mil/dtic/tr/fulltext/u2/785380.pdf

    :param sat:
    :param loc:
    :param ephemeris:
    :param sat:
    :param satRange:
    :param tEv:
    :return:
    """
    phase = calcSatSunPhase(sat, loc, ephemeris, tEv).radians
    intMag = -1.3

    term1 = intMag
    term2 = +5.0 * np.log10(satRange / 1000.)
    arg = np.sin(phase) + (np.pi - phase) * np.cos(phase)
    term3 = -2.5 * np.log10(arg)
    appMag = term1 + term2 + term3
    return appMag
