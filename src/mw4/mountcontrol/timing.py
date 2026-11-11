# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
"""Central timing constants for the communication with the mount."""

POLL_FAST_S: float = 0.5
POLL_MEDIUM_S: float = 3.0
POLL_SLOW_S: float = 30.0
BATCH_DEADLINE_S: float = 2.0
CONNECT_TIMEOUT_S: float = 2.0
RECONNECT_BACKOFF_S: float = 1.0
BULK_CHUNK_SIZE: int = 10
BULK_DEADLINE_PER_COMMAND_S: float = 0.05
COMMAND_DEADLINE_S: float = 10.0
BULK_INTERLEAVE_FAST: bool = True
FAST_POLL_COMMANDS: tuple[str, ...] = (":Ginfo#:GaE#",)
