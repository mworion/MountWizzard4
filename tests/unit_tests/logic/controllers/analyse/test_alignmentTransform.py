# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
import pytest
from dataclasses import replace
from mw4.logic.controllers.analyse.analyseModel import (
    alignmentUnitVector,
    applyAlignmentTransform,
    applyOrthogonalityRotation,
    reframeEquatorialAlignment,
    validateAlignmentRotation,
    wrapAlignmentAngle,
)
from mw4.logic.controllers.analyse.analyseTypes import AlignmentState, AlignmentTransform
from unittest import mock


@pytest.fixture(scope="module")
def alignmentState() -> AlignmentState:
    return AlignmentState(
        pointingRotation=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        declinationOffset=0.1,
        orthogonalityAngle=0.2,
        reverseOrthogonality=False,
    )


@pytest.mark.parametrize("lower", [-np.pi, -np.pi / 2])
def test_wrapEndpoints(lower: float) -> None:
    upper = lower + 2 * np.pi
    assert wrapAlignmentAngle(lower, lower) == lower
    assert wrapAlignmentAngle(upper, lower) == upper
    assert wrapAlignmentAngle(upper + 0.25, lower) == pytest.approx(lower + 0.25)
    assert wrapAlignmentAngle(lower - 0.25, lower) == pytest.approx(upper - 0.25)


