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
import pytest
import os

# external packages
from skyfield.api import Angle, wgs84
import numpy as np

# local imports
from mountcontrol.mount import Mount
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function():
    m = Mount(host='192.168.2.15',
              pathToData=os.getcwd() + '/data',
              verbose=True)
    m.obsSite.location = wgs84.latlon(latitude_degrees=90,
                                      longitude_degrees=11,
                                      elevation_m=500)
    yield m


def test_properties_1(function):
    function.geometry.initializeGeometry('10micron GM1000HPS')
    function.geometry.offVert = 0.10
    val = function.geometry.offVertGEM
    assert val == function.geometry.offAltAxisGemX + function.geometry.offBaseAltAxisZ + 0.1


def test_properties_2(function):
    function.geometry.initializeGeometry('10micron GM1000HPS')
    function.geometry.offVertGEM = 0.10
    val = function.geometry.offVert
    assert val == 0.1 - function.geometry.offAltAxisGemX - function.geometry.offBaseAltAxisZ


def test_properties_3(function):
    function.obsSite.location = None
    function.geometry.initializeGeometry('10micron GM1000HPS')
    function.geometry.offVert = 0.10
    val = function.geometry.offVertGEM
    assert val == 0


def test_properties_4(function):
    function.obsSite.location = None
    function.geometry.initializeGeometry('10micron GM1000HPS')
    function.geometry.offVertGEM = 0.10
    val = function.geometry.offVert
    assert val == 0


def test_properties_5(function):
    function.geometry.initializeGeometry('10micron GM1000HPS')
    function.geometry.offGEM = 0.10
    val = function.geometry.offPlateOTA
    assert val == 0.1 - function.geometry.offGemPlate


def test_properties_6(function):
    function.geometry.initializeGeometry('10micron GM1000HPS')
    function.geometry.offPlateOTA = 0.10
    val = function.geometry.offGEM
    assert val == 0.1 + function.geometry.offGemPlate


def test_initializeGeometry_1(function):
    suc = function.geometry.initializeGeometry('')
    assert not suc


