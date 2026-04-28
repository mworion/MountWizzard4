############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
############################################################
"""
Cyclic startup stress test for MountWizzard4.

Strategy
--------
MountWizzard4.__init__ wires   ``update10s → quit()``  when *test=1* is passed.
``update10s`` fires for the first time at timerCounter == 80, i.e. ≈ 8 seconds
after the 100-ms timer starts (formula: (timerCounter + 20) % 100 == 0).
This gives a clean, reproducible start/stop cycle that exercises:

  * full application boot (all logic objects, main window, timers)
  * the Qt event loop running normally for ~8 seconds, including at least
    3–4 mount-up checks (CYCLE_MOUNT_UP = 2 000 ms) so the mount can connect
  * clean shutdown (threadPool drain, timer stop, signal disconnect)

Mount connectivity
------------------
Set ``MOUNT_HOST`` below to the actual mount IP (e.g. "192.168.2.15").
When non-empty it is written into the test profile before each cycle so that
``SettMount.initConfig()`` picks it up and ``mount.host`` is set, enabling the
``cycleCheckMountIsUp`` worker threads.  Leave it empty ("") to run without
a real mount (host=None path, no TCP workers).

Each cycle is validated individually and a summary table is printed at the end.
``faulthandler`` is enabled so any SIGSEGV produces a Python traceback in the
terminal instead of a silent crash.

Usage
-----
    pytest tests/stress_tests/test_loader_cycle.py -v -s

    # run more cycles:
    N_CYCLES=20 pytest tests/stress_tests/test_loader_cycle.py -v -s
"""

import faulthandler
import gc
import glob
import json
import os
import pytest
import time
from mw4.base.bootstrap import extractDataFiles
from mw4.mainApp import MountWizzard4
from pathlib import Path

# ── enable low-level crash handler ────────────────────────────────────────────
faulthandler.enable()

# ── test parameters ────────────────────────────────────────────────────────────
N_CYCLES = 100  # number of start/stop cycles to run
BOOT_TIMEOUT_MS = 15_000  # max ms to wait for the main window to appear
QUIT_TIMEOUT_MS = 30_000  # max ms to wait for update10s → quit()  (fires at ≈8 s)
MAX_BOOT_S = 10.0  # per-cycle assertion: boot faster than this
MAX_CYCLE_S = 25.0  # per-cycle assertion: full cycle faster than this
#   (boot ≈ 5–8 s  +  update10s at 8 s  +  margin)

# ── optional mount host (set to "" to skip real TCP mount checks) ─────────────
MOUNT_HOST = "mount.uranus"  # e.g. "192.168.2.15"  – injected into profile config
MOUNT_PORT_3492 = True  # True → port 3492, False → port 3490

# ── work directory layout (mirrors bootstrap.setupWorkDirs) ──────────────────
WORK_DIR = Path("tests/work")

mwglob = {
    "workDir": WORK_DIR,
    "configDir": WORK_DIR / "config",
    "dataDir": WORK_DIR / "assets",
    "imageDir": WORK_DIR / "image",
    "tempDir": WORK_DIR / "temp",
    "modelDir": WORK_DIR / "model",
    "measureDir": WORK_DIR / "measure",
    "logDir": WORK_DIR / "log",
}

# Keys whose content should NOT be wiped between tests
_SKIP_CLEAN = {"workDir", "configDir", "logDir", "imageDir", "dataDir"}


# ── fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module", autouse=True)
def setup_work_dirs():
    """Create directories and extract ephemeris / time assets once per module."""
    for path in mwglob.values():
        path.mkdir(parents=True, exist_ok=True)
    extractDataFiles(mwGlob=mwglob)
    yield


@pytest.fixture(autouse=True)
def clean_work_dirs():
    """
    Before each test: re-extract assets files so every cycle starts clean.
    When MOUNT_HOST is set, write it into the config so that
    SettMount.initConfig() picks it up and mount.host is set for the TCP
    connectivity check (cycleCheckMountIsUp).
    After each test: remove generated files (images, models, temp, …).
    """
    _wipe()
    extractDataFiles(mwGlob=mwglob)
    if MOUNT_HOST:
        _inject_mount_host()
    yield
    _wipe()


def _inject_mount_host():
    """Write a minimal profile JSON so the mount host is configured at boot."""
    config_dir = mwglob["configDir"]
    # discover the active profile name (written by loader) or default to "config"
    profile_file = config_dir / "profiles.json"
    profile_name = "config"
    if profile_file.exists():
        try:
            profiles = json.loads(profile_file.read_text())
            profile_name = profiles.get("profileName", "config")
        except Exception:
            pass

    cfg_path = config_dir / f"{profile_name}.cfg"
    cfg = {}
    if cfg_path.exists():
        try:
            cfg = json.loads(cfg_path.read_text())
        except Exception:
            pass

    port = 3492 if MOUNT_PORT_3492 else 3490
    cfg.setdefault("mainW", {})
    cfg["mainW"]["mountHost"] = MOUNT_HOST
    cfg["mainW"]["port3492"] = MOUNT_PORT_3492
    cfg_path.write_text(json.dumps(cfg, indent=2))


def _wipe():
    for key, path in mwglob.items():
        if key in _SKIP_CLEAN:
            continue
        for f in glob.glob(str(path / "*")):
            if "empty" in f:
                continue
            try:
                os.remove(f)
            except OSError:
                pass


# ── helpers ────────────────────────────────────────────────────────────────────

_COL = 65


