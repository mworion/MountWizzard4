# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from dataclasses import dataclass, field
from skyfield.timelib import Time


@dataclass
class JdParamsMixin:
    """Mixin providing jdStart and jdEnd properties for dataclass-based parameter classes.

    Subclasses must provide a ``obsSite`` attribute exposing ``obsSite.ts`` (a Skyfield
    ``Timescale``) and ``obsSite.UTC2TT`` (float offset in days).
    """

    _jdStart: Time | None = field(default=None, init=False, repr=False)
    _jdEnd: Time | None = field(default=None, init=False, repr=False)

    @property
    def jdStart(self) -> Time:
        if self._jdStart is None:
            return self.obsSite.ts.now()  # type: ignore[attr-defined]
        return self._jdStart

    @jdStart.setter
    def jdStart(self, value: float) -> None:
        self._jdStart = self.obsSite.ts.tt_jd(  # type: ignore[attr-defined]
            value + self.obsSite.UTC2TT  # type: ignore[attr-defined]
        )

    @property
    def jdEnd(self) -> Time:
        if self._jdEnd is None:
            return self.obsSite.ts.now()  # type: ignore[attr-defined]
        return self._jdEnd

    @jdEnd.setter
    def jdEnd(self, value: float) -> None:
        self._jdEnd = self.obsSite.ts.tt_jd(  # type: ignore[attr-defined]
            value + self.obsSite.UTC2TT  # type: ignore[attr-defined]
        )
