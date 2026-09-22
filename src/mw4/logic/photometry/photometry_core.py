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
"""Pure numeric photometry core without any Qt dependency.

The functions and value objects in this module perform background estimation
and source extraction on an image and return plain NumPy arrays. They contain
no Qt signals and no presentation state, so they can be tested and optimised
in isolation from the GUI adapter.
"""

import astropy.units as u
import numpy as np
from astropy.stats import SigmaClip
from dataclasses import dataclass
from photutils.background import Background2D, MeanBackground, StdBackgroundRMS
from photutils.segmentation import SourceCatalog, detect_sources


class Background:
    """Adapter exposing a simple background interface on top of photutils
    Background2D. The parameters are tuned for a fast background estimate at a
    reasonable quality level (MeanBackground on 64 px boxes with a light
    sigma-clip).
    """

    def __init__(self, image: np.ndarray) -> None:
        bkg = Background2D(
            image,
            box_size=(64, 64),
            filter_size=(3, 3),
            sigma_clip=SigmaClip(sigma=3.0, maxiters=3),
            bkg_estimator=MeanBackground(),
            bkg_rms_estimator=StdBackgroundRMS(),
        )
        self.background: np.ndarray = bkg.background
        self.backgroundRMS: np.ndarray = bkg.background_rms
        self.globalback: float = float(bkg.background_median)
        self.globalrms: float = float(bkg.background_rms_median)

    def back(self) -> np.ndarray:
        return self.background

    def rms(self) -> np.ndarray:
        return self.backgroundRMS


@dataclass
class Sources:
    """Container for extracted source properties as flat, index-aligned arrays.

    Consumers use plain attribute access instead of structured-array field
    indexing.
    """

    xCoord: np.ndarray
    yCoord: np.ndarray
    aAxis: np.ndarray
    bAxis: np.ndarray
    theta: np.ndarray
    hfr: np.ndarray
    elongation: np.ndarray

    def __len__(self) -> int:
        return len(self.hfr)


@dataclass
class ExtractCounts:
    """Number of sources surviving each successive selection stage."""

    raw: int
    select: int
    signalNoise: int
    hfr: int


def estimateBackground(image: np.ndarray) -> Background:
    return Background(image)


def extractSources(
    imageSub: np.ndarray,
    backRMS: np.ndarray,
    threshold: np.ndarray,
    snTarget: float,
) -> tuple[Sources, ExtractCounts] | None:
    """Detect and measure sources on a background-subtracted image.

    Returns the surviving sources together with per-stage counts, or ``None``
    when no sources are detected at all.
    """
    segments = detect_sources(imageSub, threshold, n_pixels=7)
    if segments is None:
        return None

    catalog = SourceCatalog(imageSub, segments, error=backRMS)
    # 8.1: SourceCatalog replaces kron_radius/sum_ellipse/sum_circle/flux_radius
    flux = np.asarray(catalog.kron_flux, dtype=float)
    fluxErr = np.asarray(catalog.kron_flux_err, dtype=float)
    hfr = np.asarray(catalog.flux_radius(0.5).value, dtype=float)
    elongation = np.asarray(catalog.elongation, dtype=float)
    xCoord = np.asarray(catalog.x_centroid, dtype=float)
    yCoord = np.asarray(catalog.y_centroid, dtype=float)
    aAxis = np.asarray(catalog.semimajor_axis.value, dtype=float)
    bAxis = np.asarray(catalog.semiminor_axis.value, dtype=float)
    theta = np.asarray(catalog.orientation.to(u.rad).value, dtype=float)
    raw = len(hfr)

    columns = [xCoord, yCoord, aAxis, bAxis, theta, hfr, elongation, flux, fluxErr]

    # 8.4: n_pixels covers the lower size bound, only an upper cut remains
    r = np.sqrt(aAxis * aAxis + bAxis * bAxis)
    mask = r < 15
    columns = [c[mask] for c in columns]
    select = len(columns[5])

    # 8.2: S/N from catalog error propagation (kron_flux / kron_flux_err)
    with np.errstate(divide="ignore", invalid="ignore"):
        sn = np.where(columns[8] > 0, columns[7] / columns[8], 0.0)
    mask = sn > snTarget
    columns = [c[mask] for c in columns]
    signalNoise = len(columns[5])

    mask = columns[5] < 10
    columns = [c[mask] for c in columns]
    hfrCount = len(columns[5])

    sources = Sources(
        xCoord=columns[0],
        yCoord=columns[1],
        aAxis=columns[2],
        bAxis=columns[3],
        theta=columns[4],
        hfr=columns[5],
        elongation=columns[6],
    )
    counts = ExtractCounts(raw=raw, select=select, signalNoise=signalNoise, hfr=hfrCount)
    return sources, counts
