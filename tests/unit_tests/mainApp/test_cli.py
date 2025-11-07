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
import pytest
import sys
import os
import argparse
from unittest.mock import patch
import mw4.cli as cli


def test_read_options_default_values(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mw4.cli"])
    opts = cli.read_options()
    assert opts.dpi == 96
    assert opts.scale == 1


def test_read_options_with_dpi_argument(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mw4.cli", "--dpi", "120"])
    opts = cli.read_options()
    assert opts.dpi == 120.0
    assert opts.scale == 1


def test_read_options_with_scale_argument(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mw4.cli", "--scale", "1.5"])
    opts = cli.read_options()
    assert opts.dpi == 96
    assert opts.scale == 1.5


def test_read_options_with_both_arguments(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mw4.cli", "-d", "144", "-s", "2.0"])
    opts = cli.read_options()
    assert opts.dpi == 144.0
    assert opts.scale == 2.0


def test_read_options_short_flags(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mw4.cli", "-d", "72", "-s", "0.8"])
    opts = cli.read_options()
    assert opts.dpi == 72.0
    assert opts.scale == 0.8


def test_read_options_returns_namespace(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mw4.cli"])
    opts = cli.read_options()
    assert isinstance(opts, argparse.Namespace)


@patch("mw4.cli.main")
@patch("platform.system")
def test_app_on_windows_sets_environment_variables(mock_platform, mock_main, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mw4.cli", "--dpi", "120", "--scale", "1.5"])
    mock_platform.return_value = "Windows"

    monkeypatch.delenv("QT_SCALE_FACTOR", raising=False)
    monkeypatch.delenv("QT_FONT_DPI", raising=False)

    cli.app()

    assert os.environ["QT_SCALE_FACTOR"] == "1.5"
    assert os.environ["QT_FONT_DPI"] == "120"
    mock_main.assert_called_once()


@patch("mw4.cli.main")
@patch("platform.system")
def test_app_on_linux_does_not_set_environment_variables(
    mock_platform, mock_main, monkeypatch
):
    monkeypatch.setattr(sys, "argv", ["mw4.cli", "--dpi", "120", "--scale", "1.5"])
    mock_platform.return_value = "Linux"

    monkeypatch.delenv("QT_SCALE_FACTOR", raising=False)
    monkeypatch.delenv("QT_FONT_DPI", raising=False)

    cli.app()

    assert "QT_SCALE_FACTOR" not in os.environ
    assert "QT_FONT_DPI" not in os.environ
    mock_main.assert_called_once()


@patch("mw4.cli.main")
@patch("platform.system")
def test_app_on_darwin_does_not_set_environment_variables(
    mock_platform, mock_main, monkeypatch
):
    monkeypatch.setattr(sys, "argv", ["mw4.cli"])
    mock_platform.return_value = "Darwin"

    cli.app()

    mock_main.assert_called_once()


@patch("mw4.cli.main")
@patch("platform.system")
def test_app_with_float_formatting(mock_platform, mock_main, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mw4.cli", "--dpi", "96.7", "--scale", "1.25"])
    mock_platform.return_value = "Windows"

    monkeypatch.delenv("QT_SCALE_FACTOR", raising=False)
    monkeypatch.delenv("QT_FONT_DPI", raising=False)

    cli.app()

    assert os.environ["QT_SCALE_FACTOR"] == "1.2"
    assert os.environ["QT_FONT_DPI"] == "97"


@patch("mw4.cli.main")
@patch("platform.system")
def test_app_calls_main_function(mock_platform, mock_main, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mw4.cli"])
    mock_platform.return_value = "Linux"

    cli.app()

    mock_main.assert_called_once()


def test_read_options_with_negative_values(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mw4.cli", "--dpi", "-1", "--scale", "-0.5"])
    opts = cli.read_options()
    assert opts.dpi == -1.0
    assert opts.scale == -0.5