def test_initializeGeometry_2(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    assert suc


def test_transformRotX_1(function):
    function.geometry.transformRotX(90, degrees=True)


def test_transformRotX_2(function):
    function.geometry.transformRotX(np.pi)


def test_transformRotX_3(function):
    function.geometry.transformRotX(Angle(degrees=90))


def test_transformRotY_1(function):
    function.geometry.transformRotY(90, degrees=True)


def test_transformRotY_2(function):
    function.geometry.transformRotY(np.pi)


def test_transformRotY_3(function):
    function.geometry.transformRotY(Angle(degrees=90))


def test_transformRotZ_1(function):
    function.geometry.transformRotZ(90, degrees=True)


def test_transformRotZ_2(function):
    function.geometry.transformRotZ(np.pi)


def test_transformRotZ_3(function):
    function.geometry.transformRotZ(Angle(degrees=90))


def test_transformTranslate(function):
    function.geometry.transformTranslate([1, 2, 3])


def test_geometry_1(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    assert suc

    testValues = [[0, 0, 'E'],
                  [0, 6, 'E'],
                  [0, 12, 'E'],
                  [0, 18, 'E'],
                  [45, 0, 'E'],
                  [45, 6, 'E'],
                  [45, 12, 'E'],
                  [45, 18, 'E'],
                  [0, 0, 'W'],
                  [0, 6, 'W'],
                  [0, 12, 'W'],
                  [0, 18, 'W'],
                  [45, 0, 'W'],
                  [45, 6, 'W'],
                  [45, 12, 'W'],
                  [45, 18, 'W']]

    results = [
        [66.44185978925006, 149.97346503050713, -0.5190599405657699, -0.3, 1.3749824646517712],
        [32.64394199335745, 277.0628240594122, 0.15530261156223288, 1.253474243076767, 0.8091250958813949],
        [-11.23447830354821, 3.8973463992387267, 1.4678547546268246, -0.09999999999999992, -0.2922369232650526],
        [26.982074361307575, 76.65600567625405, 0.3085115001860286, -1.3006338576051393, 0.6805675739440871],
        [75.43055465342745, 52.66094667091431, 0.22886207517933305, -0.3, 1.451765184368536],
        [61.97490856498502, 326.4582725751, 0.5874286629495312, 0.38942608187570793, 1.324112870075758],
        [36.33302655633136, 4.746963975677392, 1.204235469568233, -0.09999999999999998, 0.8887164530004933],
        [48.9641314856381, 45.777350793074724, 0.6868451714046551, -0.7057399943437717, 1.1314480858182416],
        [52.167235157848516, 173.76012909293414, -0.9145875074677009, -0.0999999999999998, 1.1847065844267173],
        [14.443974296346557, 272.0277014555817, 0.05139645631141295, 1.4516784540353969, 0.3741497966964957],
        [-26.83859723959295, 12.952571757220932, 1.3043679144561846, -0.30000000000000016, -0.6772180917084414],
        [19.580942787000705, 94.13123370173234, -0.10181243231238284, -1.4095813493440696, 0.5027073186338036],
        [82.25469447816607, 150.35195047733998, -0.17568861329024138, -0.09999999999999987, 1.4863154144259394],
        [46.28565118511222, 308.6340496155167, 0.6471918974509034, 0.8097358761901345, 1.0841911541257354],
        [19.57897947917161, 12.255622023346525, 1.3810626483845556, -0.3000000000000001, 0.5026588915328539],
        [44.68070761603261, 70.19373766333975, 0.3613921036572813, -1.0034610457924462, 1.054732988481585],
    ]

    for t, r in zip(testValues, results):
        val = function.geometry.calcTransformationMatrices(dec=Angle(degrees=t[0]),
                                                           ha=Angle(hours=t[1]),
                                                           lat=Angle(degrees=50),
                                                           pierside=t[2])
        alt, az, inter, _, _ = val
        assert pytest.approx(alt.degrees, 0.001) == r[0]
        assert pytest.approx(az.degrees, 0.001) == r[1]
        assert pytest.approx(inter[0], 0.001) == r[2]
        assert pytest.approx(inter[1], 0.001) == r[3]
        assert pytest.approx(inter[2], 0.001) == r[4]


def test_geometry_2(function):
    suc = function.geometry.initializeGeometry('10micron GM2000HPS')
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    assert suc

    testValues = [[0, 0, 'E'],
                  [0, 6, 'E'],
                  [0, 12, 'E'],
                  [0, 18, 'E'],
                  [45, 0, 'E'],
                  [45, 6, 'E'],
                  [45, 12, 'E'],
                  [45, 18, 'E'],
                  [0, 0, 'W'],
                  [0, 6, 'W'],
                  [0, 12, 'W'],
                  [0, 18, 'W'],
                  [45, 0, 'W'],
                  [45, 6, 'W'],
                  [45, 12, 'W'],
                  [45, 18, 'W']]

    results = [
        [70.80770829267118, 142.52723263975065, -0.39135261407372224, -0.3, 1.4166309086906386],
        [36.032456225608286, 281.66981936936105, 0.24536051097011805, 1.1879519954712587, 0.8823651603006188],
        [-6.137481263351689, 3.844623125254006, 1.4880459986437942, -0.09999999999999992, -0.16037177407572112],
        [30.168083468435462, 72.10095612985542, 0.3985693995939137, -1.234065021809011, 0.753807638363311],
        [72.7923492049923, 42.535830675707174, 0.326981787908409, -0.3, 1.4328583008714506],
        [62.54185976578476, 334.03341577881554, 0.6218282313187004, 0.302837090115493, 1.3310219185217942],
        [39.29194239379899, 4.941612156358691, 1.1565788680236344, -0.09999999999999998, 0.9499080597832448],
        [49.9489502927716, 40.90394809445047, 0.7295098734884461, -0.6320092680355813, 1.1482071370619502],
        [56.647892567619955, 173.03517210441663, -0.8185886147676187, -0.0999999999999998, 1.2529615635656315],
        [17.353119068532784, 275.67006225196087, 0.14145435571929807, 1.424722070236471, 0.4473898611157196],
        [-22.352280079988912, 12.48876805445253, 1.3544690563632393, -0.30000000000000016, -0.5704503268072305],
        [22.579496379556282, 90.4862691307081, -0.011754532904497692, -1.3849716397495533, 0.5759473830530275],
        [85.10381420115498, 128.63933412813847, -0.07994141283684915, -0.09999999999999987, 1.4945264703288625],
        [47.43609870939129, 313.0855024543074, 0.6930744592534863, 0.7410112509179632, 1.1047851012497785],
        [22.162890485617243, 12.471612466584716, 1.356392531822995, -0.3000000000000001, 0.5658615551659302],
        [46.358622336707505, 66.31705071056868, 0.41581966411851917, -0.9480300785340344, 1.0855104684557926],
    ]

    for t, r in zip(testValues, results):
        val = function.geometry.calcTransformationMatrices(dec=Angle(degrees=t[0]),
                                                           ha=Angle(hours=t[1]),
                                                           lat=Angle(degrees=50),
                                                           pierside=t[2])
        alt, az, inter, _, _ = val
        assert pytest.approx(alt.degrees, 0.001) == r[0]
        assert pytest.approx(az.degrees, 0.001) == r[1]
        assert pytest.approx(inter[0], 0.001) == r[2]
        assert pytest.approx(inter[1], 0.001) == r[3]
        assert pytest.approx(inter[2], 0.001) == r[4]


def test_geometry_3(function):
    suc = function.geometry.initializeGeometry('10micron GM3000HPS')
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    assert suc

    testValues = [[0, 0, 'E'],
                  [0, 6, 'E'],
                  [0, 12, 'E'],
                  [0, 18, 'E'],
                  [45, 0, 'E'],
                  [45, 6, 'E'],
                  [45, 12, 'E'],
                  [45, 18, 'E'],
                  [0, 0, 'W'],
                  [0, 6, 'W'],
                  [0, 12, 'W'],
                  [0, 18, 'W'],
                  [45, 0, 'W'],
                  [45, 6, 'W'],
                  [45, 12, 'W'],
                  [45, 18, 'W']]

    results = [
        [73.47485083517182, 135.32008931965703, -0.3033708341295227, -0.3, 1.4380424670361989],
        [39.919288145996596, 283.22991329034744, 0.2632849799416239, 1.1198909921568878, 0.9625617824446386],
        [-2.7112235260291926, 3.826843760645391, 1.4949801491272452, -0.09999999999999992, -0.07095317974185367],
        [33.77981574347255, 70.48472561551986, 0.4164938685654196, -1.1751466933549324, 0.8340042605073308],
        [72.02746234466576, 40.40375612961661, 0.3524519914517699, -0.3, 1.4268067821964125],
        [64.81075973270924, 338.6397145250526, 0.5945604316614652, 0.2325304010198841, 1.357360492170029],
        [42.996600072407524, 5.229776118935934, 1.0925242432175382, -0.09999999999999998, 1.0229324405755957],
        [52.29875188299453, 39.034848598424226, 0.7125374960614124, -0.5777194126110852, 1.186815317140302],
        [59.56657869972119, 172.43720691263505, -0.7531958075394927, -0.09999999999999981, 1.293327520585923],
        [20.59281868373743, 276.51740987418833, 0.15937882469080397, 1.3950809628554892, 0.5275864832597394],
        [-19.419544200305225, 12.243364591087909, 1.3824883684085265, -0.30000000000000016, -0.4987242837632131],
        [25.93997738918759, 89.73792127992488, 0.006169936067008153, -1.3488650697282165, 0.6561440051970473],
        [85.6346227748226, 118.85423870178909, -0.05509880427354373, -0.09999999999999988, 1.495648395100809],
        [49.82191207458456, 314.50328074962806, 0.6783432741506076, 0.6902080717927317, 1.1460642303321367],
        [25.31986752987029, 12.782756835850506, 1.322296779086865, -0.3000000000000001, 0.6415069976364266],
        [48.85257185332797, 65.8767717531516, 0.40338665817223857, -0.9008022314811168, 1.1295284608044516],
    ]

    for t, r in zip(testValues, results):
        val = function.geometry.calcTransformationMatrices(dec=Angle(degrees=t[0]),
                                                           ha=Angle(hours=t[1]),
                                                           lat=Angle(degrees=50),
                                                           pierside=t[2])
        alt, az, inter, _, _ = val
        assert pytest.approx(alt.degrees, 0.001) == r[0]
        assert pytest.approx(az.degrees, 0.001) == r[1]
        assert pytest.approx(inter[0], 0.001) == r[2]
        assert pytest.approx(inter[1], 0.001) == r[3]
        assert pytest.approx(inter[2], 0.001) == r[4]


def test_geometry_4(function):
    suc = function.geometry.initializeGeometry('10micron GM4000HPS')
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    assert suc

    testValues = [[0, 0, 'E'],
                  [0, 6, 'E'],
                  [0, 12, 'E'],
                  [0, 18, 'E'],
                  [45, 0, 'E'],
                  [45, 6, 'E'],
                  [45, 12, 'E'],
                  [45, 18, 'E'],
                  [0, 0, 'W'],
                  [0, 6, 'W'],
                  [0, 12, 'W'],
                  [0, 18, 'W'],
                  [45, 0, 'W'],
                  [45, 6, 'W'],
                  [45, 12, 'W'],
                  [45, 18, 'W']]

    results = [
        [75.59719357876492, 126.48032637101706, -0.22182894929142927, -0.3, 1.4528564682226046],
        [43.045270444108475, 285.3087209857523, 0.2894243604259508, 1.057324945168361, 1.0238640046005874],
        [0.41650100408347557, 3.82265487908081, 1.4966232343229562, -0.09999999999999992, 0.010903874755982312],
        [36.64612586348536, 68.42082786427862, 0.44263324904974655, -1.1191524064830367, 0.8953064826632795],
        [71.02090485989088, 37.94918597871115, 0.38468522470121863, -0.3, 1.418455948521692],
        [66.15773077679029, 343.55914910920643, 0.5815389052306246, 0.1716068450504954, 1.3719925628205796],
        [45.90410281420002, 5.497626792904525, 1.0389907885851333, -0.09999999999999999, 1.0772641928678603],
        [53.871943266219844, 36.81756964307354, 0.7079946637269241, -0.5299863630680525, 1.211551901940688],
        [62.15838578538358, 171.79320515195923, -0.69336944011709, -0.09999999999999981, 1.3263630044266592],
        [23.115906949699934, 277.72829170216954, 0.18551820517513087, 1.3670380712264134, 0.5888887054156884],
        [-16.807489928723086, 12.059357022209353, 1.404234166859495, -0.30000000000000016, -0.4337354085435261],
        [28.574266989393426, 88.59456646054936, 0.032309316551335086, -1.3169005349383598, 0.7174462273529962],
        [86.07167175411232, 103.31604137399296, -0.0236685622417237, -0.0999999999999999, 1.4964757930422428],
        [51.45714234351279, 316.3092094592861, 0.6758248734232669, 0.645624478736788, 1.1732134387733018],
        [27.73143506329075, 13.058944892717603, 1.2933706763434056, -0.3000000000000001, 0.6979916142583672],
        [50.66457675260098, 64.86826067011935, 0.40380094402567956, -0.8607810888156088, 1.1601727090142162],
    ]

    for t, r in zip(testValues, results):
        val = function.geometry.calcTransformationMatrices(dec=Angle(degrees=t[0]),
                                                           ha=Angle(hours=t[1]),
                                                           lat=Angle(degrees=50),
                                                           pierside=t[2])
        alt, az, inter, _, _ = val
        assert pytest.approx(alt.degrees, 0.001) == r[0]
        assert pytest.approx(az.degrees, 0.001) == r[1]
        assert pytest.approx(inter[0], 0.001) == r[2]
        assert pytest.approx(inter[1], 0.001) == r[3]
        assert pytest.approx(inter[2], 0.001) == r[4]


def test_geometry_5(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    assert suc
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    val = function.geometry.calcTransformationMatrices(ha=None,
                                                       dec=None,
                                                       lat=None,
                                                       pierside='E')
    alt, az, inter, PB, PD = val
    assert alt is None
    assert az is None
    assert inter is None
    assert PB is None
    assert PD is None


def test_geometry_6(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    assert suc
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    val = function.geometry.calcTransformationMatrices(ha=Angle(hours=1),
                                                       dec=None,
                                                       lat=None,
                                                       pierside='E')
    alt, az, inter, PB, PD = val
    assert alt is None
    assert az is None
    assert inter is None
    assert PB is None
    assert PD is None


def test_geometry_7(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    assert suc
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    val = function.geometry.calcTransformationMatrices(ha=Angle(hours=1),
                                                       dec=Angle(degrees=1),
                                                       lat=None,
                                                       pierside='E')
    alt, az, inter, PB, PD = val
    assert alt is None
    assert az is None
    assert inter is None
    assert PB is None
    assert PD is None


def test_geometry_8(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    assert suc
    function.geometry.offNorth = 0
    function.geometry.offEast = 0
    function.geometry.offVert = 0
    function.geometry.offGEM = 0
    function.geometry.offLAT = 0.5
    function.geometry.domeRadius = 0.25

    val = function.geometry.calcTransformationMatrices(ha=Angle(hours=1),
                                                       dec=Angle(degrees=1),
                                                       lat=Angle(degrees=49),
                                                       pierside='E')
    alt, az, inter, PB, PD = val
    assert alt is None
    assert az is None
    assert inter is None
    assert PB is None
    assert PD is None


def test_geometry_9(function):
    suc = function.geometry.initializeGeometry('10micron GM1000HPS')
    assert suc
    function.geometry.offNorth = 0.1
    function.geometry.offEast = 0.2
    function.geometry.offVert = 0.3
    function.geometry.offGEM = 0.1
    function.geometry.offLAT = 0.2
    function.geometry.domeRadius = 1.5

    val = function.geometry.calcTransformationMatrices(dec=Angle(degrees=10),
                                                       ha=Angle(hours=5),
                                                       lat=Angle(degrees=-50),
                                                       pierside='E')
    alt, az, inter, _, _ = val
