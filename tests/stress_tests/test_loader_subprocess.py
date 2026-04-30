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
Cyclic startup stress test – subprocess edition.

Each cycle spawns  ``python -m mw4.cli -t 1``  as a fresh OS process
with ``cwd=WORK_DIR``.  ``bootstrap.setupWorkDirs(Path.cwd())`` therefore
resolves to the test work-tree, so every cycle is completely isolated
from the test runner process.

The subprocess runs the full application boot path:

  * splash screen
  * all logic objects (mount, camera, dome, …)
  * 100-ms cyclic timer with mount-up connectivity checks
  * ``update10s → quit()`` auto-quit at ≈ 8 s (timerCounter == 80)
  * clean shutdown in ``aboutToQuit`` / ``quit()``
  * ``sys.exit(app.exec())`` → returncode 0

Because every cycle is a *separate* OS process there is zero shared
Qt / Shiboken / C++ state between cycles.  Any use-after-free, leaked
``QObject`` or dangling C++ pointer that survived the previous cycle
cannot bleed into the next one – the fresh process either boots cleanly
or crashes independently, making the test much more sensitive to
memory-safety problems than the in-process variant.

Diagnostics
-----------
``PYTHONFAULTHANDLER=1`` is set in the subprocess environment so that
any ``SIGSEGV`` / ``SIGBUS`` produces a Python traceback on *stderr*
before the OS crash report.  When a cycle fails the test prints:

  * the tail of the ``mw4-DATE.log`` written by the subprocess to
    ``WORK_DIR/log/`` – this gives the last few hundred lines of debug
    output for post-mortem analysis.
  * captured *stderr* (includes faulthandler traceback on crash).
  * captured *stdout* (usually empty but may contain Qt warnings).

Mount connectivity
------------------
Set ``MW4_TEST_MOUNT`` (or edit ``MOUNT_HOST`` below) to a real IP so
that the ``cycleCheckMountIsUp`` workers attempt a TCP connection.
Leave blank to run without a real mount.

Configuration via environment variables
----------------------------------------
  N_CYCLES          Number of start/stop cycles      (default: 5)
  CYCLE_TIMEOUT     Seconds before a hung cycle is   (default: 60)
                    killed and marked as failed
  MAX_CYCLE_S       Assertion: cycle must finish      (default: 30)
                    within this many seconds
  MIN_CYCLE_S       Assertion: cycle must not exit    (default: 6)
                    too quickly (premature quit guard)
  MW4_TEST_MOUNT    Mount hostname / IP               (default: "")
  MW4_TEST_HEADLESS Set to "1" to add QT_QPA_PLATFORM=offscreen

Usage
-----
    # from the project root:
    pytest tests/stress_tests/test_loader_subprocess.py -v -s \\
        --override-ini="addopts="

    # more cycles + real mount:
    N_CYCLES=20 MW4_TEST_MOUNT=192.168.2.15 \\
        pytest tests/stress_tests/test_loader_subprocess.py -v -s \\
        --override-ini="addopts="
