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
###########################################################
"""Verify that bootstrap functions are importable with camelCase names."""


def test_names_importable():
    """The camelCase names are importable from mw4.base.bootstrap."""
    from mw4.base.bootstrap import (
        configureEnvironment,
        exceptHook,
        extractDataFiles,
        minimizeStartTerminal,
        setupWorkDirs,
        writeSystemInfo,
    )
    assert callable(configureEnvironment)
    assert callable(exceptHook)
    assert callable(extractDataFiles)
    assert callable(minimizeStartTerminal)
    assert callable(setupWorkDirs)
    assert callable(writeSystemInfo)
