# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import re
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[2] / "src" / "mw4"
TEST_DIR = Path(__file__).resolve().parent
GENERATED = SRC_DIR / "gui" / "widgets"


def test_everyModuleHasTestFile() -> None:
    missing = []
    for module in SRC_DIR.rglob("*.py"):
        if module.name == "__init__.py" or GENERATED in module.parents:
            continue
        testFile = TEST_DIR / module.relative_to(SRC_DIR).parent / f"test_{module.name}"
        if not testFile.exists():
            missing.append(str(module.relative_to(SRC_DIR)))
    assert not missing, f"modules without test file: {missing}"


def test_noDirectAppImport() -> None:
    allowed = {"baseTestApp.py", "test_makeApp.py", "test_testMapping.py"}
    pattern = re.compile(r"baseTestApp import (?:\w+, )*App\b")
    offenders = [
        str(testFile.relative_to(TEST_DIR))
        for testFile in TEST_DIR.rglob("*.py")
        if testFile.name not in allowed and pattern.search(testFile.read_text())
    ]
    assert not offenders, f"use the makeApp fixture instead of App: {offenders}"
