import time
import skyfield.named_stars
import skyfield.api
import numpy as np
import astropy._erfa as erfa

HEADER = '''
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
# Python  v3.7.3
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
#
# this file is auto generated for the purpose of getting data prepared
# to show the alignment stars in mountwizzard
#
# standard libraries
# external packages
# local import


def generateAlignStars():
    """
    generateAlignStars is the function where the alignment stars which were present in the
    mount computer from hipparcos catalogue are stored. for a correct calculation we need
    beside the J2000 coordinated the proper motion in ra and dec, the parallax and the
    radial velocity as the stars move over time. the data is calculated from the hipparcos
    catalogue using skyfield library

    the data is written in
    [name, hip no, ra, dec, ra proper motion, dec proper motion, parallax, radial velocity]
    based on J2000 epoch.
    the units are fitting erfa needs:
    [str, int, radians, radians, radians / year, radians/year, arc sec, km /s]


    """

    star = dict()
'''

FOOTER = '''
    return star
'''

named_star_dict = {
    'Achernar': 7588,
    'Acrux': 60718,
    'Adhara': 33579,
    # 'Agena': 68702,
    'Albireo': 95947,
    'Alcor': 65477,
    'Aldebaran': 21421,
    'Alderamin': 105199,
    'Algenib': 15863,
    'Algieba': 50583,
    'Algol': 14576,
    'Alhena': 31681,
    'Alioth': 62956,
    'Alkaid': 67301,
    'Almach': 9640,
    'Alnair': 109268,
    'Alnilam': 26311,
    'Alnitak': 26727,
    'Alphard': 46390,
    # 'Alphecca': 76267,
    'Alpheratz': 677,
    'Altair': 97649,
    'Aludra': 35904,
    'Ankaa': 2081,
    'Antares': 80763,
    'Arcturus': 69673,
    # 'Arided': 102098,
    # 'Aridif': 102098,
    # 'Aspidiske': 45556,
    'Atria': 82273,
    'Avior': 41037,
    'Becrux': 62434,
    'Bellatrix': 25336,
    # 'Benetnash': 67301,
    'Betelgeuse': 27989,
    'Birdun': 66657,
    'Canopus': 30438,
    'Capella': 24608,
    'Caph': 746,
    'Castor': 36850,
    'Deneb': 102098,
    # 'Deneb Kaitos': 3419,
    'Denebola': 57632,
    'Diphda': 3419,
    'Dschubba': 78401,
    'Dubhe': 54061,
    'Durre Menthor': 8102,
    'Elnath': 25428,
    'Enif': 107315,
    'Etamin': 87833,
    'Fomalhaut': 113368,
    'Foramen': 93308,
    'Gacrux': 61084,
    'Gemma': 76267,
    'Gienah': 102488,
    'Girtab': 86228,
    'Gruid': 112122,
    'Hadar': 68702,
    'Hamal': 9884,
    "Herschel's Garnet Star": 107259,
    'Izar': 72105,
    'Kaus Australis': 90185,
    'Kochab': 72607,
    'Koo She': 42913,
    'Marchab': 113963,
    'Marfikent': 71352,
    'Markab': 45941,
    'Megrez': 59774,
    'Men': 71860,
    'Menkalinan': 28360,
    'Menkent': 68933,
    'Merak': 53910,
    'Miaplacidus': 45238,
    # 'Mimosa': 62434,
    'Mintaka': 25930,
    'Mira': 10826,
    'Mirach': 5447,
    # 'Mirfak': 15863,
    'Mirzam': 30324,
    'Mizar': 65378,
    'Muhlifein': 61932,
    # 'Murzim': 30324,
    'Naos': 39429,
    'Nunki': 92855,
    'Peacock': 100751,
    'Phad': 58001,
    # 'Phecda': 58001,
    'Polaris': 11767,
    'Pollux': 37826,
    'Procyon': 37279,
    # 'Ras Alhague': 86032,
    'Rasalhague': 86032,
    'Regor': 39953,
    'Regulus': 49669,
    'Rigel': 24436,
    # 'Rigel Kent': 71683,
    # 'Rigil Kentaurus': 71683,
    'Sabik': 84012,
    'Sadira': 16537,
    'Sadr': 100453,
    'Saiph': 27366,
    # 'Sargas': 86228,
    'Scheat': 113881,
    'Schedar': 3179,
    # 'Scutulum': 45556,
    'Shaula': 85927,
    'Sirius': 32349,
    # 'Sirrah': 677,
    'South Star': 104382,
    'Spica': 65474,
    'Suhail': 44816,
    'Thuban': 68756,
    'Toliman': 71683,
    # 'Tseen She': 93308,
    'Tsih': 4427,
    'Turais': 45556,
    'Vega': 91262,
    'Wei': 82396,
    'Wezen': 34444,
}


def loadStars(path):
    fileName = path + '/hip_main.dat.gz'
    with skyfield.api.load.open(fileName) as f:
        df = skyfield.data.hipparcos.load_dataframe(f)

    if len(df) > 0:
        df = df[df['magnitude'] <= 3.5]
        print(len(df))
        starsDict = list()
        for index, row in df.iterrows():
            starsDict.append({row.name: skyfield.api.Star.from_dataframe(row)})

        starsDF = skyfield.api.Star.from_dataframe(df)

    return starsDF, starsDict


