from mw4.mountcontrol import timing


def test_constants() -> None:
    assert timing.POLL_FAST_S < timing.POLL_MEDIUM_S < timing.POLL_SLOW_S
    assert timing.BULK_CHUNK_SIZE > 0
    assert timing.COMMAND_DEADLINE_S > 0
