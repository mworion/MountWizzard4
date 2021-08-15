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
#
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import socket
import logging
import uuid

# external packages

# local imports


class Connection(object):
    """
    The class Connection provides the command and reply interface to a 10 micron mount.
    There should be all commands and their return values be sent to the mount via
    IP and the responses.

    Define the number of chunks for the return bytes in case of not having them in
    bulk mode this is needed, because the mount computer  doesn't support a
    transaction base like number of chunks to be expected. It's just plain data and
    I have to find out myself how much it is. there are three types of commands:

          a) no reply               this is ok -> COMMAND_A
          b) reply without '#'      this is the bad part, don't like it -> COMMAND_B
          c) reply ended with '#'   this is normal feedback -> no special treatment

    The class itself need parameters for the host and port to be able to interact
    with the mount.

        >>> command = Connection(
        >>>                   host=('127.0.0.1', 3492),
        >>>                   )

    """

    __all__ = ['Connection',
               ]

    log = logging.getLogger(__name__)

    # I don't want so wait to long for a response. In average I see values
    # shorter than 0.5 sec, so 2 seconds should be good
    SOCKET_TIMEOUT = 3

    # complete used command list to be checked first if valid
    # these are the commands, which were used in mountcontrol so far
    COMMANDS = [':AP',
                ':CM',
                ':FLIP',
                ':GDW', ':GDA', ':GDF', ':GDS', ':GDGPS', ':GJD1',
                ':GDUT', ':GDUTV',
                ':GLDT', ':GMs', ':GMsa', ':GMsb', ':GMACW', ':GMAC',
                ':GREF', ':GRPRS', ':GRTMP',
                ':GS', ':GT', ':GTMP1', ':GUDT',
                ':GVD', ':GVN', ':GVP', ':GVT', ':GVZ',
                ':GWOL', ':Ga', ':GaXa', ':GaXb',
                ':Gd', ':Gdat', ':Gev', ':Gg', ':Gh', ':GINQ', ':Ginfo', ':Glms',
                ':Glmt', ':Gmte', ':Go', ':Gr', ':Gt', ':gtg', ':GTsid',
                ':Guaf', ':Gz',
                ':MA', ':MS', ':MaX', ':Me', ':Mn', ':Ms', ':Mw',
                ':MSao', ':MSap',
                ':NTGdisc', ':NTGweb', ':NTSdisc', ':NTSweb',
                ':NUtim',
                ':PO', ':PO', ':PO', ':PaX', ':PiP',
                ':Q', ':QaXa', ':QaXb', ':Qe', ':Qn', ':Qs', ':Qw',
                ':RC', ':Rc', ':RG', ':RM', ':RMs', ':RS',
                ':RT0', ':RT1', ':RT2', ':RT9',
                ':SDAr', ':SREF', ':SRPRS', ':SRTMP', ':STOP', ':SWOL',
                ':Sa', ':SaXa', ':SaXb', ':Sd',
                ':Sdat', ':Sev', ':Sev', ':Sg', ':Sg', ':Sh', ':Slms', ':Slmt',
                ':So', ':Sr', ':St', ':Suaf', ':Sw', ':Sz',
                ':TLEG', ':TLEL0', ':TLEGAZ', ':TLEGEQ', ':TLEP', ':TLES',
                ':TLESCK',
                ':TRNEW', ':TRADD', ':TRP', ':TRREPLAY',
                ':U2',
                ':delalig', ':delalst',
                ':endalig',
                ':getain', ':getalp', ':getalst',
                ':hP',
                ':modelcnt', ':modeldel0', ':modelld0', ':modelnam',
                ':modelsv0',
                ':newalig', ':newalpt',
                ':WSG', ':WSP', ':WST', ':WSH', ':WSD', ':WSS',
                ':shutdown',
                ]

    # Command list for commands which don't reply anything
    COMMAND_A = [':AP', ':hP',
                 ':Me', ':Mn', ':Ms', ':Mw',
                 ':PO',
                 ':Q', ':Qe', ':Qn', ':Qs', ':Qw',
                 ':RC', ':Rc', ':RG', ':RM', ':RS', ':RT0', ':RT1', ':RT2',
                 ':RT9',
                 ':SDAr', ':STOP',
                 ':U2',
                 ':hP', ':Suaf',
                 ]

    # Command list for commands which have a response, but have no end mark
    # mostly these commands response value of '0' or '1'
    COMMAND_B = [':FLIP', ':shutdown', ':GREF', ':Guaf',
                 ':MA',
                 ':RMs',
                 ':SREF', ':SRPRS', ':Sa', ':Sev', ':Sr',
                 ':SRTMP', ':Slmt', ':Slms', ':St', ':Sg', ':Sw', ':Sz',
                 ':Sdat', ':Gdat',
                 ':GTsid', ':So', ':Sh', ':Sd', ':MSap', ':MSao', ':MS',
                 ':WSS', ':SWOL'
                 ]

    def __init__(self,
                 host=None,
                 ):

        self.host = host
        self.id = str(uuid.uuid4())[:8]

    def validCommand(self, command):
        """
        validCommand test if command is valid and known.

        :param command: command for 10 micron to test
        :return: True if valid commands were issued
        """

        for key in sorted(self.COMMANDS, reverse=True):
            if command.startswith(key):
                return True
        return False

    def validCommandSet(self, commandString):
        """
        validCommandSet test if all commands in the commandString are valid
        and known.

        :param commandString: command for 10 micron to test
        :return: True if valid commands were issued
        """

        commandSet = commandString.split('#')[:-1]
        for command in commandSet:
            if not self.validCommand(command):
                return False
        return True

    def analyseCommand(self, commandString):
        """
        analyseCommand parses the provided commandString against the two command
        type A and B to evaluate if a response is expected and how many chunks of
        data show be received.

        the command slots will be sorted in reverse order to ensure that longer
        commands with the same leading characters will be tested first. otherwise
        the test will be ended before testing al commands.

        :param commandString:       string sent to the mount
        :return: chunksToReceive:   counted chunks
                 noResponse:        True, if we should not wait for receiving data
        """

        chunksToReceive = 0
        getData = False
        commandSet = commandString.split('#')[:-1]
        minBytes = 0
        for command in commandSet:
            foundCOMMAND_A = False
            for key in sorted(self.COMMAND_A, reverse=True):
                if command.startswith(key):
                    if key == ':Q':
                        continue
                    foundCOMMAND_A = True
                    break
            if not foundCOMMAND_A:
                getData = True
                for keyBad in sorted(self.COMMAND_B, reverse=True):
                    if command.startswith(keyBad):
                        minBytes += 1
                        break
                else:
                    chunksToReceive += 1
        return chunksToReceive, getData, minBytes

    def closeClientHard(self, client):
        """
        closeClientHard tries to shutdown a socket in case of error hard

        :param client:
        :return: success
        """
        if not client:
            return False

        try:
            client.shutdown(socket.SHUT_RDWR)
            client.close()

        except Exception as e:
            self.log.warning(f'hard close: {e}')
            return False

        return True

    def buildClient(self):
        """
        buildClient checks necessary information and tries to open a socket.
        if success it returns the client (socket connection)

        :return: client for socket connection if succeeded
        """
        if not self.host:
            self.log.info(f'[{self.id}] no host defined')
            return None

        if not isinstance(self.host, tuple):
            self.log.info(f'[{self.id}] host entry malformed')
            return None

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(self.SOCKET_TIMEOUT)
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

        try:
            client.connect(self.host)

        except socket.timeout:
            self.closeClientHard(client)
            self.log.debug(f'[{self.id}] socket timeout')
            return None

        except socket.error as e:
            self.closeClientHard(client)
            self.log.debug(f'[{self.id}] socket error: {e}')
            return None

        except Exception as e:
            self.closeClientHard(client)
            self.log.debug(f'[{self.id}] socket error: {e}')
            return None

        else:
            return client

    def sendData(self, client=None, commandString=''):
        """
        sendData sends all data of the command string out to the given socket client.

        :param client: socket client
        :param commandString: command to mount as string
        :return: success
        """
        try:
            client.sendall(commandString.encode())

        except Exception as e:
            self.closeClientHard(client)
            self.log.debug(f'[{self.id}] socket error: {e}')
            return False

        else:
            return True

    def receiveData(self, client=None, numberOfChunks=0, minBytes=0):
        """
        receive Data waits on the give socket client for a number of chunks to
        be receive or a minimum set of bytes received. the chunks are delimited
        with #. the min bytes is necessary, because the mount computer has
        commands which giv a response without delimiter. this is bad, but status.

        :param client: socket client
        :param numberOfChunks: number of data chunks
        :param minBytes: minimum number of data bytes
        :return: success and response data
        """

        response = ''
        receiving = True
        try:
            while receiving:
                chunkRaw = client.recv(2048)
                try:
                    chunk = chunkRaw.decode('ASCII')

                except Exception as e:
                    self.log.warning(f'[{self.id}] {e}, {chunkRaw}')
                    return False, ''

                if not chunk:
                    break

                response += chunk
                if numberOfChunks == 0 and len(response) == minBytes:
                    break

                elif numberOfChunks != 0 and numberOfChunks == response.count('#'):
                    break

        except socket.timeout:
            self.log.debug(f'[{self.id}] socket timeout')
            return False, response

        except Exception as e:
            self.log.debug(f'[{self.id}] socket error: {e}')
            return False, response

        else:
            response = response.rstrip('#').split('#')
            self.log.trace(f'[{self.id}] response : {response}')
            return True, response

    def communicate(self, commandString):
        """
        transfer open a socket to the mount, takes the command string for the
        mount, analyses it, check validity and finally if valid sends it to the
        mount. If response expected, wait for the response and returns the data.

        :param commandString:
        :return: success:           True or False for full transfer
                 response:          the data load
                 numberOfChunks:    number of responses chunks which were
                                    split with #
        """

        if not self.validCommandSet(commandString):
            self.log.warning(f'[{self.id}] unknown commands: {commandString}')
            return False, 'wrong commands', 0

        numberOfChunks, getData, minBytes = self.analyseCommand(commandString)
        logFormat = '[{0}] sending  : {1}, getData: {2}, minBytes: {3}, chunks: {4}, host: {5}'
        self.log.trace(logFormat.format(self.id,
                                        commandString,
                                        getData,
                                        minBytes,
                                        numberOfChunks,
                                        self.host,
                                        ))

        client = self.buildClient()
        if client is None:
            return False, '', numberOfChunks

        suc = self.sendData(client=client,
                            commandString=commandString)
        if not suc:
            return False, '', numberOfChunks

        if not getData:
            self.closeClientHard(client)
            return True, '', numberOfChunks

        suc, response = self.receiveData(client=client,
                                         numberOfChunks=numberOfChunks,
                                         minBytes=minBytes)
        self.closeClientHard(client)
        del client

        return suc, response, numberOfChunks