"""

import contextlib
import datetime
import faulthandler
import glob
import json
import os
import pytest
import subprocess
import sys
import time
from pathlib import Path

# ── crash handler in the TEST process ─────────────────────────────────────────
faulthandler.enable()

# ── absolute paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # …/MountWizzard4
WORK_DIR = PROJECT_ROOT / "tests" / "work"  # separate from in-process test

# ── parameters (overridable via environment variables) ─────────────────────────
N_CYCLES = int(os.environ.get("N_CYCLES", "100"))
CYCLE_TIMEOUT = float(os.environ.get("CYCLE_TIMEOUT", "60"))  # s – hard kill limit
MAX_CYCLE_S = float(os.environ.get("MAX_CYCLE_S", "30.0"))  # s – upper assertion
MIN_CYCLE_S = float(os.environ.get("MIN_CYCLE_S", "6.0"))  # s – premature-exit guard

# ── optional real-mount host ────────────────────────────────────────────────────
MOUNT_HOST = os.environ.get("MW4_TEST_MOUNT", "mount.uranus")
MOUNT_PORT_3492 = True  # True → port 3492, False → port 3490

# ── headless Qt (set MW4_TEST_HEADLESS=1 for CI / no-display environments) ─────
HEADLESS = os.environ.get("MW4_TEST_HEADLESS", "0") == "1"

# ── sub-directories that survive between cycles ─────────────────────────────────
_KEEP_SUBDIRS = {"config", "log", "assets", "image"}

# ── how many bytes to tail from the mw4 log on failure ─────────────────────────
LOG_TAIL_BYTES = 8_000


# ──────────────────────────────────────────────────────────────────────────────
# Directory helpers
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_dirs() -> None:
    """Create the WORK_DIR sub-tree (mirrors ``bootstrap.setupWorkDirs``)."""
    for sub in ("config", "assets", "image", "temp", "model", "measure", "log"):
        (WORK_DIR / sub).mkdir(parents=True, exist_ok=True)


def _wipe_transient() -> None:
    """Remove generated files from *temp / model / measure* between cycles."""
    for sub in WORK_DIR.iterdir():
        if not sub.is_dir() or sub.name in _KEEP_SUBDIRS:
            continue
        for f in glob.glob(str(sub / "*")):
            if "empty" in f:
                continue
            with contextlib.suppress(OSError):
                os.remove(f)


def _inject_mount_host() -> None:
    """Write ``MOUNT_HOST`` into the active profile config before each cycle."""
    config_dir = WORK_DIR / "config"
    profile_file = config_dir / "profiles.json"
    profile_name = "config"
    if profile_file.exists():
        try:
            profiles = json.loads(profile_file.read_text())
            profile_name = profiles.get("profileName", "config")
        except Exception:
            pass

    cfg_path = config_dir / f"{profile_name}.cfg"
    cfg: dict = {}
    if cfg_path.exists():
        with contextlib.suppress(Exception):
            cfg = json.loads(cfg_path.read_text())

    cfg.setdefault("mainW", {})
    cfg["mainW"]["mountHost"] = MOUNT_HOST
    cfg["mainW"]["port3492"] = MOUNT_PORT_3492
    cfg_path.write_text(json.dumps(cfg, indent=2))


# ──────────────────────────────────────────────────────────────────────────────
# Subprocess helpers
# ──────────────────────────────────────────────────────────────────────────────


def _build_env() -> dict:
    """
    Return an environment dict for the child process.

    * ``PYTHONFAULTHANDLER=1``  → Python emits a traceback on SIGSEGV
    * ``PYTHONPATH``           → ensures ``mw4`` is importable from ``src/``
    * ``QT_QPA_PLATFORM``      → set to ``offscreen`` when ``HEADLESS=True``
    """
    env = os.environ.copy()
    env["PYTHONFAULTHANDLER"] = "1"

    src_path = str(PROJECT_ROOT / "src")
    pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{src_path}:{pythonpath}" if pythonpath else src_path

    if HEADLESS:
        env["QT_QPA_PLATFORM"] = "offscreen"

    return env


def _tail_mw4_log(n_bytes: int = LOG_TAIL_BYTES) -> str:
    """Return the last *n_bytes* of today's mw4 log (empty string if absent)."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    log_dir = WORK_DIR / "log"
    matches = glob.glob(str(log_dir / f"mw4-{today}.log"))
    if not matches:
        matches = glob.glob(str(log_dir / "mw4-*.log"))  # fallback: any date
    if not matches:
        return ""
    log_path = sorted(matches)[-1]
    try:
        size = os.path.getsize(log_path)
        with open(log_path, "rb") as fh:
            fh.seek(max(0, size - n_bytes))
            return fh.read().decode(errors="replace")
    except OSError:
        return ""


# ──────────────────────────────────────────────────────────────────────────────
# Console helpers
# ──────────────────────────────────────────────────────────────────────────────

_COL = 65


def _banner() -> None:
    pass


def _row(cycle: int, t_total: float, returncode, status: str) -> None:
    pass


def _summary(results: list) -> None:
    sum(1 for r in results if r["status"] == "ok")
    if results:
        [r["t_total"] for r in results]


def _print_diagnostics(cycle: int, stderr_b: bytes, stdout_b: bytes) -> None:
    """Print log tail + captured I/O to help diagnose a failed cycle."""
    tail = _tail_mw4_log()
    if tail:
        pass
    if stderr_b:
        pass
    if stdout_b:
        pass


