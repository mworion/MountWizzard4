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
# Licence APL2.0
#
###########################################################

import pytest
from mw4.logic.buildData.alignstars import generateAlignStars

EXPECTED_STAR_COUNT = 101
EXPECTED_VALUE_LENGTH = 6

EXPECTED_KEYS = {
    "Achernar",
    "Acrux",
    "Adhara",
    "Albireo",
    "Alcor",
    "Aldebaran",
    "Alderamin",
    "Algenib",
    "Algieba",
    "Algol",
    "Alhena",
    "Alioth",
    "Alkaid",
    "Almach",
    "Alnair",
    "Alnilam",
    "Alnitak",
    "Alphard",
    "Alpheratz",
    "Altair",
    "Aludra",
    "Ankaa",
    "Antares",
    "Arcturus",
    "Atria",
    "Avior",
    "Becrux",
    "Bellatrix",
    "Betelgeuse",
    "Birdun",
    "Canopus",
    "Capella",
    "Caph",
    "Castor",
    "Deneb",
    "Denebola",
    "Diphda",
    "Dschubba",
    "Dubhe",
    "Durre Menthor",
    "Elnath",
    "Enif",
    "Etamin",
    "Fomalhaut",
    "Foramen",
    "Gacrux",
    "Gemma",
    "Gienah",
    "Girtab",
    "Gruid",
    "Hadar",
    "Hamal",
    "Herschel Star",
    "Izar",
    "Kaus Australis",
    "Kochab",
    "Koo She",
    "Marchab",
    "Marfikent",
    "Markab",
    "Megrez",
    "Men",
    "Menkalinan",
    "Menkent",
    "Merak",
    "Miaplacidus",
    "Mintaka",
    "Mira",
    "Mirach",
    "Mirzam",
    "Mizar",
    "Muhlifein",
    "Naos",
    "Nunki",
    "Peacock",
    "Phad",
    "Polaris",
    "Pollux",
    "Procyon",
    "Rasalhague",
    "Regor",
    "Regulus",
    "Rigel",
    "Sabik",
    "Sadira",
    "Sadr",
    "Saiph",
    "Scheat",
    "Schedar",
    "Shaula",
    "Sirius",
    "South Star",
    "Spica",
    "Suhail",
    "Thuban",
    "Toliman",
    "Tsih",
    "Turais",
    "Vega",
    "Wei",
    "Wezen",
}


@pytest.fixture(scope="module")
def alignStars():
    return generateAlignStars()


def test_returnType(alignStars):
    assert isinstance(alignStars, dict)


def test_starCount(alignStars):
    assert len(alignStars) == EXPECTED_STAR_COUNT


def test_keySet(alignStars):
    assert set(alignStars.keys()) == EXPECTED_KEYS


def test_allKeysAreStrings(alignStars):
    for key in alignStars:
        assert isinstance(key, str)


def test_allValuesAreLists(alignStars):
    for name, value in alignStars.items():
        assert isinstance(value, list), f"Entry '{name}' is not a list"


def test_allValueLengths(alignStars):
    for name, value in alignStars.items():
        assert len(value) == EXPECTED_VALUE_LENGTH, (
            f"Entry '{name}' has {len(value)} elements, expected {EXPECTED_VALUE_LENGTH}"
        )


def test_allValueElementsAreFloats(alignStars):
    for name, value in alignStars.items():
        for idx, elem in enumerate(value):
            assert isinstance(elem, float), f"Entry '{name}'[{idx}] = {elem!r} is not a float"