def make_test():

    ts = skyfield.api.load.timescale()
    planets = skyfield.api.load('de421.bsp')
    starsDF, starsDict = loadStars('.')
    earth = planets['earth']
    location = skyfield.api.Topos(latitude_degrees=50,
                                  longitude_degrees=11,
                                  elevation_m=500)
    observer = earth + location
    t = ts.now()

    # standard version plus
    timeStart = time.time()
    alt = list()
    az = list()
    """
    obs = observer.at(t)
    for value in starsDict:
        name, coord = list(value.items())[0]
        altE, azE, d = obs.observe(coord).apparent().altaz()
        alt.append(altE.degrees)
        az.append(azE.degrees)
    az_SKY = az
    alt_SKY = alt
    print('standard opt: ', time.time() - timeStart)
    """
    # standard version plus
    timeStart = time.time()
    alt, az, dist = observer.at(t).observe(starsDF).apparent().altaz()
    az_SKY_new = az.degrees
    alt_SKY_new = alt.hours
    print('skyfield master: ', time.time() - timeStart)

    # mas / year to radians / year
    # mas * 3600000 = degrees / year
    # mas * 3600000 / 360 * 2 * np.pi
    # mas/year  * 20000 * np.pi is radians / year
    # version with astropy and erfa and vector
    ra = starsDF.ra.radians
    dec = starsDF.dec.radians
    PR = starsDF.ra_mas_per_year / 3600000 * 2 * np.pi / 360
    PD = starsDF.dec_mas_per_year / 3600000 * 2 * np.pi / 360
    PX = starsDF.parallax_mas / 1000
    RV = starsDF.radial_km_per_s

    # J2000             = 2451544.5
    # HIP = J1991,25    = 2448347.5

    print('preparation')
    ra2, dec2, pr2, pd2, px2, rv2 = erfa.pmsafe(ra, dec, PR, PD, PX, RV,
                                                2448347.5, 0.0, 2452544.5, 0.0)
    timeStart = time.time()
    print('calculation')
    aob, zob, hob, dob, rob, eo = erfa.atco13(ra2,
                                              dec2,
                                              pr2,
                                              pd2,
                                              px2,
                                              rv2,
                                              t.ut1,
                                              0.0,
                                              t.dut1,
                                              location.longitude.radians,
                                              location.latitude.radians,
                                              location.elevation.m,
                                              0.0,
                                              0.0,
                                              0.0,
                                              0.0,
                                              0.0,
                                              0.0)
    az_ERFA = aob * 360 / 2 / np.pi
    alt_ERFA = 90.0 - zob * 360 / 2 / np.pi
    print('astropy scalar: ', time.time() - timeStart)
    print('error skyfield standard')
    print(np.max(abs(alt_ERFA - alt_SKY)), np.max(abs(az_ERFA - az_SKY)))
    print('error skyfield_new')
    print(np.max(abs(alt_ERFA - alt_SKY_new)), np.max(abs(az_ERFA - az_SKY_new)))


def testBrandon():
    ts = skyfield.api.load.timescale()
    planets = skyfield.api.load('de421.bsp')
    fileName = './hip_main.dat.gz'

    with skyfield.api.load.open(fileName) as f:
        df = skyfield.data.hipparcos.load_dataframe(f)

    starsDF = skyfield.api.Star.from_dataframe(df)

    earth = planets['earth']
    location = skyfield.api.Topos(latitude_degrees=50,
                                  longitude_degrees=11,
                                  elevation_m=500)
    observer = earth + location
    t = ts.now()

    # this calculation works
    ra, dec, dist = observer.at(t).observe(starsDF).radec()
    print(ra, dec, dist)

    # this calculation throws the named error
    alt, az, dist = observer.at(t).observe(starsDF).apparent().altaz()
    print(alt, au, dist)


def make_file():
    with open('alignstars.py', 'w') as f:
        f.write(HEADER)
        for name in named_star_dict:
            starH = skyfield.named_stars.NamedStar(name)
            ra = starH.ra.radians
            dec = starH.dec.radians
            ra_mas_per_year = starH.ra_mas_per_year
            dec_mas_per_year = starH.dec_mas_per_year
            parallax_mas = starH.parallax_mas
            radial_km_per_s = starH.radial_km_per_s

            # convert it for erfa routine in astropy as skyfield calculation is not performant
            # enough

            # convert mas / year to radians / year
            PR = ra_mas_per_year / 3600000 * 2 * np.pi / 360
            PD = dec_mas_per_year / 3600000 * 2 * np.pi / 360
            PX = parallax_mas / 1000
            RV = radial_km_per_s

            # and convert the epoch of hipparcos (J1991,25) to the epoch erfa needs (J2000)
            # J2000             = 2451544.5
            # HIP = J1991,25    = 2448347.5

            ra2, dec2, pr2, pd2, px2, rv2 = erfa.pmsafe(ra,
                                                        dec,
                                                        PR,
                                                        PD,
                                                        PX,
                                                        RV,
                                                        2448347.5,
                                                        0.0,
                                                        2452544.5,
                                                        0.0,
                                                        )

            if name.startswith('Hersch'):
                name = 'Herschel Star'

            lineA = "star['{0}'] = [{1}, {2}, {3},\n".format(name, ra2, dec2, pr2)
            lineB = "               {0}, {1}, {2}]\n".format(pd2, px2, rv2)
            print(name)
            f.write('    ' + lineA)
            spacer = ' ' * (len(name) - 3)
            f.write('    ' + spacer + lineB)
        f.write(FOOTER)


if __name__ == '__main__':
    testBrandon()
