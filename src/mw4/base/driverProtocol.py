# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HasSignals(Protocol):
    """A device instance that announces connection state through signals."""

    signals: Any


@runtime_checkable
class HasDriverConfig(Protocol):
    """A framework driver that carries a configuration dataclass."""

    config: Any
