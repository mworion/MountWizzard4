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
import os
import pytest
import logging
from unittest import mock
from unittest.mock import MagicMock
from pathlib import Path

# external packages

# local import
from mw4.base import loggerMW
from mw4.base.loggerMW import setupLogging, LoggerWriter


@pytest.fixture
def clean_log_directory():
    """Fixture to ensure the log directory is clean before each test."""
    log_dir = Path("./log")
    if log_dir.exists():
        for log_file in log_dir.glob("*.log"):
            log_file.unlink()
    yield
    # Cleanup after test
    if log_dir.exists():
        for log_file in log_dir.glob("*.log"):
            log_file.unlink()


def test_loggerwriter_write_single_line():
    mock_level = MagicMock()
    writer = LoggerWriter(level=mock_level, mode="INFO", std="stdout")
    writer.write("Test message")
    mock_level.assert_called_once_with("[INFO] Test message")


def test_loggerwriter_write_multi_line():
    mock_level = MagicMock()
    writer = LoggerWriter(level=mock_level, mode="DEBUG", std="stderr")
    writer.write("Line 1\nLine 2\nLine 3")
    assert mock_level.call_count == 3
    mock_level.assert_any_call("[DEBUG] Line 1")
    mock_level.assert_any_call("         Line 2")
    mock_level.assert_any_call("         Line 3")


def test_loggerwriter_flush():
    mock_level = MagicMock()
    writer = LoggerWriter(level=mock_level, mode="INFO", std="stdout")
    assert writer.flush() is None


def test_setupLogging_creates_log_directory(clean_log_directory):
    setupLogging()
    assert os.path.isdir("./log"), "Log directory should be created."


def test_setupLogging_creates_log_file(clean_log_directory):
    setupLogging()
    log_dir = Path("./log")
    log_files = list(log_dir.glob("mw4-*.log"))
    assert len(log_files) == 1, "A log file should be created."
    assert log_files[0].is_file(), "The created log file should be a valid file."


def test_setupLogging_configures_logging_format(clean_log_directory):
    setupLogging()
    logger = logging.getLogger()
    assert logger.handlers, "Logger should have at least one handler."
    handler = logger.handlers[0]
    assert isinstance(handler, logging.Handler), (
        "Handler should be an instance of logging.Handler."
    )
    formatter = handler.formatter


def test_setupLogging_configures_specific_log_levels(clean_log_directory):
    setupLogging()
    assert logging.getLogger("PySide6").level == logging.WARNING, (
        "PySide6 logger level should be WARNING."
    )
    assert logging.getLogger("requests").level == logging.WARNING, (
        "Requests logger level should be WARNING."
    )
    assert logging.getLogger("urllib3").level == logging.WARNING, (
        "Urllib3 logger level should be WARNING."
    )
    assert logging.getLogger("astropy").level == logging.WARNING, (
        "Astropy logger level should be WARNING."
    )
    assert logging.getLogger("keyring").level == logging.WARNING, (
        "Keyring logger level should be WARNING."
    )


def test_setupLogging_custom_log_levels(clean_log_directory):
    setupLogging()
    assert hasattr(logging, "TRACE"), "Custom TRACE level should be defined in logging."
    assert hasattr(logging, "UI"), "Custom UI level should be defined in logging."
    assert hasattr(logging, "HEADER"), "Custom HEADER level should be defined in logging."


def test_setupLogging():
    with mock.patch.object(os.path, "isdir", return_value=False):
        with mock.patch.object(os, "mkdir"):
            loggerMW.setupLogging()


def test_setCustomLoggingLevel():
    loggerMW.setCustomLoggingLevel()
