############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Installer for MountWizzard4
#
# a Python-based Tool for interaction with the
# 10micron mounts GUI with PyQT5/6
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
import argparse
import platform
import os
from mw4.loader import main


def read_options() -> argparse.Namespace:
    """ """
    parser = argparse.ArgumentParser(
        prog=__name__,
        description="Installs MountWizzard4 in Python virtual "
        "environment in local workdir",
    )
    parser.add_argument(
        "-d",
        "--dpi",
        default=96,
        type=float,
        dest="dpi",
        help="Setting QT font DPI (+dpi = -fontsize, default=96)",
    )
    parser.add_argument(
        "-s",
        "--scale",
        default=1,
        type=float,
        dest="scale",
        help="Setting Qt DPI scale factor (+scale = +size, default=1)",
    )
    return parser.parse_args()


def app():
    options = read_options()
    if platform.system() == "Windows":
        os.environ["QT_SCALE_FACTOR"] = f"{options.scale:2.1f}"
        os.environ["QT_FONT_DPI"] = f"{options.dpi:2.0f}"
    main()


if __name__ == "__main__":
    app()
