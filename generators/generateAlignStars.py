from skyfield.data import hipparcos
from skyfield.api import Star, load
import numpy as np
import erfa

HEADER = '''############################################################
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
    generateAlignStars is the function where the alignment stars which were
    present in the mount computer from hipparcos catalogue are stored. for a
    correct calculation we need beside the J2000 coordinated the proper motion in
    ra and dec, the parallax and the radial velocity as the stars move over time.
    the data is calculated from the hipparcos catalogue using skyfield library

    the data is written in
    [name, hip no, ra, dec, ra proper motion, dec proper motion, parallax,
    radial velocity] based on J2000 epoch. the units are fitting erfa needs:
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


def make_file():
    with load.open(hipparcos.URL) as f:
        df = hipparcos.load_dataframe(f)

    with open('alignstars.py', 'w') as f:
        f.write(HEADER)
        for name in named_star_dict:
            starH = Star.from_dataframe(df.loc[named_star_dict[name]])
            ra = starH.ra.radians
            dec = starH.dec.radians
            ra_mas_per_year = starH.ra_mas_per_year
            dec_mas_per_year = starH.dec_mas_per_year
            parallax_mas = starH.parallax_mas
            radial_km_per_s = starH.radial_km_per_s

            # convert it for erfa routine in astropy as skyfield calculation
            # is not performant enough

            # convert mas / year to radians / year
            PR = ra_mas_per_year / 3600000 * 2 * np.pi / 360
            PD = dec_mas_per_year / 3600000 * 2 * np.pi / 360
            PX = parallax_mas / 1000
            RV = radial_km_per_s

            # and convert the epoch of hipparcos (J1991,25) to the epoch
            # erfa needs (J2000)
            # J2000             = 2451545
            # HIP = J1991,25    = 2448347.5

            ra2, dec2, pr2, pd2, px2, rv2 = erfa.pmsafe(ra,
                                                        dec,
                                                        PR,
                                                        PD,
                                                        PX,
                                                        RV,
                                                        2448347.5,
                                                        0.0,
                                                        2451545,
                                                        0.0,
                                                        )

            if name.startswith('Hersch'):
                name = 'Herschel Star'

            lineA = f"star['{name}'] = [{ra2}, {dec2},\n"
            lineB = f"               {pr2}, {pd2},\n"
            lineC = f"               {px2}, {rv2}]\n"
            print(name)
            f.write('    ' + lineA)
            spacer = ' ' * (len(name) - 3)
            f.write('    ' + spacer + lineB)
            f.write('    ' + spacer + lineC)
        f.write(FOOTER)


if __name__ == '__main__':
    make_file()
