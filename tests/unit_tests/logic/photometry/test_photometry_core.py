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

import mw4.logic.photometry.photometry_core
import numpy as np
from mw4.logic.photometry.photometry_core import (
    Background,
    Sources,
    estimateBackground,
    extractSources,
)
from unittest import mock


def starField(size: int = 200) -> np.ndarray:
    np.random.seed(1)
    img = np.random.rand(size, size).astype(np.float32) + 100.0
    yy, xx = np.mgrid[0:size, 0:size]
    stars = [
        (50, 60),
        (150, 120),
        (120, 40),
        (90, 160),
        (40, 100),
        (160, 40),
        (40, 160),
        (110, 180),
        (170, 150),
        (70, 110),
        (150, 180),
        (110, 90),
    ]
    for cx, cy in stars:
        img += 3000 * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * 2.0**2))
    return img


def test_background():
    img = np.random.rand(200, 200) + 100
    bkg = Background(img)
    assert bkg.back().shape == (200, 200)
    assert bkg.rms().shape == (200, 200)
    assert bkg.globalback > 0
    assert bkg.globalrms >= 0


def test_estimateBackground():
    img = np.random.rand(200, 200) + 100
    bkg = estimateBackground(img)
    assert isinstance(bkg, Background)


def test_sources_len():
    s = Sources(
        xCoord=np.zeros(3),
        yCoord=np.zeros(3),
        aAxis=np.zeros(3),
        bAxis=np.zeros(3),
        theta=np.zeros(3),
        hfr=np.zeros(3),
        elongation=np.zeros(3),
    )
    assert len(s) == 3


def test_extractSources_success():
    img = starField().astype(np.float32)
    bkg = Background(img)
    sub = img - bkg.back()
    threshold = 2.0 * bkg.rms()
    result = extractSources(sub, bkg.rms(), threshold, 5)
    assert result is not None
    sources, counts = result
    assert isinstance(sources, Sources)
    assert len(sources) > 0
    assert len(sources.xCoord) == len(sources.hfr)
    assert counts.raw >= counts.select >= counts.signalNoise >= counts.hfr


def test_extractSources_noSources():
    img = np.zeros((100, 100), dtype=np.float32)
    with mock.patch.object(
        mw4.logic.photometry.photometry_core, "detect_sources", return_value=None
    ):
        result = extractSources(img, np.ones((100, 100)), np.ones((100, 100)), 5)
    assert result is None
