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

# external packages
import numpy as np
from skyfield import almanac

# local import


def findSunlit(sat, ephemeris, tEvent) -> bool:
    """
    :param sat:
    :param ephemeris:
    :param tEvent:
    :return:
    """
    sunlit = sat.at(tEvent).is_sunlit(ephemeris)
    return sunlit


def findSatUp(sat, loc, tStart, tEnd, alt) -> [bool, list]:
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


def checkTwilight(ephemeris, loc, data) -> int:
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


def findRangeRate(sat, loc, tEv) -> [float, float, float, float]:
    """
    :param sat:
    :param loc:
    :param tEv:
    :return:
    """
    pos = (sat - loc).at(tEv)
    _, _, satRange, latRate, lonRate, radRate = pos.frame_latlon_and_rates(loc)
    return (
        satRange.km,
        radRate.km_per_s,
        latRate.degrees.per_second,
        lonRate.degrees.per_second,
    )


def calcSatSunPhase(sat, loc, ephemeris, tEv) -> float:
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
    earth = ephemeris["earth"]

    vecObserverSat = (sat - loc).at(tEv)
    vecSunSat = (earth + sat).at(tEv)
    phase = vecObserverSat.separation_from(vecSunSat)
    return phase


def calcAppMag(sat, loc, ephemeris, satRange, tEv) -> float:
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
    term2 = +5.0 * np.log10(satRange / 1000.0)
    arg = np.sin(phase) + (np.pi - phase) * np.cos(phase)
    term3 = -2.5 * np.log10(arg)
    appMag = term1 + term2 + term3
    return appMag


def calcSatelliteMeridianTransit(satellite, location, tolerance) -> callable:
    """ """
    difference = satellite - location

    def west_of_meridian_at(t):
        alt, az, _ = difference.at(t).altaz()
        delta = (az.degrees + tolerance + 360) % 360 - 180
        return delta < 0

    west_of_meridian_at.step_days = 0.4
    return west_of_meridian_at


def calcPassEvents(satellite, obsSite, minAlt=5) -> [list, list]:
    """ """
    if minAlt is None:
        minAlt = 5
    if minAlt < 5:
        minAlt = 5

    loc = obsSite.location
    orbitCycleTime = np.pi / satellite.model.no_kozai / 12 / 60
    t0 = obsSite.ts.tt_jd(obsSite.timeJD.tt - orbitCycleTime)
    t1 = obsSite.ts.tt_jd(obsSite.timeJD.tt + 5)
    times, events = satellite.find_events(loc, t0, t1, altitude_degrees=minAlt)
    return times, events


def collectAllOrbits(times, events, obsSite) -> list:
    """ """
    counter = 0
    satOrbits = []
    for ti, event in zip(times, events):
        if event == 0:
            satOrbits.append({"rise": ti})

        elif event == 1:
            if counter >= len(satOrbits):
                continue
            satOrbits[counter]["culminate"] = ti

        elif event == 2:
            if counter >= len(satOrbits):
                continue
            satOrbits[counter]["settle"] = ti

            if ti.tt < obsSite.ts.now().tt:
                del satOrbits[counter]
                continue
            counter += 1

        if counter > 2:
            break
    return satOrbits


def extractCorrectOrbits(times, events, satOrbits) -> list:
    """ """
    if not satOrbits and np.all(events == 1) and len(events) > 0:
        satOrbits.append({"rise": times[0]})
        satOrbits[0]["culminate"] = times[0] + 0.5
        satOrbits[0]["settle"] = times[0] + 1.0

    if "settle" not in satOrbits[-1]:
        del satOrbits[-1]

    return satOrbits


def sortFlipEvents(satOrbit, t0, t1, t2) -> dict:
    """ """
    settle = satOrbit["settle"]
    rise = satOrbit["rise"]
    if t0:
        satOrbit["flip"] = t0[0]
    if t1 and t2:
        if t1[0].tt > t2[0].tt:
            satOrbit["flipEarly"] = t2[0]
            satOrbit["flipLate"] = t1[0]
        else:
            satOrbit["flipEarly"] = t1[0]
            satOrbit["flipLate"] = t2[0]
    if t1 and not t2:
        if abs(rise.tt - t1[0].tt) > abs(settle.tt - t1[0].tt):
            satOrbit["flipLate"] = t1[0]
        else:
            satOrbit["flipEarly"] = t1[0]
    if not t1 and t2:
        if abs(rise.tt - t2[0].tt) > abs(settle.tt - t2[0].tt):
            satOrbit["flipLate"] = t2[0]
        else:
            satOrbit["flipEarly"] = t2[0]
    return satOrbit


def addMeridianTransit(satellite, satOrbits, location, setting) -> list:
    """ """
    limit = setting.meridianLimitTrack
    if limit is None:
        limit = 0
    limit = limit * 0.95

    f0 = calcSatelliteMeridianTransit(satellite, location, 0)
    f1 = calcSatelliteMeridianTransit(satellite, location, limit)
    f2 = calcSatelliteMeridianTransit(satellite, location, -limit)
    for i, satOrbit in enumerate(satOrbits):
        t0, y0 = almanac.find_discrete(satOrbit["rise"], satOrbit["settle"], f0)
        t1, y1 = almanac.find_discrete(satOrbit["rise"], satOrbit["settle"], f1)
        t2, y2 = almanac.find_discrete(satOrbit["rise"], satOrbit["settle"], f2)

        satOrbits[i] = sortFlipEvents(satOrbit, t0, t1, t2)
    return satOrbits


def calcSatPasses(satellite, obsSite, setting) -> list:
    """ """
    times, events = calcPassEvents(satellite, obsSite, setting.horizonLimitLow)
    satOrbits = collectAllOrbits(times, events, obsSite)
    satOrbits = extractCorrectOrbits(times, events, satOrbits)
    satOrbits = addMeridianTransit(satellite, satOrbits, obsSite.location, setting)
    return satOrbits