# ──────────────────────────────────────────────────────────────────────────────
# Pytest fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module", autouse=True)
def setup_work_dirs():
    """Create ``WORK_DIR`` layout once for the whole module."""
    _ensure_dirs()
    yield


# ──────────────────────────────────────────────────────────────────────────────
# Test
# ──────────────────────────────────────────────────────────────────────────────


def test_loader_subprocess_cycles():
    """
    Spawn MountWizzard4 as an OS subprocess *N* times and verify clean exit.

    Lifecycle per cycle
    -------------------
    1. Wipe transient directories (``temp``, ``model``, ``measure``).
    2. Inject ``MOUNT_HOST`` into the profile config (when configured).
    3. Spawn:  ``python -m mw4.cli -t 1``  with ``cwd=WORK_DIR``.

       Inside the subprocess:
         * ``bootstrap.setupWorkDirs(Path.cwd())`` → WORK_DIR work-tree
         * ``bootstrap.extractDataFiles()`` extracts ephemeris / IERS assets
         * ``MountWizzard4(..., test=1)`` wires ``update10s → quit()``
         * 100-ms cyclic timer runs for ≈ 8 s until ``update10s`` fires
         * ``quit()`` → ``application.quit()`` → ``app.exec()`` returns 0
         * ``sys.exit(0)`` → subprocess exits with returncode 0

    4. Wait up to ``CYCLE_TIMEOUT`` seconds for the process to exit.
    5. On timeout: kill the subprocess, record *"timeout"* status.
    6. Validate:
         * ``returncode == 0``  (non-zero → Python exception or OS crash)
         * ``t_total >=  MIN_CYCLE_S``  (premature-exit guard)
         * ``t_total <=  MAX_CYCLE_S``  (upper bound; asserted after summary)
    7. On failure: print mw4 log tail + captured stderr / stdout so that
       ``faulthandler`` tracebacks and Python errors are visible in the
       test report.
    """
    _ensure_dirs()
    _banner()

    env = _build_env()
    cmd = [sys.executable, "-m", "mw4.cli", "-t", "1"]
    results = []

    for cycle in range(1, N_CYCLES + 1):
        _wipe_transient()
        if MOUNT_HOST:
            _inject_mount_host()

        t0 = time.monotonic()
        status = "ok"
        returncode = None
        stdout_b = b""
        stderr_b = b""

        # ── spawn ───────────────────────────────────────────────────────────
        proc = subprocess.Popen(
            cmd,
            cwd=str(WORK_DIR),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # ── wait ────────────────────────────────────────────────────────────
        try:
            stdout_b, stderr_b = proc.communicate(timeout=CYCLE_TIMEOUT)
            returncode = proc.returncode
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout_b, stderr_b = proc.communicate()
            returncode = proc.returncode
            status = f"timeout (>{CYCLE_TIMEOUT:.0f}s)"

        t_total = time.monotonic() - t0

        # ── classify ────────────────────────────────────────────────────────
        if status == "ok":
            if returncode != 0:
                status = f"bad-exit (rc={returncode})"
            elif t_total < MIN_CYCLE_S:
                status = f"too-fast ({t_total:.2f}s < {MIN_CYCLE_S:.1f}s)"

        results.append(
            {
                "cycle": cycle,
                "t_total": t_total,
                "returncode": returncode,
                "status": status,
                "stderr": stderr_b,
                "stdout": stdout_b,
            }
        )

        _row(cycle, t_total, returncode, status)

        if status != "ok":
            _print_diagnostics(cycle, stderr_b, stdout_b)

    _summary(results)

    # ── assertions ──────────────────────────────────────────────────────────
    failed = [r for r in results if r["status"] != "ok"]
    assert not failed, f"{len(failed)}/{N_CYCLES} cycle(s) failed:\n" + "\n".join(
        f"  cycle {r['cycle']:02d}: {r['status']}" for r in failed
    )

    for r in results:
        assert r["t_total"] <= MAX_CYCLE_S, (
            f"Cycle {r['cycle']:02d}: total {r['t_total']:.2f}s "
            f"exceeds limit {MAX_CYCLE_S:.1f}s"
        )
