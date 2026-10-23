# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import mw4.logic.controllers.model.buildpointsSupport as support
from mw4.logic.controllers.model.buildpointsSupport import generateUntilTarget, querySimbad
from unittest import mock


def test_generateUntilTarget_reachesTarget() -> None:
    points: list[int] = []
    requested: list[int] = []

    def generate(number: int) -> None:
        requested.append(number)
        points[:] = [1] * (number // 2)

    generateUntilTarget(generate, lambda: None, lambda: len(points), 10)
    assert len(points) >= 10
    assert requested[0] == 10


def test_generateUntilTarget_limitedIterations() -> None:
    generate = mock.Mock()
    generateUntilTarget(generate, lambda: None, lambda: 1, 10)
    assert generate.call_count == support.MAX_ITERATIONS - 1


def test_generateUntilTarget_stopWhenEmpty() -> None:
    generate = mock.Mock()
    generateUntilTarget(generate, lambda: None, lambda: 0, 10, stopWhenEmpty=True)
    generate.assert_called_once_with(10)


def test_generateUntilTarget_continueWhenEmpty() -> None:
    generate = mock.Mock()
    generateUntilTarget(generate, lambda: None, lambda: 0, 10)
    assert generate.call_count == support.MAX_ITERATIONS - 1


def test_querySimbad_unknown() -> None:
    with mock.patch.object(support.Simbad, "query_object", return_value=None):
        assert querySimbad("xyz") is None


def test_querySimbad() -> None:
    with mock.patch.object(support.Simbad, "query_object", return_value={"ra": 10.0, "dec": -5.0}):
        ra, dec = querySimbad("m31")
    assert ra.degrees == 10.0
    assert dec.degrees == -5.0
