# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from mw4.gui.styles.images import images


@pytest.fixture(autouse=True, scope="module")
def module(qapp):
    yield


def test_forms_1():
    assert len(images) == 4
