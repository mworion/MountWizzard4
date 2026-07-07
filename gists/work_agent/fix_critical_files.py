#!/usr/bin/env python3
"""
Carefully migrate pointer.py and tabModel.py with proper fixes
"""

import re
from pathlib import Path


def migrate_file(filepath):
    content = filepath.read_text()

    # Pattern 1: Multi-line self.app.dReg.drivers["device"]["key"] patterns
    content = re.sub(
        r'self\.app\.dReg\.drivers\["([^"]+)"\]\s*\[\s*"class"\s*\]',
        r'self.app.dReg["\1"].instance',
        content,
        flags=re.DOTALL,
    )

    # Pattern 2: Multi-line self.app.dReg.drivers["device"]["stat"] patterns
    content = re.sub(
        r'self\.app\.dReg\.drivers\["([^"]+)"\]\s*\[\s*"stat"\s*\]',
        r'self.app.dReg["\1"].stat',
        content,
        flags=re.DOTALL,
    )

    # Pattern 3: Multi-line self.app.dReg.drivers["device"]["deviceType"] patterns
    content = re.sub(
        r'self\.app\.dReg\.drivers\["([^"]+)"\]\s*\[\s*"deviceType"\s*\]',
        r'self.app.dReg["\1"].deviceType',
        content,
        flags=re.DOTALL,
    )

    filepath.write_text(content)


# Migrate both files
migrate_file(Path("../../src/mw4/gui/extWindows/simulator/pointer.py"))
migrate_file(Path("../../src/mw4/gui/mainWaddon/tabModel.py"))

