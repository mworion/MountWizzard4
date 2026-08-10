import sys
import threading
import time
import traceback
from PySide6.QtCore import QObject, QTimer


class EventLoopWatchdog(QObject):
    def __init__(self, threshold_seconds=0.2, check_interval=0.05):
        super().__init__()
        self.threshold = threshold_seconds
        self.check_interval = check_interval
        self.last_heartbeat = time.perf_counter()

        # Capture the Main Thread ID reliably
        self.main_thread_id = threading.main_thread().ident

        # Heartbeat timer running on PySide GUI event loop
        self.timer = QTimer()
        self.timer.setInterval(int(check_interval * 1000))
        self.timer.timeout.connect(self._heartbeat)
        self.timer.start()

        # Background thread that monitors the main thread
        self.monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self.monitor_thread.start()

    def log(self, message: str):
        """Bypass stdout buffering to force terminal print instantly."""
        sys.__stdout__.write(message + "\n")
        sys.__stdout__.flush()

    def _heartbeat(self):
        self.last_heartbeat = time.perf_counter()

    def _monitor(self):
        while True:
            time.sleep(self.check_interval)
            elapsed = time.perf_counter() - self.last_heartbeat

            if elapsed > self.threshold:
                # Sample 1: Take initial frame snapshot
                frames_1 = sys._current_frames()
                main_frame_1 = frames_1.get(self.main_thread_id)
                lasti_1 = getattr(main_frame_1, "f_lasti", None) if main_frame_1 else None

                # Small pause to see if Python bytecode pointer moves
                time.sleep(0.02)

                # Sample 2: Take second frame snapshot
                frames_2 = sys._current_frames()
                main_frame_2 = frames_2.get(self.main_thread_id)
                lasti_2 = getattr(main_frame_2, "f_lasti", None) if main_frame_2 else None

                if main_frame_2:
                    # If instruction pointer (f_lasti) hasn't moved, it's stuck in a C call
                    is_c_call = (lasti_1 is not None) and (lasti_1 == lasti_2)

                    self.log(f"\n==================================================")
                    self.log(f"[WATCHDOG ALERT] Event loop frozen for {elapsed:.3f}s!")

                    if is_c_call:
                        self.log(
                            "==> BLOCK TYPE: Native C/C++ Extension Call (stuck in un-GIL'd/C code)"
                        )
                    else:
                        self.log("==> BLOCK TYPE: Active Python Bytecode Execution (CPU loop)")

                    self.log("--- Stack Trace ---")
                    stack = traceback.extract_stack(main_frame_2)
                    for filename, lineno, name, line in stack:
                        self.log(f'  File "{filename}", line {lineno}, in {name}')
                        if line:
                            self.log(f"    {line}")

                    if stack:
                        caller = stack[-1]
                        label = (
                            "NATIVE C FUNCTION CALLER" if is_c_call else "ACTIVE PYTHON LINE"
                        )
                        self.log(f"\n--> {label}:")
                        self.log(f"    Function : {caller.name}")
                        self.log(f"    File     : {caller.filename}:{caller.lineno}")
                        self.log(f"    Code     : {caller.line}")
                    self.log(f"==================================================\n")

                # Throttle logging so it doesn't flood terminal during a long lockup
                time.sleep(self.threshold * 2)