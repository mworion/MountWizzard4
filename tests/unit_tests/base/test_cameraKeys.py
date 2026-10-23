# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base import cameraKeys


def keyConstants() -> dict[str, str]:
    return {k: v for k, v in vars(cameraKeys).items() if k.isupper()}


def test_constantsFollowIndiNaming():
    for name, value in keyConstants().items():
        assert name == value.replace(".", "_")


def test_valuesAreUnique():
    values = list(keyConstants().values())
    assert values
    assert len(values) == len(set(values))
