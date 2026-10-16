# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from dataclasses import dataclass, field
from skyfield.timelib import Time, Timescale
from typing import TYPE_CHECKING, Protocol


class TimeSource(Protocol):
    ts: Timescale
    UTC2TT: float


@dataclass
class JdParamsMixin:
    """Mixin providing jdStart and jdEnd properties for dataclass-based parameter classes.

    Subclasses must provide a ``obsSite`` attribute exposing ``obsSite.ts`` (a Skyfield
    ``Timescale``) and ``obsSite.UTC2TT`` (float offset in days).
    """

    if TYPE_CHECKING:

        @property
        def obsSite(self) -> TimeSource: ...

    _jdStart: Time | None = field(default=None, init=False, repr=False)
    _jdEnd: Time | None = field(default=None, init=False, repr=False)

    @property
    def jdStart(self) -> Time:
        if self._jdStart is None:
            return self.obsSite.ts.now()
        return self._jdStart

    @jdStart.setter
    def jdStart(self, value: float) -> None:
        self._jdStart = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)

    @property
    def jdEnd(self) -> Time:
        if self._jdEnd is None:
            return self.obsSite.ts.now()
        return self._jdEnd

    @jdEnd.setter
    def jdEnd(self, value: float) -> None:
        self._jdEnd = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)