def _banner():
    mount_info = f"mount={MOUNT_HOST}" if MOUNT_HOST else "no mount"
    print(
        f"\n{'─' * _COL}\n"
        f"  MountWizzard4  cyclic startup stress test\n"
        f"  Cycles : {N_CYCLES}   |   mode: test=1  (update10s → quit, ≈8 s)\n"
        f"  Limits : boot < {MAX_BOOT_S}s   cycle < {MAX_CYCLE_S}s   {mount_info}\n"
        f"{'─' * _COL}"
    )


def _row(cycle, t_boot, t_total, pool_active, status):
    mark = "✓" if status == "ok" else "✗"
    print(
        f"  [{mark}] #{cycle:02d}  "
        f"boot={t_boot:5.2f}s  "
        f"total={t_total:5.2f}s  "
        f"pool={pool_active:2d}  "
        f"{status}"
    )


def _summary(results):
    passed = sum(1 for r in results if r["status"] == "ok")
    print(f"\n{'─' * _COL}")
    print(f"  {passed}/{len(results)} cycles passed")
    if results:
        boots = [r["t_boot"] for r in results]
        totals = [r["t_total"] for r in results]
        print(
            f"  boot  : min={min(boots):.2f}s "
            f"max={max(boots):.2f}s "
            f"avg={sum(boots) / len(boots):.2f}s"
        )
        print(
            f"  cycle : min={min(totals):.2f}s "
            f"max={max(totals):.2f}s "
            f"avg={sum(totals) / len(totals):.2f}s"
        )
    print(f"{'─' * _COL}\n")


# ── test ───────────────────────────────────────────────────────────────────────


def test_loader_startup_cycles(qtbot, qapp):
    """
    Boot MountWizzard4 in test-mode and let it self-quit N times.

    Lifecycle per cycle
    -------------------
    1. ``MountWizzard4(mwGlob, qapp, test=1)``
       Connects  update10s → quit()  before returning.

    2. ``qtbot.waitExposed(app.mainW)``
       Confirms the main window is visible on screen.

    3. ``qtbot.waitSignal(app.update10s)``
       Processes Qt events until update10s fires (≈ 8 s, timerCounter == 80).
       Because quit() is connected *before* the waitSignal slot,
       quit() → qapp.quit() runs first, exiting the local QEventLoop;
       pytest-qt still marks the signal as received.
       During these 8 s the mount-up timer (CYCLE_MOUNT_UP = 2 000 ms) fires
       3–4 times, so a real mount (MOUNT_HOST != "") can fully connect.

    4. ``app.threadPool.waitForDone(10_000)``
       Ensures no worker threads outlive the app object.
       10 s gives in-flight socket workers (SOCKET_TIMEOUT = 2 s) enough
       headroom to complete cleanly.

    5. ``del app; gc.collect()``
       Releases all Python references so Shiboken / Qt can clean up
       the C++ side.  Any use-after-free will surface here on
       Apple Silicon (PAC) or with AddressSanitizer.
    """
    _banner()
    results = []

    for cycle in range(1, N_CYCLES + 1):
        t0 = time.monotonic()
        status = "ok"

        # ── boot ─────────────────────────────────────────
        app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)

        try:
            qtbot.waitExposed(app.mainW, timeout=BOOT_TIMEOUT_MS)
        except Exception as exc:
            status = f"boot-timeout ({exc.__class__.__name__})"

        t_boot = time.monotonic() - t0

        # ── run until auto-quit ───────────────────────────
        if status == "ok":
            try:
                with qtbot.waitSignal(app.update10s, timeout=QUIT_TIMEOUT_MS, raising=True):
                    pass  # event loop runs here; update10s fires → quit()
            except Exception as exc:
                status = f"quit-timeout ({exc.__class__.__name__})"

        t_total = time.monotonic() - t0
        pool_active = app.threadPool.activeThreadCount()

        # ── drain thread pool ─────────────────────────────
        if not app.threadPool.waitForDone(10_000):
            if status == "ok":
                status = "pool-drain-timeout"

        pool_after = app.threadPool.activeThreadCount()

        # ── record ───────────────────────────────────────
        results.append(
            {
                "cycle": cycle,
                "t_boot": t_boot,
                "t_total": t_total,
                "pool_active": pool_active,
                "pool_after": pool_after,
                "status": status,
            }
        )
        _row(cycle, t_boot, t_total, pool_active, status)

        # ── cleanup ───────────────────────────────────────
        del app
        gc.collect()
        qapp.processEvents()  # drain any remaining queued events

    _summary(results)

    # ── assertions ────────────────────────────────────────
    failed = [r for r in results if r["status"] != "ok"]
    assert not failed, f"{len(failed)}/{N_CYCLES} cycle(s) failed:\n" + "\n".join(
        f"  cycle {r['cycle']:02d}: {r['status']}" for r in failed
    )

    for r in results:
        assert r["t_boot"] < MAX_BOOT_S, (
            f"Cycle {r['cycle']:02d}: boot {r['t_boot']:.2f}s exceeds limit {MAX_BOOT_S}s"
        )
        assert r["t_total"] < MAX_CYCLE_S, (
            f"Cycle {r['cycle']:02d}: total {r['t_total']:.2f}s exceeds limit {MAX_CYCLE_S}s"
        )
        assert r["pool_after"] == 0, (
            f"Cycle {r['cycle']:02d}: "
            f"{r['pool_after']} worker thread(s) still active after drain"
        )
