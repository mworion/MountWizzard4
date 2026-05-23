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
# License APL2.0
#
###########################################################
from typing import Any


class DeviceRegistry:
    """Stores the active driver mapping populated by the settings GUI.

    Keys are device names (e.g. "camera", "dome").
    Values are the same dicts that SettDevice.drivers uses:
        {
            "uiDropDown": <QComboBox>,
            "uiSetup":    <QPushButton | None>,
            "class":      <device-logic instance>,
            "deviceType": <str | None>,
        }

    Only the "class" entry is required by logic-layer consumers;
    the GUI-specific keys ("uiDropDown", "uiSetup") are ignored
    outside the GUI.
    """

    def __init__(self) -> None:
        self._drivers: dict[str, Any] = {}

    def update(self, drivers: dict[str, Any]) -> None:
        """Replace the entire driver mapping.

        Called by SettDevice after building self.drivers so that
        logic-layer code never needs to navigate the widget tree.
        """
        self._drivers = drivers

    def getDrivers(self) -> dict[str, Any]:
        """Return the current active-driver mapping.

        Returns an empty dict before the GUI has populated the
        registry; consumers must guard with
        ``if device not in drivers``.
        """
        return self._drivers
