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
import unittest.mock as mock


def test_main_imports_run():
    """Test that __main__ module successfully imports and calls run()."""
    with mock.patch("mw4.cli.run") as mock_run:
        import mw4.__main__  # noqa: F401

        assert mock_run is not None
