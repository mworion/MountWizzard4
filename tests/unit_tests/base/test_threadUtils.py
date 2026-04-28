import time

from PySide6.QtCore import QCoreApplication


def ensure_qt_app() -> None:
    """Ensure a Qt application instance exists for QEventLoop/QTimer calls.

    Creating a QCoreApplication is cheap and safe for unit tests; some CI
    environments may already have an application instance from other
    test fixtures.
    """
    if QCoreApplication.instance() is None:
        QCoreApplication([])


def test_mainThreadSleep_sleeps_at_least_specified_time():
    from mw4.base.threadUtils import mainThreadSleep

    ensure_qt_app()
    ms = 200
    t0 = time.monotonic()
    mainThreadSleep(ms)
    delta = time.monotonic() - t0

    # Allow a small scheduling tolerance (20 ms)
    assert delta >= (ms / 1000.0) - 0.02


def test_mainThreadSleep_zero_returns_quickly():
    from mw4.base.threadUtils import mainThreadSleep

    ensure_qt_app()
    t0 = time.monotonic()
    mainThreadSleep(0)
    delta = time.monotonic() - t0

    # Should return almost immediately (within 50 ms)
    assert delta < 0.05
