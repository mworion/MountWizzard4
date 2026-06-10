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
class TabAddon:
    """Base class for all main-window tab addons.

    Declares the four lifecycle hooks dispatched by
    :class:`MainWindowAddons` and provides no-op default implementations
    so concrete addons only override what they need. This replaces the
    repetitive ``hasattr`` guards previously used by the dispatcher and
    makes the contract explicit.
    """

    def initConfig(self) -> None:
        """Load addon-specific state from ``self.app.config``."""

    def storeConfig(self) -> None:
        """Persist addon-specific state to ``self.app.config``."""

    def setupIcons(self) -> None:
        """Assign themed icons to addon widgets."""

    def updateColorSet(self) -> None:
        """React to a global color-set change."""

