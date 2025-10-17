############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import argparse
import platform

# external packages
import unittest.mock as mock

# local import
import mw4.cli
from mw4.cli import app, read_options


@mock.patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(dpi=96, scale=1))
def test_read_options(test_options):
    options = read_options()
    assert options.dpi == 96
    assert options.scale == 1


@mock.patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(dpi=96, scale=1))
def test_app_1(test_options):
    with mock.patch.object(mw4.cli, "main"):
        with mock.patch.object(mw4.cli, "read_options"):
            app()


@mock.patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(dpi=96, scale=1))
def test_app_2(test_options):
    with mock.patch.object(mw4.cli, "main"):
        with mock.patch.object(platform, "system", return_value="Windows"):
            app()


