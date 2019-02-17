import numpy as np
import matplotlib as plt
import pylab


def constellations(plot=False, plot3d=False, color='blue', radius=None, greatcircles=True):
    """ Plot constellation patterns, in 2D or 3D.

    This does not provide extraordinarily high precision; it's just a cosmetic display that sketches out
    the appropriate stick figures on the sky.  Data coordinates must be degrees.

    Based on IDL constellations.pro by Marshall Perrin.
    Constellation data is taken from Xephem, courtesy of Elwood Downey.

    Parameters
    -----------
    plot, plot3D : bool
        Draw constellations into current Axes in 2D, or 3D using mplot3d, respectively.
        If neither of these is set, the constellation stick figure data will be returned as a dictionary.
    color : Matplotlib color specification
        Color for the lines
    radius : float
        Only used for Mplot3d display, in which case it sets the radius of the sphere on which the constellations are drawn.
    greatcircles : bool
        Draw major great circles such as celestial equator, 0 RA, etc.


    """

    constellation_data = dict()

    # The data structures containing the points for each constellation are as
    # follows (from Xephem):
    #
    #  typedef struct [
    #      short drawcode;
    #      unsigned short ra;	/* hours * 1800 */
    #      short dec;		/* degrees * 60 */
    #  ] ConFig;
    #

    constellation_data["Andromeda"] = [
        [0, 3717, 2539],  # /* move gamma 1 */
        [1, 2091, 2137],  # /* draw beta */
        [1, 1179, 1851],  # /* draw delta */
        [1, 251, 1745],  # /* draw alpha */
        [0, 1716, 1405],  # /* move eta */
        [1, 1420, 1456],  # /* draw zeta */
        [1, 1156, 1758],  # /* draw epsilon */
        [1, 1179, 1851],  # /* draw delta */
        [1, 1106, 2023],  # /* draw pi */
        [1, 512, 2320],  # /* draw theta */
        [1, 42544, 2596],  # /* draw iota */
        [1, 42612, 2660],  # /* draw kappa */
        [1, 42526, 2787],  # /* draw lambda */
        [0, 42544, 2596],  # /* move iota */
        [1, 41457, 2539],  # /* draw omicron */
        [0, 1106, 2023],  # /* move pi */
        [1, 2091, 2137],  # /* draw beta */
        [1, 1702, 2309],  # /* draw mu */
        [1, 1494, 2464],  # /* draw nu */
        [1, 2085, 2834],  # /* draw phi */
        [1, 2939, 2917],  # /* draw 51 */
        [-1, 0, 0]
    ]

    constellation_data["Antlia"] = [
        [0, 17077, -2157],  # /* move epsilon */
        [2, 18814, -1864],  # /* dotted alpha */
        [2, 19701, -2228],  # /* dotted iota */
        [-1, 0, 0]
    ]

    constellation_data["Apus"] = [
        [0, 26635, -4742],  # /* move alpha */
        [2, 29803, -4733],  # /* dotted gamma */
        [2, 30092, -4651],  # /* dotted beta */
        [2, 29410, -4721],  # /* dotted delta 1 */
        [2, 29803, -4733],  # /* dotted gamma */
        [-1, 0, 0]
    ]

    constellation_data["Aquarius"] = [
        [0, 37430, -569],  # /* move epsilon */
        [1, 38746, -334],  # /* draw beta */
        [1, 39773, -19],  # /* draw alpha */
        [1, 40249, -83],  # /* draw gamma */
        [1, 40464, -1],  # /* draw zeta 1 */
        [1, 40358, 82],  # /* draw pi */
        [1, 39773, -19],  # /* draw alpha */
        [0, 40464, -1],  # /* move zeta 1 */
        [1, 40660, -7],  # /* draw eta */
        [0, 38746, -334],  # /* move beta */
        [1, 39793, -832],  # /* draw iota */
        [0, 39773, -19],  # /* move alpha */
        [1, 40105, -467],  # /* draw theta */
        [1, 41178, -454],  # /* draw lambda */
        [1, 41829, -362],  # /* draw phi */
        [1, 41937, -550],  # /* draw psi 2 */
        [1, 41239, -949],  # /* draw delta */
        [1, 41087, -815],  # /* draw tau 2 */
        [1, 41178, -454],  # /* draw lambda */
        [0, 42089, -1206],  # /* move 98 */
        [1, 41937, -550],  # /* draw psi 2 */
        [1, 41683, -1270],  # /* draw 88 */
        [-1, 0, 0]
    ]

    constellation_data["Aquila"] = [
        [0, 35859, 384],  # /* move beta */
        [1, 35723, 532],  # /* draw alpha */
        [1, 35587, 636],  # /* draw gamma */
        [1, 34964, 186],  # /* draw delta */
        [1, 34387, -292],  # /* draw lambda */
        [1, 34362, 831],  # /* draw zeta */
        [1, 34964, 186],  # /* draw delta */
        [1, 35774, 60],  # /* draw eta */
        [1, 36339, -49],  # /* draw theta */
        [1, 35301, -77],  # /* draw iota */
        [1, 34387, -292],  # /* draw lambda */
        [-1, 0, 0]
    ]

    constellation_data["Ara"] = [
        [0, 31811, -2964],  # /* move lambda */
        [1, 31555, -2992],  # /* draw alpha */
        [1, 31359, -3331],  # /* draw beta */
        [1, 31361, -3382],  # /* draw gamma */
        [1, 31532, -3641],  # /* draw delta */
        [1, 30293, -3542],  # /* draw eta */
        [1, 30558, -3359],  # /* draw zeta */
        [1, 30587, -3189],  # /* draw epsilon 1 */
        [1, 31555, -2992],  # /* draw alpha */
        [-1, 0, 0]
    ]

    constellation_data["Aries"] = [
        [0, 3405, 1157],  # /* move gamma */
        [1, 3439, 1248],  # /* draw beta */
        [1, 3815, 1407],  # /* draw alpha */
        [1, 5099, 1635],  # /* draw 41 */
        [-1, 0, 0]
    ]

    constellation_data["Auriga"] = [
        [0, 9500, 2759],  # /* move capella */
        [1, 10785, 2696],  # /* draw beta */
        [1, 10791, 2232],  # /* draw theta */
        [1, 9788, 1716],  # /* draw beta tau */
        [1, 8909, 1989],  # /* draw iota */
        [1, 9500, 2759],  # /* draw capella */
        [1, 10785, 3257],  # /* draw delta */
        [1, 10785, 2696],  # /* draw beta */
        [0, 9500, 2759],  # /* move capella */
        [1, 9059, 2629],  # /* draw epsilon */
        [1, 9074, 2464],  # /* draw zeta */
        [-1, 0, 0]
    ]

    constellation_data["Bootes"] = [
        [0, 26434, 823],  # /* move zeta */
        [1, 25669, 1150],  # /* draw arcturus */
        [1, 26549, 1624],  # /* draw epsilon */
        [1, 27465, 1998],  # /* draw delta */
        [1, 27058, 2423],  # /* draw beta */
        [1, 26162, 2298],  # /* draw gamma */
        [1, 26154, 1822],  # /* draw rho */
        [1, 25669, 1150],  # /* draw arcturus */
        [1, 25040, 1103],  # /* draw eta */
        [1, 24817, 1047],  # /* draw tau */
        [0, 26162, 2298],  # /* move gamma */
        [1, 25691, 2765],  # /* draw lambda */
        [1, 25604, 3107],  # /* draw kappa 2 */
        [1, 25955, 3111],  # /* draw theta */
        [1, 25691, 2765],  # /* draw lambda */
        [-1, 0, 0]
    ]

    constellation_data["Caelum"] = [
        [0, 9132, -2129],  # /* move gamma */
        [2, 8461, -2228],  # /* dotted beta */
        [2, 8416, -2511],  # /* dotted alpha */
        [2, 8125, -2697],  # /* dotted delta */
        [-1, 0, 0]
    ]

    constellation_data["Camelopardalis"] = [
        [0, 8918, 3225],  # /* move 7 */
        [2, 9102, 3626],  # /* dotted beta */
        [2, 8821, 3980],  # /* dotted alpha */
        [2, 6910, 4279],  # /* dotted gamma */
        [2, 6885, 3931],  # /* dotted 3:49:31 65:31:34 */
        [2, 6272, 3596],  # /* dotted 6272 3596 */
        [0, 8821, 3980],  # /* move alpha */
        [2, 11365, 4159],  # /* dotted 6:18:51 69:19:11 */
        [2, 12602, 4618],  # /* dotted 7:00:04 76:58:39 */
        [-1, 0, 0]
    ]

    constellation_data["Cancer"] = [
        [0, 15800, 1725],  # /* move iota1 */
        [2, 15698, 1288],  # /* dotted gamma */
        [2, 15740, 1089],  # /* dotted delta */
        [2, 16154, 711],  # /* dotted alpha */
        [0, 15740, 1089],  # /* move delta */
        [2, 14895, 551],  # /* dotted beta */
        [-1, 0, 0]
    ]

    constellation_data["Canes_Venatici"] = [
        [0, 23280, 2299],  # /* move alpha2 */
        [2, 22612, 2481],  # /* dotted beta */
        [-1, 0, 0]
    ]

    constellation_data["Canis_Major"] = [
        [0, 13322, -1758],  # /* move eta */
        [1, 12851, -1583],  # /* draw delta */
        [1, 12690, -1430],  # /* draw omicron2 */
        [1, 12154, -1002],  # /* draw alpha */
        [1, 11481, -1077],  # /* draw beta */
        [1, 11900, -1155],  # /* draw nu2 */
        [1, 12423, -1451],  # /* draw omicron1 */
        [1, 12558, -1738],  # /* draw epsilon */
        [1, 12651, -1676],  # /* draw sigma */
        [1, 12851, -1583],  # /* draw delta */
        [0, 12154, -1002],  # /* move alpha */
        [2, 12484, -1023],  # /* dotted iota */
        [2, 12712, -938],  # /* dotted gamma */
        [2, 12483, -842],  # /* dotted mu */
        [2, 12484, -1023],  # /* dotted iota */
        [-1, 0, 0]
    ]

    constellation_data["Canis_Minor"] = [
        [0, 13779, 313],  # /* move alpha */
        [1, 13414, 497],  # /* draw beta */
        [-1, 0, 0]
    ]

    constellation_data["Capricornus"] = [
        [0, 36529, -750],  # /* move alpha1 */
        [1, 36630, -886],  # /* draw beta */
        [1, 37382, -1516],  # /* draw psi */
        [1, 37554, -1615],  # /* draw omega */
        [1, 38013, -1500],  # /* draw 24 */
        [1, 38600, -1344],  # /* draw zeta */
        [1, 38912, -1167],  # /* draw epsilon */
        [1, 39211, -967],  # /* draw delta */
        [1, 39002, -999],  # /* draw gamma */
        [1, 38467, -1010],  # /* draw iota */
        [1, 37978, -1033],  # /* draw theta */
        [1, 36529, -750],  # /* draw alpha1 */
        [-1, 0, 0]
    ]

    constellation_data["Carina"] = [
        [0, 11518, -3161],  # /* move canopus */
        [1, 16596, -4183],  # /* draw beta */
        [1, 18412, -4202],  # /* draw omega */
        [1, 19288, -3863],  # /* draw theta */
        [1, 19996, -3745],  # /* draw 11:06:32 -62:25:27 */
        [1, 20178, -3619],  # /* draw 11:12:36 -60:19:03 */
        [1, 20057, -3538],  # /* draw 11:08:35 -58:58:30 */
        [1, 19605, -3531],  # /* draw 10:53:30 -58:51:12 */
        [1, 19351, -3581],  # /* draw eta */
        [1, 18960, -3701],  # /* draw 10:32:01 -61:41:07 */
        [1, 19288, -3863],  # /* draw theta */
        [0, 18960, -3701],  # /* move 10:32:01 -61:41:07 */
        [1, 18512, -3679],  # /* draw 10:17:05 -61:19:56 */
        [1, 16712, -3556],  # /* draw iota */
        [1, 15741, -3282],  # /* draw delta vel */
        [0, 16712, -3556],  # /* move iota */
        [1, 15075, -3570],  # /* draw epsilon */
        [1, 14303, -3178],  # /* draw chi */
        [1, 14686, -2840],  # /* draw gamma2 vel */
        [-1, 0, 0]
    ]

    constellation_data["Cassiopeia"] = [
        [0, 275, 3548],  # /* move beta */
        [1, 1215, 3392],  # /* draw alpha */
        [1, 1701, 3643],  # /* draw gamma */
        [1, 2574, 3614],  # /* draw delta */
        [1, 3431, 3820],  # /* draw epsilon */
        [-1, 0, 0]
    ]

    constellation_data["Centaurus"] = [
        [0, 26387, -3650],  # /* move alpha1 */
        [1, 25314, -3622],  # /* draw hadar (agena) */
        [1, 24596, -3207],  # /* draw epsilon */
        [1, 25066, -2837],  # /* draw zeta */
        [1, 25251, -2736],  # /* draw upsilon2 */
        [1, 25160, -2688],  # /* draw upsilon1 */
        [1, 25148, -2526],  # /* draw phi */
        [1, 26265, -2529],  # /* draw eta */
        [1, 26974, -2526],  # /* draw kappa */
        [0, 25148, -2526],  # /* move phi */
        [1, 25381, -2470],  # /* draw chi */
        [1, 25816, -2273],  # /* draw psi */
        [1, 25400, -2182],  # /* draw theta */
        [1, 24885, -2501],  # /* draw nu */
        [1, 24331, -2364],  # /* draw 24331 -2364 */
        [1, 24017, -2202],  # /* draw iota */
        [1, 23203, -2410],  # /* draw 23203 -2410 */
        [0, 24885, -2501],  # /* move nu */
        [1, 24888, -2548],  # /* draw mu */
        [1, 25066, -2837],  # /* draw zeta */
        [1, 22845, -2937],  # /* draw gamma */
        [1, 24596, -3207],  # /* draw epsilon */
        [0, 22845, -2937],  # /* move gamma */
        [1, 22441, -3013],  # /* draw sigma */
        [1, 21949, -3142],  # /* draw rho */
        [1, 21195, -3670],  # /* draw 21195 -3670 */
        [1, 20873, -3781],  # /* draw lambda */
        [0, 22441, -3013],  # /* move sigma */
        [1, 21850, -3043],  # /* draw delta */
        [1, 20430, -3269],  # /* draw pi */
        [-1, 0, 0]
    ]

    constellation_data["Cepheus"] = [
        [0, 38357, 3755],  # /* move alpha */
        [1, 38659, 4233],  # /* draw beta */
        [1, 42580, 4657],  # /* draw gamma */
        [1, 41090, 3972],  # /* draw iota */
        [1, 42580, 4657],  # /* draw gamma */
        [0, 41090, 3972],  # /* move iota */
        [1, 39925, 3492],  # /* draw zeta */
        [1, 39163, 3667],  # /* draw nu */
        [1, 39105, 3526],  # /* draw mu */
        [1, 38357, 3755],  # /* draw alpha */
        [1, 37358, 3710],  # /* draw eta */
        [1, 36887, 3779],  # /* draw theta */
        [-1, 0, 0]
    ]

    constellation_data["Cetus"] = [
        [0, 4899, 194],  # /* move gamma */
        [1, 5468, 245],  # /* draw alpha */
        [1, 5391, 534],  # /* draw lambda */
        [1, 4948, 606],  # /* draw mu */
        [1, 4444, 507],  # /* draw xi2 */
        [1, 4676, 335],  # /* draw nu */
        [1, 4899, 194],  # /* draw gamma */
        [1, 4784, 19],  # /* draw delta */
        [1, 4180, -178],  # /* draw mira */
        [1, 3343, -620],  # /* draw zeta */
        [1, 2520, -491],  # /* draw theta */
        [1, 2057, -610],  # /* draw eta */
        [1, 582, -529],  # /* draw iota */
        [1, 1307, -1079],  # /* draw beta */
        [1, 3122, -956],  # /* draw tau */
        [1, 3343, -620],  # /* draw zeta */
        [-1, 0, 0]
    ]

    constellation_data["Chamaeleon"] = [
        [0, 14955, -4615],  # /* move alpha */
        [1, 15019, -4649],  # /* draw theta */
        [1, 19064, -4716],  # /* draw gamma */
        [1, 21588, -4693],  # /* draw epsilon */
        [1, 22150, -4758],  # /* draw beta */
        [1, 19357, -4828],  # /* draw delta1 */
        [1, 19064, -4716],  # /* draw gamma */
        [-1, 0, 0]
    ]

    constellation_data["Circinus"] = [
        [0, 27525, -3528],  # /* move beta */
        [1, 26475, -3898],  # /* draw alpha */
        [1, 27701, -3559],  # /* draw gamma */
        [-1, 0, 0]
    ]

    constellation_data["Columba"] = [
        [0, 9936, -2128],  # /* move epsilon */
        [1, 10189, -2044],  # /* draw alpha */
        [1, 10528, -2146],  # /* draw beta */
        [1, 10726, -2117],  # /* draw gamma */
        [1, 11463, -2006],  # /* draw delta */
        [0, 10528, -2146],  # /* move beta */
        [1, 10774, -2568],  # /* draw eta */
        [-1, 0, 0]
    ]

    constellation_data["Coma_Berenices"] = [
        [0, 23699, 1051],  # /* move alpha */
        [2, 23756, 1672],  # /* dotted beta */
        [2, 22408, 1696],  # /* dotted gamma */
        [-1, 0, 0]
    ]

    constellation_data["Corona_Australis"] = [
        [0, 34392, -2223],  # /* move gamma */
        [1, 34484, -2274],  # /* draw alpha */
        [1, 34500, -2360],  # /* draw beta */
        [1, 34450, -2429],  # /* draw delta */
        [1, 33405, -2538],  # /* draw theta */
        [-1, 0, 0]
    ]

    constellation_data["Corona_Borealis"] = [
        [0, 27987, 1881],  # /* move theta */
        [1, 27834, 1746],  # /* draw beta */
        [1, 28040, 1602],  # /* draw alpha */
        [1, 28282, 1577],  # /* draw gamma */
        [1, 28487, 1564],  # /* draw delta */
        [1, 28727, 1612],  # /* draw epsilon */
        [1, 28843, 1791],  # /* draw iota */
        [-1, 0, 0]
    ]

    constellation_data["Corvus"] = [
        [0, 21852, -1483],  # /* move alpha */
        [1, 21903, -1357],  # /* draw epsilon */
        [1, 22631, -1403],  # /* draw beta */
        [1, 22495, -990],  # /* draw delta */
        [1, 22074, -1052],  # /* draw gamma */
        [1, 21903, -1357],  # /* draw epsilon */
        [-1, 0, 0]
    ]

    constellation_data["Crater"] = [
        [0, 21480, -1029],  # /* move eta */
        [1, 21142, -1101],  # /* draw zeta */
        [1, 20546, -1061],  # /* draw gamma */
        [1, 20500, -1126],  # /* draw lambda */
        [1, 20149, -1369],  # /* draw beta */
        [1, 19793, -1097],  # /* draw alpha */
        [1, 20380, -886],  # /* draw delta */
        [1, 20546, -1061],  # /* draw gamma */
        [0, 20380, -886],  # /* move delta */
        [1, 20538, -651],  # /* draw epsilon */
        [1, 20900, -588],  # /* draw theta */
        [-1, 0, 0]
    ]

    constellation_data["Crux"] = [
        [0, 22397, -3785],  # /* move alpha1 */
        [1, 22534, -3426],  # /* draw gamma */
        [0, 23031, -3581],  # /* move beta */
        [1, 22054, -3524],  # /* draw delta */
        [-1, 0, 0]
    ]

    constellation_data["Cygnus"] = [
        [0, 35121, 1677],  # /* move beta1 */
        [1, 35716, 1974],  # /* draw chi */
        [1, 35889, 2105],  # /* draw eta */
        [1, 36666, 2415],  # /* draw gamma */
        [1, 37386, 2038],  # /* draw epsilon */
        [2, 38188, 1813],  # /* dotted zeta */
        [2, 37715, 2470],  # /* dotted nu */
        [2, 37242, 2716],  # /* dotted deneb */
        [1, 36666, 2415],  # /* draw gamma */
        [1, 35549, 2707],  # /* draw delta */
        [2, 35091, 3103],  # /* dotted iota */
        [2, 34713, 3202],  # /* dotted kappa */
        [0, 35091, 3103],  # /* move iota */
        [2, 36464, 2862],  # /* dotted 32 */
        [2, 37242, 2716],  # /* dotted deneb */
        [-1, 0, 0]
    ]

    constellation_data["Delphinus"] = [
        [0, 36996, 678],  # /* move epsilon */
        [1, 37018, 781],  # /* draw eta */
        [1, 37126, 875],  # /* draw beta */
        [1, 37303, 904],  # /* draw delta */
        [1, 37399, 967],  # /* draw gamma1 */
        [1, 37189, 954],  # /* draw alpha */
        [1, 37126, 875],  # /* draw beta */
        [-1, 0, 0]
    ]

    constellation_data["Dorado"] = [
        [0, 7680, -3089],  # /* move gamma */
        [1, 8219, -3302],  # /* draw alpha */
        [1, 10008, -3749],  # /* draw beta */
        [1, 10343, -3944],  # /* draw delta */
        [1, 10623, -3785],  # /* draw 5:54:06 -63:05:23 */
        [1, 10008, -3749],  # /* draw beta */
        [1, 9165, -3448],  # /* draw zeta */
        [1, 8219, -3302],  # /* draw alpha */
        [-1, 0, 0]
    ]

    constellation_data["Draco"] = [
        [0, 20742, 4159],  # /* move lambda */
        [1, 22604, 4187],  # /* draw kappa */
        [1, 25331, 3862],  # /* draw alpha */
        [1, 27747, 3537],  # /* draw iota */
        [1, 28856, 3513],  # /* draw theta */
        [1, 29519, 3690],  # /* draw eta */
        [1, 30863, 3942],  # /* draw zeta */
        [1, 33022, 4280],  # /* draw phi */
        [1, 33031, 4363],  # /* draw chi */
        [0, 33022, 4280],  # /* move phi */
        [1, 34576, 4059],  # /* draw delta */
        [1, 35645, 4216],  # /* draw epsilon */
        [0, 34576, 4059],  # /* move delta */
        [1, 32205, 3412],  # /* draw xi */
        [1, 31565, 3311],  # /* draw nu1 */
        [1, 31513, 3138],  # /* draw beta */
        [1, 32298, 3089],  # /* draw gamma */
        [1, 32205, 3412],  # /* draw xi */
        [-1, 0, 0]
    ]

    constellation_data["Equuleus"] = [
        [0, 38110, 607],  # /* move gamma */
        [2, 38234, 600],  # /* dotted delta */
        [2, 38274, 314],  # /* dotted alpha */
        [-1, 0, 0]
    ]

    constellation_data["Eridanus"] = [
        [0, 9235, -305],  # /* move beta */
        [1, 8786, -327],  # /* draw omega */
        [1, 8565, -195],  # /* draw mu */
        [1, 8289, -201],  # /* draw nu */
        [1, 7555, -410],  # /* draw omicron1 */
        [1, 7140, -810],  # /* draw gamma */
        [1, 6784, -726],  # /* draw pi */
        [1, 6697, -585],  # /* draw delta */
        [1, 6387, -567],  # /* draw epsilon */
        [1, 5292, -533],  # /* draw eta */
        [1, 4923, -831],  # /* draw cet pi */
        [1, 4953, -1114],  # /* draw tau1 */
        [1, 5471, -1417],  # /* draw tau3 */
        [1, 5985, -1305],  # /* draw tau4 */
        [1, 6413, -1297],  # /* draw tau5 */
        [1, 6805, -1394],  # /* draw tau6 */
        [1, 7011, -1476],  # /* draw tau8 */
        [1, 7197, -1440],  # /* draw tau9 */
        [1, 8205, -1786],  # /* draw upsilon1 */
        [1, 8266, -1833],  # /* draw upsilon2 */
        [1, 7921, -2041],  # /* draw 43 */
        [1, 7736, -2027],  # /* draw upsilon4 */
        [1, 6883, -2172],  # /* draw 3:49:27 -36:12:01 */
        [1, 6685, -2238],  # /* draw 3:42:50 -37:18:49 */
        [1, 6513, -2416],  # /* draw 3:37:06 -40:16:29 */
        [1, 5998, -2584],  # /* draw 3:19:56 -43:04:11 */
        [1, 5348, -2418],  # /* draw theta2 */
        [1, 4820, -2391],  # /* draw iota */
        [1, 4794, -2573],  # /* draw 4794 -2573 */
        [1, 4409, -2862],  # /* draw kappa */
        [1, 4095, -3090],  # /* draw phi */
        [1, 3478, -3096],  # /* draw chi */
        [1, 2931, -3434],  # /* draw achernar */
        [-1, 0, 0]
    ]

    constellation_data["Fornax"] = [
        [0, 5762, -1739],  # /* move alpha */
        [1, 5072, -1944],  # /* draw beta */
        [1, 3734, -1757],  # /* draw nu */
        [-1, 0, 0]
    ]

    constellation_data["Gemini"] = [
        [0, 10923, 1395],  # /* move gem 1 */
        [1, 11246, 1350],  # /* draw gem eta */
        [1, 11488, 1350],  # /* draw gem mu */
        [1, 12117, 1507],  # /* draw gem epsilon */
        [1, 12934, 1814],  # /* draw gem tau */
        [1, 13473, 1907],  # /* draw gem rho */
        [1, 13638, 1913],  # /* draw castor */
        [0, 13959, 1681],  # /* move pollux */
        [1, 13677, 1613],  # /* draw gem upsilon */
        [1, 13203, 1318],  # /* draw gem delta */
        [1, 12723, 1234],  # /* draw gem zeta */
        [1, 11931, 983],  # /* draw gem gamma */
        [0, 12383, 2037],  # /* move gem theta */
        [1, 12934, 1814],  # /* draw gem tau */
        [1, 13336, 1658],  # /* draw gem 59 */
        [1, 13677, 1613],  # /* draw gem upsilon */
        [1, 13933, 1463],  # /* draw gem kappa */
        [0, 13203, 1318],  # /* move gem delta */
        [1, 13142, 992],  # /* draw gem lambda */
        [1, 13001, 969],  # /* draw gem 51 */
        [1, 13001, 969],  # /* draw gem 51 */
        [1, 12158, 773],  # /* draw gem xi */
        [0, 12117, 1507],  # /* move gem epsilon */
        [1, 11668, 1212],  # /* draw gem nu */
        [-1, 0, 0]
    ]

    constellation_data["Grus"] = [
        [0, 39417, -2241],  # /* move gamma */
        [1, 39783, -2372],  # /* draw lambda */
        [1, 40478, -2609],  # /* draw delta1 */
        [1, 40880, -2813],  # /* draw beta */
        [1, 41056, -3079],  # /* draw epsilon */
        [1, 41426, -3165],  # /* draw zeta */
        [0, 40880, -2813],  # /* move beta */
        [1, 39847, -2817],  # /* draw alpha */
        [1, 40478, -2609],  # /* draw delta1 */
        [-1, 0, 0]
    ]

    constellation_data["Hercules"] = [
        [0, 28580, 2547],  # /* move chi */
        [1, 29063, 2696],  # /* draw phi */
        [1, 29392, 2778],  # /* draw tau */
        [1, 29823, 2546],  # /* draw sigma */
        [1, 30086, 2335],  # /* draw eta */
        [1, 30038, 1896],  # /* draw zeta */
        [1, 29706, 1289],  # /* draw beta */
        [1, 29457, 1149],  # /* draw gamma */
        [1, 29562, 842],  # /* draw omega */
        [1, 29778, 689],  # /* draw 29 */
        [0, 29706, 1289],  # /* move beta */
        [1, 31039, 863],  # /* draw alpha */
        [1, 31050, 1490],  # /* draw delta */
        [1, 30608, 1855],  # /* draw epsilon */
        [1, 30038, 1896],  # /* draw zeta */
        [0, 31050, 1490],  # /* move delta */
        [1, 31522, 1566],  # /* draw lambda */
        [1, 31993, 1663],  # /* draw mu */
        [1, 32332, 1754],  # /* draw xi */
        [1, 32626, 1725],  # /* draw omicron */
        [0, 30608, 1855],  # /* move epsilon */
        [1, 31051, 2208],  # /* draw pi */
        [1, 30086, 2335],  # /* draw eta */
        [0, 31051, 2208],  # /* move pi */
        [1, 32287, 2235],  # /* draw theta */
        [1, 31783, 2760],  # /* draw iota */
        [-1, 0, 0]
    ]

    constellation_data["Horologium"] = [
        [0, 7620, -2537],  # /* move alpha */
        [1, 4876, -3048],  # /* draw iota */
        [1, 4722, -3152],  # /* draw eta */
        [1, 4819, -3273],  # /* draw zeta */
        [1, 5508, -3584],  # /* draw mu */
        [1, 5363, -3844],  # /* draw beta */
        [-1, 0, 0]
    ]

    constellation_data["Hydra"] = [
        [0, 26708, -1677],  # /* move 58 */
        [1, 25391, -1600],  # /* draw pi */
        [1, 23967, -1390],  # /* draw gamma */
        [1, 21387, -2034],  # /* draw beta */
        [1, 20790, -1911],  # /* draw xi */
        [1, 20149, -1369],  # /* draw crt beta */
        [1, 19793, -1097],  # /* draw crt alpha */
        [1, 19488, -971],  # /* draw nu */
        [1, 18782, -1010],  # /* draw mu */
        [1, 18317, -741],  # /* draw lambda */
        [1, 18153, -783],  # /* draw upsilon2 */
        [1, 17744, -890],  # /* draw upsilon1 */
        [1, 17027, -519],  # /* draw alpha */
        [1, 17395, -68],  # /* draw iota */
        [1, 16630, 138],  # /* draw theta */
        [1, 16061, 356],  # /* draw zeta */
        [1, 15803, 385],  # /* draw epsilon */
        [1, 15529, 342],  # /* draw delta */
        [1, 15562, 200],  # /* draw sigma */
        [1, 15696, 203],  # /* draw eta */
        [1, 15853, 350],  # /* draw rho */
        [1, 15803, 385],  # /* draw epsilon */
        [-1, 0, 0]
    ]

    constellation_data["Hydrus"] = [
        [0, 6817, -4454],  # /* move gamma */
        [1, 772, -4635],  # /* draw beta */
        [1, 3563, -3694],  # /* draw alpha */
        [1, 6817, -4454],  # /* draw gamma */
        [-1, 0, 0]
    ]

    constellation_data["Indus"] = [
        [0, 37644, -3507],  # /* move beta */
        [2, 37321, -3115],  # /* dotted eta */
        [2, 37127, -2837],  # /* dotted alpha */
        [2, 38396, -3206],  # /* dotted theta */
        [2, 39537, -3299],  # /* dotted delta */
        [-1, 0, 0]
    ]

    constellation_data["Lacerta"] = [
        [0, 40079, 2264],  # /* move 1 */
        [2, 40016, 2382],  # /* dotted 22:13:53 39:42:53 */
        [2, 40514, 2587],  # /* dotted 6 */
        [2, 40815, 2656],  # /* dotted 11 */
        [2, 40485, 2862],  # /* dotted 5 */
        [2, 40538, 3016],  # /* dotted alpha */
        [2, 40306, 3133],  # /* dotted beta */
        [2, 40335, 2968],  # /* dotted 4 */
        [2, 40485, 2862],  # /* dotted 5 */
        [2, 40230, 2792],  # /* dotted 2 */
        [2, 40514, 2587],  # /* dotted 6 */
        [-1, 0, 0]
    ]

    constellation_data["Leo"] = [
        [0, 18251, 718],  # /* move regulus */
        [1, 18220, 1005],  # /* draw eta */
        [1, 18599, 1190],  # /* draw gamma1 */
        [1, 18500, 1405],  # /* draw zeta */
        [1, 17782, 1560],  # /* draw mu */
        [1, 16939, 1570],  # /* draw kappa */
        [1, 17151, 1378],  # /* draw lambda */
        [1, 17575, 1426],  # /* draw epsilon */
        [1, 17782, 1560],  # /* draw mu */
        [0, 17575, 1426],  # /* move epsilon */
        [1, 18220, 1005],  # /* draw eta */
        [1, 20227, 925],  # /* draw theta */
        [1, 20517, 631],  # /* draw iota */
        [1, 20434, 361],  # /* draw sigma */
        [0, 20227, 925],  # /* move theta */
        [1, 21271, 874],  # /* draw beta */
        [1, 20223, 1231],  # /* draw delta */
        [1, 20227, 925],  # /* draw theta */
        [0, 20223, 1231],  # /* move delta */
        [1, 18599, 1190],  # /* draw gamma1 */
        [-1, 0, 0]
    ]

    constellation_data["Leo_Minor"] = [
        [0, 17226, 2183],  # /* move 10 */
        [2, 18222, 2114],  # /* dotted 21 */
        [2, 18777, 2027],  # /* dotted 30 */
        [2, 19599, 2052],  # /* dotted 46 */
        [2, 18836, 2202],  # /* dotted beta */
        [2, 18222, 2114],  # /* dotted 21 */
        [-1, 0, 0]
    ]

    constellation_data["Lepus"] = [
        [0, 9396, -776],  # /* move kappa */
        [1, 9387, -972],  # /* draw mu */
        [1, 9587, -790],  # /* draw lambda */
        [0, 9981, -1069],  # /* move alpha */
        [1, 9847, -1245],  # /* draw beta */
        [1, 10333, -1346],  # /* draw gamma */
        [1, 10539, -1252],  # /* draw delta */
        [1, 10984, -896],  # /* draw theta */
        [1, 10692, -850],  # /* draw eta */
        [1, 10408, -889],  # /* draw zeta */
        [1, 9981, -1069],  # /* draw alpha */
        [1, 9387, -972],  # /* draw mu */
        [1, 9163, -1342],  # /* draw epsilon */
        [1, 9847, -1245],  # /* draw beta */
        [-1, 0, 0]
    ]

    constellation_data["Libra"] = [
        [0, 27122, -1516],  # /* move sigma */
        [1, 26726, -962],  # /* draw alpha2 */
        [1, 27510, -562],  # /* draw beta */
        [1, 28065, -887],  # /* draw gamma */
        [1, 26726, -962],  # /* draw alpha2 */
        [0, 28065, -887],  # /* move gamma */
        [1, 28110, -1688],  # /* draw upsilon */
        [1, 28159, -1786],  # /* draw tau */
        [-1, 0, 0]
    ]

    constellation_data["Lupus"] = [
        [0, 26955, -2588],  # /* move beta */
        [1, 27641, -2438],  # /* draw delta */
        [1, 28054, -2470],  # /* draw gamma */
        [1, 28803, -2303],  # /* draw eta */
        [1, 28528, -2017],  # /* draw chi */
        [1, 27654, -2175],  # /* draw phi1 */
        [1, 28803, -2303],  # /* draw eta */
        [1, 27368, -3125],  # /* draw zeta */
        [1, 26457, -2843],  # /* draw alpha */
        [0, 27368, -3125],  # /* move zeta */
        [1, 27556, -2872],  # /* draw mu */
        [1, 27680, -2681],  # /* draw epsilon */
        [1, 28054, -2470],  # /* draw gamma */
        [-1, 0, 0]
    ]

    constellation_data["Lynx"] = [
        [0, 16831, 2063],  # /* move alpha */
        [2, 16765, 2208],  # /* dotted 38 */
        [2, 16396, 2307],  # /* dotted 9:06:32 38:27:08 */
        [2, 16219, 2506],  # /* dotted 9:00:38 41:46:58 */
        [2, 15085, 2591],  # /* dotted 31 */
        [2, 13401, 2952],  # /* dotted 21 */
        [2, 12518, 3505],  # /* dotted 15 */
        [2, 11388, 3540],  # /* dotted 2 */
        [-1, 0, 0]
    ]

    constellation_data["Lyra"] = [
        [0, 33743, 2256],  # /* move zeta1 */
        [1, 33730, 2380],  # /* draw epsilon1 */
        [1, 33508, 2327],  # /* draw vega */
        [1, 33743, 2256],  # /* draw zeta1 */
        [1, 33902, 2001],  # /* draw beta */
        [1, 34168, 1961],  # /* draw gamma */
        [1, 34035, 2213],  # /* draw delta2 */
        [1, 33743, 2256],  # /* draw zeta1 */
        [-1, 0, 0]
    ]

    constellation_data["Mensa"] = [
        [0, 11107, -4485],  # /* move alpha */
        [2, 9956, -4580],  # /* dotted gamma */
        [2, 8855, -4496],  # /* dotted eta */
        [2, 9081, -4278],  # /* dotted beta */
        [-1, 0, 0]
    ]

    constellation_data["Microscopium"] = [
        [0, 38422, -2448],  # /* move theta1 */
        [2, 38338, -1930],  # /* dotted epsilon */
        [2, 37838, -1935],  # /* dotted gamma */
        [2, 37499, -2026],  # /* dotted alpha */
        [-1, 0, 0]
    ]

    constellation_data["Monoceros"] = [
        [0, 12029, 593],  # /* move 15 */
        [2, 11787, 439],  # /* dotted 13 */
        [2, 11513, 275],  # /* dotted epsilon */
        [2, 12235, 144],  # /* dotted 18 */
        [2, 11787, 439],  # /* dotted 13 */
        [0, 12235, 144],  # /* move 18 */
        [2, 12955, -29],  # /* dotted delta */
        [2, 11664, -422],  # /* dotted beta */
        [1, 11245, -376],  # /* draw gamma */
        [0, 12955, -29],  # /* move delta */
        [2, 13837, -573],  # /* dotted alpha */
        [2, 14657, -179],  # /* dotted zeta */
        [-1, 0, 0]
    ]

    constellation_data["Musca"] = [
        [0, 21168, -4003],  # /* move lambda */
        [1, 22127, -4077],  # /* draw epsilon */
        [1, 22715, -4148],  # /* draw alpha */
        [1, 22574, -4327],  # /* draw gamma */
        [1, 23468, -4292],  # /* draw delta */
        [1, 22988, -4086],  # /* draw beta */
        [-1, 0, 0]
    ]

    constellation_data["Norma"] = [
        [0, 29615, -2853],  # /* move epsilon */
        [1, 29310, -3004],  # /* draw gamma1 */
        [1, 29395, -3009],  # /* draw gamma2 */
        [1, 28896, -2953],  # /* draw eta */
        [1, 28994, -2710],  # /* draw delta */
        [1, 29615, -2853],  # /* draw epsilon */
        [-1, 0, 0]
    ]

    constellation_data["Octans"] = [
        [0, 26007, -5020],  # /* move delta */
        [1, 39044, -4643],  # /* draw nu */
        [1, 40200, -4826],  # /* draw epsilon */
        [1, 40981, -4882],  # /* draw beta */
        [1, 26007, -5020],  # /* draw delta */
        [-1, 0, 0]
    ]

    constellation_data["Ophiuchus"] = [
        [0, 31420, -1792],  # /* move 45 */
        [1, 31260, -1499],  # /* draw theta */
        [1, 30911, -943],  # /* draw eta */
        [1, 29914, -634],  # /* draw zeta */
        [1, 29734, -996],  # /* draw phi */
        [1, 29610, -1107],  # /* draw chi */
        [1, 29523, -1202],  # /* draw psi */
        [1, 29567, -1406],  # /* draw rho */
        [0, 29914, -634],  # /* move zeta */
        [1, 29634, -502],  # /* draw upsilon */
        [1, 29349, -281],  # /* draw epsilon */
        [1, 29230, -221],  # /* draw delta */
        [1, 29727, 119],  # /* draw lambda */
        [1, 30530, 562],  # /* draw kappa */
        [1, 29914, -634],  # /* draw zeta */
        [0, 30530, 562],  # /* move kappa */
        [1, 31648, 753],  # /* draw alpha */
        [1, 31904, 274],  # /* draw beta */
        [1, 30911, -943],  # /* draw eta */
        [0, 31904, 274],  # /* move beta */
        [1, 32036, 162],  # /* draw gamma */
        [1, 32370, -586],  # /* draw nu */
        [-1, 0, 0]
    ]

    constellation_data["Orion"] = [
        [0, 11158, 852],  # /* move xi */
        [1, 11027, 886],  # /* draw nu */
        [1, 10631, 1216],  # /* draw chi1 */
        [1, 10917, 1208],  # /* draw chi2 */
        [1, 11158, 852],  # /* draw xi */
        [1, 10871, 578],  # /* draw mu */
        [1, 10655, 444],  # /* draw betelgeuse */
        [1, 9753, 380],  # /* draw gamma */
        [1, 10054, 596],  # /* draw lambda */
        [1, 10655, 444],  # /* draw betelgeuse */
        [1, 10222, -116],  # /* draw zeta */
        [1, 10432, -580],  # /* draw kappa */
        [0, 10222, -116],  # /* move zeta */
        [1, 10086, -72],  # /* draw epsilon */
        [1, 9960, -17],  # /* draw delta */
        [1, 9734, -143],  # /* draw eta */
        [1, 9436, -492],  # /* draw rigel */
        [0, 9960, -17],  # /* move delta */
        [1, 9753, 380],  # /* draw gamma */
        [1, 8695, 417],  # /* draw pi3 */
        [1, 8736, 336],  # /* draw pi4 */
        [1, 8827, 146],  # /* draw pi5 */
        [1, 8956, 102],  # /* draw pi6 */
        [0, 8695, 417],  # /* move pi3 */
        [1, 8718, 534],  # /* draw pi2 */
        [1, 8846, 609],  # /* draw pi1 */
        [1, 8891, 810],  # /* draw omicron2 */
        [1, 9137, 924],  # /* draw 11 */
        [-1, 0, 0]
    ]

    constellation_data["Pavo"] = [
        [0, 36017, -4374],  # /* move epsilon */
        [1, 36261, -3970],  # /* draw delta */
        [1, 33691, -4285],  # /* draw zeta */
        [0, 31971, -3883],  # /* move eta */
        [1, 32657, -3820],  # /* draw pi */
        [1, 33096, -3689],  # /* draw xi */
        [1, 33966, -3731],  # /* draw lambda */
        [1, 36261, -3970],  # /* draw delta */
        [1, 36769, -3404],  # /* draw alpha */
        [1, 38593, -3921],  # /* draw gamma */
        [1, 37348, -3972],  # /* draw beta */
        [1, 36261, -3970],  # /* draw delta */
        [1, 34108, -4034],  # /* draw kappa */
        [1, 32657, -3820],  # /* draw pi */
        [-1, 0, 0]
    ]

    constellation_data["Pegasus"] = [
        [0, 39125, 592],  # /* move epsilon */
        [1, 39906, 371],  # /* draw theta */
        [1, 40843, 649],  # /* draw zeta */
        [1, 41542, 912],  # /* draw alpha */
        [1, 397, 911],  # /* draw gamma */
        [1, 251, 1745],  # /* draw and alpha */
        [1, 41513, 1684],  # /* draw beta */
        [1, 41542, 912],  # /* draw alpha */
        [0, 39899, 1990],  # /* move pi2 */
        [1, 40890, 1813],  # /* draw eta */
        [1, 41513, 1684],  # /* draw beta */
        [1, 41100, 1476],  # /* draw mu */
        [1, 40995, 1413],  # /* draw lambda */
        [1, 39810, 1520],  # /* draw iota */
        [1, 39139, 1538],  # /* draw kappa */
        [-1, 0, 0]
    ]

    constellation_data["Perseus"] = [
        [0, 3109, 3041],  # /* move phi */
        [1, 4926, 2953],  # /* draw theta */
        [1, 5672, 2976],  # /* draw iota */
        [1, 5684, 2691],  # /* draw kappa */
        [1, 5645, 2457],  # /* draw algol */
        [1, 5555, 2330],  # /* draw rho */
        [0, 5645, 2457],  # /* move algol */
        [1, 7135, 2400],  # /* draw epsilon */
        [1, 7168, 2147],  # /* draw xi */
        [1, 7023, 1913],  # /* draw zeta */
        [1, 6729, 1937],  # /* draw omicron */
        [0, 7135, 2400],  # /* move epsilon */
        [1, 6687, 2867],  # /* draw delta */
        [1, 7459, 2862],  # /* draw 48 */
        [1, 7646, 2904],  # /* draw mu */
        [1, 7747, 3017],  # /* draw 4:18:15 50:17:44 */
        [1, 7397, 3021],  # /* draw lambda */
        [0, 6687, 2867],  # /* move delta */
        [1, 6129, 2991],  # /* draw alpha */
        [1, 5543, 3210],  # /* draw gamma */
        [1, 5120, 3353],  # /* draw eta */
        [1, 5227, 3165],  # /* draw tau */
        [1, 5672, 2976],  # /* draw iota */
        [1, 6129, 2991],  # /* draw alpha */
        [-1, 0, 0]
    ]

    constellation_data["Phoenix"] = [
        [0, 1982, -2803],  # /* move beta */
        [1, 282, -2744],  # /* draw epsilon */
        [1, 788, -2538],  # /* draw alpha */
        [1, 1982, -2803],  # /* draw beta */
        [1, 2650, -2599],  # /* draw gamma */
        [1, 2737, -2944],  # /* draw delta */
        [1, 2051, -3314],  # /* draw zeta */
        [1, 1982, -2803],  # /* draw beta */
        [-1, 0, 0]
    ]

    constellation_data["Pictor"] = [
        [0, 12245, -3716],  # /* move alpha */
        [2, 10494, -3370],  # /* dotted gamma */
        [2, 10418, -3063],  # /* dotted beta */
        [-1, 0, 0]
    ]

    constellation_data["Pisces"] = [
        [0, 1970, 1288],  # /* move psi1 */
        [1, 2384, 1635],  # /* draw upsilon */
        [1, 2149, 1805],  # /* draw tau */
        [1, 1970, 1288],  # /* draw psi1 */
        [1, 2143, 1262],  # /* draw chi */
        [1, 2744, 920],  # /* draw eta */
        [1, 3161, 549],  # /* draw omicron */
        [1, 3661, 165],  # /* draw alpha */
        [1, 3406, 191],  # /* draw xi */
        [1, 3042, 329],  # /* draw nu */
        [1, 2705, 368],  # /* draw mu */
        [1, 1888, 473],  # /* draw epsilon */
        [1, 1460, 455],  # /* draw delta */
        [1, 43179, 411],  # /* draw omega */
        [1, 42598, 337],  # /* draw iota */
        [1, 42239, 382],  # /* draw theta */
        [1, 41914, 196],  # /* draw gamma */
        [1, 42208, 75],  # /* draw kappa */
        [1, 42661, 106],  # /* draw lambda */
        [1, 42598, 337],  # /* draw iota */
        [-1, 0, 0]
    ]

    constellation_data["Piscis_Austrinus"] = [
        [0, 41329, -1777],  # /* move fomalhaut */
        [1, 40819, -1622],  # /* draw epsilon */
        [1, 39851, -1979],  # /* draw mu */
        [1, 39232, -1853],  # /* draw theta */
        [1, 39148, -1981],  # /* draw iota */
        [1, 39851, -1979],  # /* draw mu */
        [1, 40545, -1940],  # /* draw beta */
        [1, 41175, -1972],  # /* draw gamma */
        [1, 41278, -1952],  # /* draw delta */
        [1, 41329, -1777],  # /* draw fomalhaut */
        [-1, 0, 0]
    ]

    constellation_data["Puppis"] = [
        [0, 11518, -3161],  # /* move canopus */
        [1, 11932, -2591],  # /* draw nu */
        [1, 13114, -2225],  # /* draw pi */
        [1, 13906, -1704],  # /* draw 1 */
        [1, 13914, -1737],  # /* draw 3 */
        [1, 14078, -1491],  # /* draw xi */
        [1, 13764, -1608],  # /* draw 7:38:49 -26:48:06 */
        [1, 13906, -1704],  # /* draw 1 */
        [0, 14078, -1491],  # /* move xi */
        [1, 14626, -1458],  # /* draw rho */
        [1, 14507, -2400],  # /* draw zeta */
        [1, 14686, -2840],  # /* draw vel gamma2 */
        [-1, 0, 0]
    ]

    constellation_data["Pyxis"] = [
        [0, 15915, -1662],  # /* move gamma */
        [1, 15707, -1991],  # /* draw alpha */
        [1, 15603, -2118],  # /* draw beta */
        [1, 14507, -2400],  # /* draw pup zeta */
        [-1, 0, 0]
    ]

    constellation_data["Reticulum"] = [
        [0, 7632, -3748],  # /* move alpha */
        [1, 6726, -3888],  # /* draw beta */
        [1, 7162, -3684],  # /* draw delta */
        [1, 7694, -3558],  # /* draw epsilon */
        [1, 7632, -3748],  # /* draw alpha */
        [-1, 0, 0]
    ]

    constellation_data["Sagitta"] = [
        [0, 35402, 1080],  # /* move alpha */
        [1, 35621, 1112],  # /* draw delta */
        [1, 35962, 1169],  # /* draw gamma */
        [0, 35621, 1112],  # /* move delta */
        [1, 35431, 1048],  # /* draw beta */
        [-1, 0, 0]
    ]

    constellation_data["Sagittarius"] = [
        [0, 32928, -2205],  # /* move eta */
        [2, 33125, -2063],  # /* dotted epsilon */
        [1, 32574, -1825],  # /* draw gamma */
        [1, 33029, -1789],  # /* draw delta */
        [1, 33125, -2063],  # /* draw epsilon */
        [1, 34278, -1792],  # /* draw zeta */
        [1, 34408, -1660],  # /* draw tau */
        [1, 34057, -1577],  # /* draw sigma */
        [1, 33769, -1619],  # /* draw phi */
        [1, 34278, -1792],  # /* draw zeta */
        [0, 33239, -1525],  # /* move lambda */
        [1, 33769, -1619],  # /* draw phi */
        [1, 33029, -1789],  # /* draw delta */
        [1, 33239, -1525],  # /* draw lambda */
        [2, 32812, -1263],  # /* dotted mu */
        [0, 34850, -1070],  # /* move rho1 */
        [2, 34492, -1261],  # /* dotted pi */
        [2, 34340, -1304],  # /* dotted omicron */
        [2, 34131, -1266],  # /* dotted xi2 */
        [2, 34492, -1261],  # /* dotted pi */
        [-1, 0, 0]
    ]

    constellation_data["Scorpius"] = [
        [0, 32095, -2222],  # /* move 17:49:52 -37:02:36 */
        [1, 31608, -2226],  # /* draw lambda */
        [1, 31522, -2237],  # /* draw upsilon */
        [1, 31874, -2341],  # /* draw kappa */
        [1, 32027, -2407],  # /* draw iota1 */
        [1, 31719, -2579],  # /* draw theta */
        [1, 30964, -2594],  # /* draw eta */
        [1, 30437, -2541],  # /* draw zeta 2 */
        [1, 30356, -2282],  # /* draw mu 1 */
        [1, 30304, -2057],  # /* draw epsilon */
        [1, 29876, -1692],  # /* draw tau */
        [1, 29682, -1585],  # /* draw antares */
        [1, 29435, -1535],  # /* draw sigma */
        [1, 28810, -1357],  # /* draw delta */
        [1, 28765, -1566],  # /* draw pi */
        [1, 28706, -1752],  # /* draw rho */
        [0, 28810, -1357],  # /* move delta */
        [1, 28963, -1188],  # /* draw beta1 */
        [1, 29159, -1166],  # /* draw nu */
        [-1, 0, 0]
    ]

    constellation_data["Sculptor"] = [
        [0, 1758, -1761],  # /* move alpha */
        [1, 42867, -1687],  # /* draw delta */
        [1, 41964, -1951],  # /* draw gamma */
        [1, 42389, -2269],  # /* draw beta */
        [-1, 0, 0]
    ]

    constellation_data["Scutum"] = [
        [0, 33456, -494],  # /* move alpha */
        [1, 33815, -284],  # /* draw beta */
        [1, 33668, -543],  # /* draw delta */
        [1, 33275, -873],  # /* draw gamma */
        [1, 33456, -494],  # /* draw alpha */
        [-1, 0, 0]
    ]

    constellation_data["Serpens_Caput"] = [
        [0, 28385, 925],  # /* move ser beta */
        [1, 28693, 939],  # /* draw ser gamma */
        [1, 28462, 1088],  # /* draw ser kappa */
        [1, 28246, 1180],  # /* draw ser iota */
        [1, 28385, 925],  # /* draw ser beta */
        [1, 28044, 632],  # /* draw ser delta */
        [1, 28328, 385],  # /* draw ser alpha */
        [1, 28524, 268],  # /* draw ser epsilon */
        [1, 28488, -205],  # /* draw ser mu */
        [1, 29230, -221],  # /* draw oph delta */
        [-1, 0, 0]
    ]

    constellation_data["Serpens_Cauda"] = [
        [0, 34086, 252],  # /* move ser theta1 */
        [1, 33039, -173],  # /* draw ser eta */
        [1, 32370, -586],  # /* draw oph nu */
        [1, 31727, -923],  # /* draw ser xi */
        [1, 30911, -943],  # /* draw oph eta */
        [-1, 0, 0]
    ]

    constellation_data["Sextans"] = [
        [0, 18884, -164],  # /* move delta */
        [2, 18908, -38],  # /* dotted beta */
        [2, 18238, -22],  # /* dotted alpha */
        [2, 17775, -486],  # /* dotted gamma */
        [-1, 0, 0]
    ]

    constellation_data["Taurus"] = [
        [0, 6506, 24],  # /* move 10 */
        [1, 6144, 541],  # /* draw omicron */
        [1, 6215, 583],  # /* draw xi */
        [1, 7294, 359],  # /* draw nu */
        [0, 6215, 583],  # /* move xi */
        [1, 7220, 749],  # /* draw lambda */
        [1, 7793, 937],  # /* draw gamma */
        [1, 8057, 957],  # /* draw theta1 */
        [1, 8277, 990],  # /* draw aldebaran */
        [1, 10129, 1268],  # /* draw zeta */
        [0, 7793, 937],  # /* move gamma */
        [1, 7888, 1052],  # /* draw delta1 */
        [1, 7964, 1075],  # /* draw delta3 */
        [1, 8058, 1150],  # /* draw epsilon */
        [1, 9788, 1716],  # /* draw beta */
        [-1, 0, 0]
    ]

    constellation_data["Telescopium"] = [
        [0, 32736, -2757],  # /* move epsilon */
        [1, 33209, -2758],  # /* draw alpha */
        [1, 33264, -2944],  # /* draw zeta */
        [-1, 0, 0]
    ]

    constellation_data["Triangulum"] = [
        [0, 3392, 1774],  # /* move alpha */
        [1, 3886, 2099],  # /* draw beta */
        [1, 4119, 2030],  # /* draw gamma */
        [1, 3392, 1774],  # /* draw alpha */
        [-1, 0, 0]
    ]

    constellation_data["Triangulum_Australe"] = [
        [0, 30259, -4141],  # /* move alpha */
        [1, 28654, -3805],  # /* draw beta */
        [1, 28101, -3979],  # /* draw epsilon */
        [1, 27567, -4120],  # /* draw gamma */
        [1, 30259, -4141],  # /* draw alpha */
        [-1, 0, 0]
    ]

    constellation_data["Tucana"] = [
        [0, 40420, -3897],  # /* move delta */
        [1, 40155, -3615],  # /* draw alpha */
        [1, 41922, -3494],  # /* draw gamma */
        [1, 946, -3777],  # /* draw beta1 */
        [1, 602, -3892],  # /* draw zeta */
        [1, 43197, -3934],  # /* draw epsilon */
        [1, 40420, -3897],  # /* draw delta */
        [-1, 0, 0]
    ]

    constellation_data["Ursa_Major"] = [
        [0, 24826, 2958],  # /* move eta */
        [1, 24117, 3295],  # /* draw mizar a */
        [1, 23220, 3357],  # /* draw epsilon */
        [1, 22062, 3421],  # /* draw delta */
        [1, 21414, 3221],  # /* draw gamma */
        [1, 19855, 3382],  # /* draw beta */
        [1, 19911, 3705],  # /* draw alpha */
        [1, 22062, 3421],  # /* draw delta */
        [0, 21414, 3221],  # /* move gamma */
        [2, 21181, 2866],  # /* dotted chi */
        [2, 20354, 1985],  # /* dotted nu */
        [2, 20345, 1891],  # /* dotted xi */
        [0, 21181, 2866],  # /* move chi */
        [2, 20089, 2669],  # /* dotted psi */
        [2, 18669, 2489],  # /* dotted mu */
        [2, 18512, 2574],  # /* dotted lambda */
        [0, 19855, 3382],  # /* move beta */
        [2, 17729, 3542],  # /* dotted upsilon */
        [2, 15307, 3643],  # /* dotted omicron */
        [2, 17145, 3783],  # /* dotted 23 */
        [2, 19911, 3705],  # /* dotted alpha */
        [0, 17145, 3783],  # /* move 23 */
        [2, 17729, 3542],  # /* dotted upsilon */
        [2, 17185, 3100],  # /* dotted theta */
        [2, 16308, 2829],  # /* dotted kappa */
        [2, 16176, 2882],  # /* dotted iota */
        [-1, 0, 0]
    ]

    constellation_data["Ursa_Minor"] = [
        [0, 4554, 5355],  # /* move polaris */
        [1, 31566, 5195],  # /* draw umi delta */
        [1, 30179, 4922],  # /* draw umi epsilon */
        [1, 28321, 4667],  # /* draw umi zeta */
        [1, 26721, 4449],  # /* draw umi beta */
        [1, 27621, 4310],  # /* draw umi gamma */
        [1, 29325, 4545],  # /* draw umi eta */
        [1, 28321, 4667],  # /* draw umi zeta */
        [-1, 0, 0]
    ]

    constellation_data["Vela"] = [
        [0, 15741, -3282],  # /* move delta */
        [1, 16863, -3300],  # /* draw kappa */
        [1, 17905, -3274],  # /* draw phi */
        [1, 19403, -2965],  # /* draw mu */
        [1, 18442, -2527],  # /* draw 10:14:44 -42:07:20 */
        [1, 17121, -2428],  # /* draw psi */
        [1, 16439, -2605],  # /* draw lambda */
        [1, 14684, -2840],  # /* draw gamma1 */
        [1, 15741, -3282],  # /* draw delta */
        [-1, 0, 0]
    ]

    constellation_data["Virgo"] = [
        [0, 26491, -339],  # /* move mu */
        [1, 25680, -360],  # /* draw iota */
        [1, 24155, -669],  # /* draw spica */
        [1, 22849, -86],  # /* draw gamma */
        [1, 22197, -40],  # /* draw eta */
        [1, 21320, 105],  # /* draw beta */
        [1, 21175, 391],  # /* draw nu */
        [1, 21756, 523],  # /* draw omicron */
        [1, 22849, -86],  # /* draw gamma */
        [1, 23268, 203],  # /* draw delta */
        [1, 23465, 657],  # /* draw epsilon */
        [0, 23268, 203],  # /* move delta */
        [1, 24440, -35],  # /* draw zeta */
        [1, 24155, -669],  # /* draw spica */
        [0, 24440, -35],  # /* move zeta */
        [1, 25249, 92],  # /* draw tau */
        [1, 25680, -360],  # /* draw iota */
        [0, 25249, 92],  # /* move tau */
        [1, 26587, 113],  # /* draw 109 */
        [-1, 0, 0]
    ]

    constellation_data["Volans"] = [
        [0, 16273, -3983],  # /* move alpha */
        [1, 14994, -4290],  # /* draw kappa1 */
        [1, 13854, -4356],  # /* draw zeta */
        [1, 12861, -4229],  # /* draw gamma1 */
        [1, 13104, -4077],  # /* draw delta */
        [1, 14637, -4117],  # /* draw epsilon */
        [1, 15172, -3968],  # /* draw beta */
        [1, 16273, -3983],  # /* draw alpha */
        [-1, 0, 0]
    ]

    constellation_data["Vulpecula"] = [
        [0, 35803, 1444],  # /* move 13 */
        [2, 35061, 1479],  # /* dotted alpha */
        [-1, 0, 0]
    ]

    for name, point_list in constellation_data.items():
        points = np.asarray(point_list)

        drawtype = points[:, 0]
        ra_degrees = points[:, 1] * 1.0 / 1800 * 15
        dec_degrees = points[:, 2] * 1.0 / 60

        lines = []
        for i in range(0, len(drawtype) - 1):
            if drawtype[i] == 0:
                continue  # don't draw lines, just move for type 0
            if plot:
                lines.append(pylab.plot(ra_degrees[i - 1:(i) + 1], dec_degrees[i - 1:(i) + 1],
                                        linestyle=':' if drawtype[i] == 2 else "-",
                                        color=color))
            elif plot3d:
                ras = ra_degrees[i - 1:(i) + 1]
                decs = dec_degrees[i - 1:(i) + 1]
                xs, ys, zs = radec2xyz(radius, ras, decs)
                ax = pylab.gca()
                lines.append(ax.plot(xs, ys, zs, linestyle=':' if drawtype[i] == 2 else "-",
                                     color=color))

    if plot3d and greatcircles:
        pts = 45
        xs, ys, zs = radec2xyz(radius, np.linspace(0, 360, pts), np.zeros(pts))
        lines.append(ax.plot(xs, ys, zs, linestyle='-', color='black'))

        xs, ys, zs = radec2xyz(radius, np.zeros(pts), np.linspace(-90, 90, pts))
        lines.append(ax.plot(xs, ys, zs, linestyle=':', color='black'))

    if plot is False and plot3d is False:
        return constellation_data
    else:
        return lines


