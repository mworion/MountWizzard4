# tests/unit_tests/gui/extWindows/conftest.py
import gc
import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(autouse=True)
def flush_qt_events_on_teardown(qapp):
    yield
    # Flush Qt events WHILE objects are still alive (before GC runs)
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()