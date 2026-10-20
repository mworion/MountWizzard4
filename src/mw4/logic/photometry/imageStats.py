# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from dataclasses import dataclass

# arcsec per pixel = pixelSize[um] / focalLength[mm] * 206.265
ARCSEC_PER_RAD_FACTOR = 206.265


@dataclass(frozen=True)
class ImageStats:
    resolutionX: float | None
    resolutionY: float | None
    speed: float | None
    dawes: float | None
    rayleigh: float | None
    magLimit: float | None
    fovX: float | None
    fovY: float | None
    fovHint: float
    focusCCD: float | None
    focusRed: float | None
    focusGreen: float | None
    focusBlue: float | None


def calcResolution(
    focalLength: float, pixelSizeX: float, pixelSizeY: float
) -> tuple[float | None, float | None]:
    if not (focalLength and pixelSizeX and pixelSizeY):
        return None, None
    return (
        pixelSizeX / focalLength * ARCSEC_PER_RAD_FACTOR,
        pixelSizeY / focalLength * ARCSEC_PER_RAD_FACTOR,
    )


def calcOpticsLimits(aperture: float) -> tuple[float | None, float | None, float | None]:
    if not aperture:
        return None, None, None
    return 116 / aperture, 138 / aperture, 7.7 + (5 * np.log10(aperture / 10))


def calcFov(
    focalLength: float, pixelSizeX: float, pixelSizeY: float, pixelX: int, pixelY: int
) -> tuple[float | None, float | None, float]:
    if not (focalLength and pixelSizeY and pixelX and pixelY):
        return None, None, 0
    fovX = pixelSizeX / focalLength * ARCSEC_PER_RAD_FACTOR * pixelX / 3600
    fovY = pixelSizeY / focalLength * ARCSEC_PER_RAD_FACTOR * pixelY / 3600
    return fovX, fovY, float(np.sqrt(fovX * fovX + fovY * fovY))


def calcFocus(
    speed: float | None, pixelSizeX: float
) -> tuple[float | None, float | None, float | None, float | None]:
    if not (pixelSizeX and speed):
        return None, None, None, None
    return (
        speed * pixelSizeX,
        4.88 * speed * speed * 0.650,
        4.88 * speed * speed * 0.510,
        4.88 * speed * speed * 0.475,
    )


def calcImageStats(
    focalLength: float,
    aperture: float,
    pixelSizeX: float,
    pixelSizeY: float,
    pixelX: int,
    pixelY: int,
) -> ImageStats:
    resolutionX, resolutionY = calcResolution(focalLength, pixelSizeX, pixelSizeY)
    speed = focalLength / aperture if aperture else None
    dawes, rayleigh, magLimit = calcOpticsLimits(aperture)
    fovX, fovY, fovHint = calcFov(focalLength, pixelSizeX, pixelSizeY, pixelX, pixelY)
    focusCCD, focusRed, focusGreen, focusBlue = calcFocus(speed, pixelSizeX)
    return ImageStats(
        resolutionX=resolutionX,
        resolutionY=resolutionY,
        speed=speed,
        dawes=dawes,
        rayleigh=rayleigh,
        magLimit=magLimit,
        fovX=fovX,
        fovY=fovY,
        fovHint=fovHint,
        focusCCD=focusCCD,
        focusRed=focusRed,
        focusGreen=focusGreen,
        focusBlue=focusBlue,
    )
