# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.logic.profiles import migration
from mw4.logic.profiles.config import profileVersion
from unittest import mock


def test_migrateConfig_current():
    data = {"version": profileVersion, "a": 1}
    assert migration.migrateConfig(data) is data


def test_migrateConfig_unknownVersion():
    assert migration.migrateConfig({"version": "0.1"}) is None
    assert migration.migrateConfig({}) is None


def test_migrateConfig_chain():
    steps = {
        "0.1": lambda d: {**d, "version": "0.2"},
        "0.2": lambda d: {**d, "version": profileVersion, "migrated": True},
    }
    with mock.patch.object(migration, "migrations", steps):
        result = migration.migrateConfig({"version": "0.1"})
    assert result == {"version": profileVersion, "migrated": True}


def test_migrateConfig_noProgress():
    steps = {"0.1": lambda d: d}
    with mock.patch.object(migration, "migrations", steps):
        assert migration.migrateConfig({"version": "0.1"}) is None
