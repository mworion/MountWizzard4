# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.controllers.mount.iersTime import reloadDeltaT
from mw4.mountcontrol.obsSite import ObsSite
from unittest import mock


@pytest.mark.parametrize("success", [True, False])
def test_reloadDeltaT(success: bool) -> None:
    obsSite = mock.create_autospec(ObsSite, instance=True)
    obsSite.reloadDeltaT.return_value = success
    assert reloadDeltaT(obsSite) is success
    obsSite.reloadDeltaT.assert_called_once_with()
