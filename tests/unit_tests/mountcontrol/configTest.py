############################################################
# -*- coding: utf-8 -*-
#
# MOUNTCONTROL
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
############################################################
# standard libraries
import logging
# external packages
# local imports

handler = logging.FileHandler('unittest.log')

logging.basicConfig(level=logging.DEBUG,
                    handlers=[handler],
                    format='[%(asctime)s.%(msecs)03d]'
                           + '[%(levelname)7s]'
                           + '[%(filename)15s]'
                           + '[%(lineno)5s]'
                           + '[%(funcName)20s]'
                           + '[%(threadName)10s]'
                           + ' > %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', )