def radec2xyz(radius, ra, dec, degrees=True):
    northpole = 90 if degrees else np.pi
    return polrec3d(radius, northpole - dec, ra, degrees=degrees)


def polrec(r, a, degrees=False):
    """Convert 2-d polar coordinates to rectangular coordinates.
    Based on IDL JHUAPL lib's polrec.pro

    """
    cf = 1.e0
    if degrees: cf = 180 / np.pi

    x = r * np.cos(a / cf)
    y = r * np.sin(a / cf)
    return x, y


def polrec3d(radius, az, ax, degrees=False):
    """Convert vector(s) from spherical polar to rectangular form.
        Based on IDL JHUAPL lib's polrec3d.pro
    """
    z, rxy = polrec(radius, az, degrees=degrees)
    x, y = polrec(rxy, ax, degrees=degrees)
    return x, y, z


def demo3d(ax=None, radius=1):
    from mpl_toolkits.mplot3d import Axes3D

    for i in range(3):
        try:
            pylab.clf()
        except:
            pass
            # need to create X, Y, Z arrays each of which can be 2D for the surface connectivity.
    if ax is None:
        ax = pylab.subplot(111, projection='3d', aspect='equal')
        ax.set_xlim3d(-radius, radius)
        ax.set_ylim3d(-radius, radius)
        ax.set_zlim3d(-radius, radius)

    constellations(plot3d=True, radius=radius)


if __name__ == "__main__":
    constellations(plot=True)
    # demo3d()
