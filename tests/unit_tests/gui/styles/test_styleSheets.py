# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from mw4.gui.styles.styleSheets import BASIC_STYLE, MAC_STYLE, NON_MAC_STYLE


@pytest.fixture(autouse=True, scope="module")
def module(qapp):
    yield


def test_styleSheets_1():
    assert isinstance(MAC_STYLE, str)


def test_styleSheets_2():
    assert isinstance(NON_MAC_STYLE, str)


def test_styleSheets_3():
    assert isinstance(BASIC_STYLE, str)
