############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
# external packages
# local imports


class IndiBaseMediator:

    __all__ = ['IndiBaseMediator',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    def __init__(self):
        pass

    def new_device(self, device):
        self.logger.info('new_device: {0}'.format(device.name))

    def remove_device(self, device):
        self.logger.info('remove_device: {0}'.format(device.name))

    def new_property(self, iproperty):
        self.logger.info('new_property: {0}'.format(iproperty.name))

    def remove_property(self, iproperty):
        self.logger.info('remove_property: {0}'.format(iproperty.name))

    def new_blob(self, blob):
        self.logger.info('new_blob element: {0} in BLOB blob {3}'
                         .format(blob.name, blob.size, blob.format, blob.parent.name))

    def new_switch(self, switch):
        self.logger.info('new_switch: {0}'.format(switch.name))

    def new_number(self, number):
        self.logger.info('new_number: {0}'.format(number.name))

    def new_text(self, text):
        self.logger.info('new_text: {0}'.format(text.name))

    def new_light(self, light):
        self.logger.info('new_light: {0}'.format(light.name))

    def new_message(self, device, message_id):
        self.logger.info('new_message(id={0})'
                         .format(message_id, device.messageQueue(message_id)))

    def new_universal_message(self, message):
        self.logger.info('new_universal_message: {0}'.format(message))

    def server_connected(self):
        self.logger.info('server_connected')

    def server_disconnected(self, exit_code):
        self.logger.info('server_disconnected: {0}'.format(str(exit_code)))
