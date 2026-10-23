# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import ipaddress
import logging
import re
import socket
import wakeonlan

log = logging.getLogger("MW4")


def checkFormatMAC(value: str) -> str:
    if not value or not isinstance(value, str):
        return ""

    value = value.upper()
    value = value.replace(".", ":")
    value = value.split(":")
    if len(value) != 6:
        return ""

    for chunk in value:
        if not re.fullmatch(r"[0-9A-F]{2}", chunk):
            return ""

    return "{:2s}:{:2s}:{:2s}:{:2s}:{:2s}:{:2s}".format(*value)


def getLocalAddress(refAddress: str) -> str | None:
    """Return the local IPv4 address used to reach refAddress (no traffic)."""
    try:
        target = socket.gethostbyname(refAddress)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect((target, 9))
            return str(sock.getsockname()[0])
    except (OSError, UnicodeError):
        return None


def getSubnetBroadcast(localAddress: str) -> str:
    net = ipaddress.ip_network(f"{localAddress}/24", strict=False)
    return str(net.broadcast_address)


def sendWakeOnLan(mac: str, host: str, port: int, refAddress: str) -> None:
    """Send a magic packet; on OSError retry via the local subnet broadcast.

    Limited broadcast fails on some systems (e.g. macOS with several default
    routes). The retry binds to the local interface used to reach refAddress
    and sends to the /24 broadcast address of that interface.
    """
    try:
        wakeonlan.wake(mac, host=host, port=port)
    except OSError:
        localAddress = getLocalAddress(refAddress)
        if localAddress is None:
            raise
        subnetBroadcast = getSubnetBroadcast(localAddress)
        if subnetBroadcast == host:
            raise
        log.debug("Retry wake on lan via [%s] on [%s]", subnetBroadcast, localAddress)
        wakeonlan.wake(mac, host=subnetBroadcast, port=port, interface=localAddress)
