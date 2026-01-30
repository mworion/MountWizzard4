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
import argparse
import os
import platform
from mw4.loader import main


def read_options() -> argparse.Namespace:
    """ """
    parser = argparse.ArgumentParser(
        prog=__name__,
        description="MountWizzard4",
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
        "-t",
        "--test",
        default=0,
        type=int,
        dest="test",
    )
    parser.add_argument(
        "-s",
        "--scale",
        default=1,
        type=float,
        dest="scale",
        help="Setting Qt DPI scale factor (+scale = +size, default=1)",
    )
    parser.add_argument(
        "-e",
        action="store_true",
        dest="efficient",
        default=0,
        type=int,
        help="Efficient CPU mode",
    )
    return parser.parse_args()


def app():
    options = read_options()
    if platform.system() == "Windows":
        os.environ["QT_SCALE_FACTOR"] = f"{options.scale:2.1f}"
        os.environ["QT_FONT_DPI"] = f"{options.dpi:2.0f}"
    main(options.efficient == 1, options.test)


if __name__ == "__main__":
    app()