@pytest.mark.parametrize("angle,lower", [(np.nan, 0), (0, np.inf)])
def test_invalidWrap(angle: float, lower: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        wrapAlignmentAngle(angle, lower)


def test_unitVector() -> None:
    np.testing.assert_allclose(alignmentUnitVector(np.pi / 2, 0), [0, 1, 0], atol=1e-15)
    np.testing.assert_allclose(alignmentUnitVector(0, np.pi / 6), [np.sqrt(3) / 2, 0, 0.5])


@pytest.mark.parametrize("d,c", [(np.nan, 0), (0, np.inf), (0, 2)])
def test_invalidSphericalAngles(d: float, c: float) -> None:
    with pytest.raises(ValueError, match="latitude"):
        alignmentUnitVector(d, c)


def test_rotationValidation(alignmentState: AlignmentState) -> None:
    np.testing.assert_array_equal(
        validateAlignmentRotation(alignmentState.pointingRotation), np.eye(3)
    )


@pytest.mark.parametrize(
    "matrix",
    [
        ((1, 0), (0, 1)),
        ((np.nan, 0, 0), (0, 1, 0), (0, 0, 1)),
        ((-1, 0, 0), (0, 1, 0), (0, 0, 1)),
        ((2, 0, 0), (0, 1, 0), (0, 0, 1)),
    ],
)
def test_invalidRotation(matrix: tuple) -> None:
    with pytest.raises(ValueError, match="matrix"):
        validateAlignmentRotation(matrix)


@pytest.mark.parametrize("phi", [-0.3, 0, 0.3])
def test_orthogonalityEquator(phi: float) -> None:
    result = applyOrthogonalityRotation(np.array([1.0, 0, 0]), phi)
    assert result.d == pytest.approx(-phi)
    assert result.c == 0
    assert result.status == "applied"
    assert result.diagnostic is None


@pytest.mark.parametrize("sign", [-1, 1])
def test_orthogonalityInteriorAndBoundary(sign: int) -> None:
    interior = applyOrthogonalityRotation(np.array([np.sqrt(3) / 2, 0, sign * 0.5]), np.pi / 6)
    assert interior.c == pytest.approx(sign * np.arcsin(1 / np.sqrt(3)))
    assert interior.d == pytest.approx(-np.arctan(np.sqrt(0.5)))
    boundary = applyOrthogonalityRotation(np.array([0, 0, sign]), 0)
    assert boundary.c == sign * np.pi / 2
    assert boundary.d == 0
    assert boundary.status == "applied"
    nonzeroBoundary = applyOrthogonalityRotation(
        np.array([np.sin(0.5), 0, sign * np.cos(0.5)]), 0.5
    )
    assert nonzeroBoundary.c == sign * np.pi / 2
    assert nonzeroBoundary.d == pytest.approx(-np.pi / 2)


@pytest.mark.parametrize("sign", [-1, 1])
def test_orthogonalityFallback(sign: int) -> None:
    result = applyOrthogonalityRotation(np.array([0, 0, sign]), 0.2)
    assert result.status == "fallback"
    assert result.d == 0
    assert result.c == sign * np.pi / 2
    assert "domain exceeded" in result.diagnostic


@pytest.mark.parametrize(
    "vector,phi,message",
    [
        ([1, 0], 0, "three-vector"),
        ([np.nan, 0, 0], 0, "finite"),
        ([1, 0, 0], np.nan, "finite"),
        ([0, 0, 0], 0, "unit vector"),
        ([2, 0, 0], 0, "unit vector"),
        ([1, 0, 0], np.pi / 2, "singular"),
    ],
)
def test_invalidOrthogonality(vector: list[float], phi: float, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        applyOrthogonalityRotation(np.array(vector), phi)


def test_nearSingularButDefinedOrthogonality() -> None:
    result = applyOrthogonalityRotation(np.array([0, 0, 1]), np.pi / 2 - 1e-12)
    assert result.status == "fallback"


def test_gmReframe() -> None:
    assert reframeEquatorialAlignment(0, 0.3, 0.1) == pytest.approx((np.pi, np.pi / 2 - 0.2))
    assert reframeEquatorialAlignment(np.pi, 0, 0) == pytest.approx((0, np.pi / 2))
    with pytest.raises(ValueError, match="finite"):
        reframeEquatorialAlignment(0, 0, np.nan)


def test_explicitStateTransform(alignmentState: AlignmentState) -> None:
    result = applyAlignmentTransform(0, 0, alignmentState)
    assert result.status == "applied"
    assert (result.d, result.c) == pytest.approx((np.pi - 0.2, np.pi / 2 + 0.1))
    flipped = applyAlignmentTransform(0, 0, replace(alignmentState, reverseOrthogonality=True))
    assert flipped.d == pytest.approx(np.pi + 0.2)
    assert flipped.c == result.c
    assert alignmentState.geometry == "GM equatorial"
    assert alignmentState.unit == result.unit == "radians"
    assert "GM-only" in alignmentState.provenance
    assert alignmentState.polarAxisRotation is None


def test_rotationThenOrthogonalityThenReframe(alignmentState: AlignmentState) -> None:
    rotation = ((0, -1, 0), (1, 0, 0), (0, 0, 1))
    result = applyAlignmentTransform(
        2 * np.pi, 0, replace(alignmentState, pointingRotation=rotation)
    )
    assert result.d == pytest.approx(3 * np.pi / 2 - 0.2)
    assert result.c == pytest.approx(np.pi / 2 + 0.1)
    fallback = applyAlignmentTransform(0, np.pi / 2, alignmentState)
    assert fallback.status == "fallback"
    assert fallback.c == pytest.approx(0.1)


@pytest.mark.parametrize(
    "field", ["pointingRotation", "declinationOffset", "orthogonalityAngle", "reverseOrthogonality"]
)
def test_missingState(alignmentState: AlignmentState, field: str) -> None:
    result = applyAlignmentTransform(0, 0, replace(alignmentState, **{field: None}))
    assert result.status == "unavailable"
    assert result.d is None and result.c is None
    assert "missing" in result.diagnostic


@pytest.mark.parametrize("geometry", ["altaz", "unknown"])
def test_unsupportedGeometry(alignmentState: AlignmentState, geometry: str) -> None:
    result = applyAlignmentTransform(0, 0, replace(alignmentState, geometry=geometry))
    assert result.status == "unavailable"
    assert result.d is None and result.c is None
    assert "GM equatorial" in result.diagnostic


@pytest.mark.parametrize("field", ["declinationOffset", "orthogonalityAngle"])
def test_nonfiniteState(alignmentState: AlignmentState, field: str) -> None:
    with pytest.raises(ValueError, match="finite"):
        applyAlignmentTransform(0, 0, replace(alignmentState, **{field: np.nan}))


def test_invalidHelperResult(alignmentState: AlignmentState) -> None:
    with (
        mock.patch(
            "mw4.logic.controllers.analyse.analyseModel.applyOrthogonalityRotation",
            return_value=AlignmentTransform(None, None, "unavailable"),
        ),
        pytest.raises(ValueError, match="did not return"),
    ):
        applyAlignmentTransform(0, 0, alignmentState)
