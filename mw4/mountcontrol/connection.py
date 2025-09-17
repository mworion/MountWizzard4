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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
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
    The class Connection provides the command and reply interface to a 10 micron
    mount. There should be all commands and their return values be sent to the
    mount via IP and the responses.

    Define the number of chunks for the return bytes in case of not having them
    in bulk mode this is needed, because the mount computer  doesn't support a
    transaction base like number of chunks to be expected. It's just plain data
    and I have to find out myself how much it is. there are three types of
    commands:

          a) no reply               this is ok -> COMMAND_A
          b) reply without '#'      this is the bad part, don't like it -> COMMAND_B
          c) reply ended with '#'   this is normal feedback -> no special treatment

    The class itself need parameters for the host and port to be able to interact
    with the mount.
    """

    log = logging.getLogger("MW4")

    # I don't want so wait to long for a response. In average, I see values
    # shorter than 0.5 sec, so 3 seconds should be good
    SOCKET_TIMEOUT = 3

    # complete used command list to be checked first if valid
    # these are the commands, which were used in mountcontrol so far
    COMMANDS = [
        ":AP",
        ":CM",
        ":CMCFG",
        ":FLIP",
        ":GDW",
        ":GDA",
        ":GDF",
        ":GDS",
        ":GDGPS",
        ":GJD1",
        ":GDUT",
        ":GDUTV",
        ":GLDT",
        ":GMs",
        ":GMsa",
        ":GMsb",
        ":GMACW",
        ":GMAC",
        ":GREF",
        ":GRPRS",
        ":GRTMP",
        ":GS",
        ":GT",
        ":GTMP1",
        ":GUDT",
        ":GVD",
        ":GVN",
        ":GVP",
        ":GVT",
        ":GVZ",
        ":GWOL",
        ":Ga",
        ":GaE",
        ":GaXa",
        ":GaXb",
        ":Gd",
        ":Gdat",
        ":Gev",
        ":Gg",
        ":Gh",
        ":GINQ",
        ":Ginfo",
        ":Glms",
        ":Glmt",
        ":Gmte",
        ":Go",
        ":Gr",
        ":Gt",
        ":gtg",
        ":GTsid",
        ":Gstm",
        ":Guaf",
        ":Gz",
        ":MA",
        ":MS",
        ":MSao",
        ":MSap",
        ":MaX",
        ":Me",
        ":Mn",
        ":Ms",
        ":Mw",
        ":NTGdisc",
        ":NTGweb",
        ":NTSdisc",
        ":NTSweb",
        ":NUtim",
        ":PO",
        ":PO",
        ":PO",
        ":PaX",
        ":PiP",
        ":Q",
        ":QaXa",
        ":QaXb",
        ":Qe",
        ":Qn",
        ":Qs",
        ":Qw",
        ":RC",
        ":Rc",
        ":RG",
        ":RM",
        ":RMs",
        ":RS",
        ":RT0",
        ":RT1",
        ":RT2",
        ":RT9",
        ":SDAr",
        ":SREF",
        ":SRPRS",
        ":SRTMP",
        ":STOP",
        ":SWOL",
        ":Sa",
        ":SaXa",
        ":SaXb",
        ":Sd",
        ":Sdat",
        ":Sev",
        ":Sev",
        ":Sg",
        ":Sg",
        ":Sh",
        ":Slms",
        ":Slmt",
        ":Sstm",
        ":So",
        ":Sr",
        ":St",
        ":Suaf",
        ":Sw",
        ":Sz",
        ":TLEG",
        ":TLEL0",
        ":TLEGAZ",
        ":TLEGEQ",
        ":TLEP",
        ":TLES",
        ":TLESCK",
        ":TROFFADD",
        ":TROFFCLR",
        ":TROFFGET",
        ":TROFFSET",
        ":TRNEW",
        ":TRADD",
        ":TRP",
        ":TRREPLAY",
        ":U2",
        ":WSG",
        ":WSP",
        ":WST",
        ":WSH",
        ":WSD",
        ":WSS",
        ":delalig",
        ":delalst",
        ":endalig",
        ":getain",
        ":getalp",
        ":getalst",
        ":hP",
        ":modelcnt",
        ":modeldel0",
        ":modelld0",
        ":modelnam",
        ":modelsv0",
        ":newalig",
        ":newalpt",
        ":shutdown",
    ]

    # Command list for commands which don't reply to anything
    COMMAND_A = [
        ":AP",
        ":hP",
        ":Me",
        ":Mn",
        ":Ms",
        ":Mw",
        ":PO",
        ":Q",
        ":Qe",
        ":Qn",
        ":Qs",
        ":Qw",
        ":RC",
        ":Rc",
        ":RG",
        ":RM",
        ":RS",
        ":RT0",
        ":RT1",
        ":RT2",
        ":RT9",
        ":SDAr",
        ":STOP",
        ":Suaf",
        ":U2",
        ":hP",
    ]

    # Command list for commands which don't reply to anything, but give a parameter
    COMMAND_P = [":RC", ":Rc", ":RG", ":Suaf"]

    # Command list for commands which have a response but have no end mark
    # mostly these commands response value of '0' or '1'
    COMMAND_B = [
        ":CM",
        ":CMCFG",
        ":FLIP",
        ":shutdown",
        ":GREF",
        ":Guaf",
        ":MA",
        ":RMs",
        ":SREF",
        ":SRPRS",
        ":Sa",
        ":Sev",
        ":Sr",
        ":SRTMP",
        ":Slmt",
        ":Slms",
        ":St",
        ":Sg",
        ":Sw",
        ":Sz",
        ":Sdat",
        ":Gdat",
        ":Sstm",
        ":GTsid",
        ":So",
        ":Sh",
        ":Sd",
        ":MSap",
        ":MSao",
        ":MS",
        ":WSS",
        ":SWOL",
    ]

    def __init__(self, host=None):
        self.host = host
        self.id = str(uuid.uuid4())[:8]

    def validCommand(self, command):
        """ """
        for key in sorted(self.COMMANDS, reverse=True):
            if command.startswith(key):
                return True
        return False

    def validCommandSet(self, commandString):
        """ """
        commandSet = commandString.split("#")[:-1]
        for command in commandSet:
            if not self.validCommand(command):
                self.log.warning(f"[{self.id}] unknown commands: {commandString}")
                return False
        return True

    def analyseCommand(self, commandString):
        """
        analyseCommand parses the provided commandString against the two command
        types A and B to evaluate if a response is expected and how many chunks of
        data show be received.

        the command slots will be sorted in reverse order to ensure that longer
        commands with the same leading characters will be tested first. otherwise,
        the test will be ended before testing al commands.
        """
        chunksToReceive = 0
        getData = False
        commandSet = commandString.split("#")[:-1]
        minBytes = 0
        for command in commandSet:
            foundCOMMAND_A = False
            for key in sorted(self.COMMAND_A, reverse=True):
                if command.startswith(key):
                    if len(command) != len(key) and key not in self.COMMAND_P:
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
        t = f"Analyse: minBytes: [{minBytes}], numOfChunks: [{chunksToReceive}]"
        t += ", host: [{self.host}]"
        self.log.trace(t)
        return chunksToReceive, getData, minBytes

    @staticmethod
    def closeClientHard(client):
        """ """
        if not client:
            return

        try:
            client.shutdown(socket.SHUT_RDWR)
            client.close()

        except Exception:
            return

    def buildClient(self):
        """ """
        if not self.host:
            self.log.info(f"[{self.id}] no host defined")
            return None
        if not isinstance(self.host, tuple):
            self.log.info(f"[{self.id}] host entry malformed [{self.host}]")
            return None

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(self.SOCKET_TIMEOUT)
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        try:
            client.connect(self.host)

        except socket.timeout:
            self.closeClientHard(client)
            self.log.debug(f"[{self.id}] socket timeout")
            return None

        except Exception as e:
            self.closeClientHard(client)
            self.log.debug(f"[{self.id}] socket general: [{e}]")
            return None

        else:
            return client

    def sendData(self, client=None, commandString=""):
        """
        sendData sends all data of the command string out to the given socket
        client.
        """
        try:
            self.log.trace(f"[{self.id}] sending  : {commandString}")
            client.sendall(commandString.encode())

        except Exception as e:
            self.closeClientHard(client)
            self.log.debug(f"[{self.id}] socket error: [{e}]")
            return False

        else:
            return True

    def receiveData(self, client=None, numberOfChunks=0, minBytes=0):
        """
        receive Data waits on the give socket client for a number of chunks to
        be received or a minimum set of bytes received. the chunks are delimited
        with #. the min bytes are necessary because the mount computer has
        commands which give a response without a delimiter. this is bad, but status.

        :param client: socket client
        :param numberOfChunks: number of data chunks
        :param minBytes: minimum number of data bytes
        :return: success and response data
        """
        response = ""
        receiving = True
        try:
            while receiving:
                chunkRaw = client.recv(2048)
                try:
                    chunk = chunkRaw.decode("ASCII")
                except Exception as e:
                    self.log.warning(f"[{self.id}] error: [{e}], received: [{chunkRaw}]")
                    return False, ""

                if not chunk:
                    break

                response += chunk
                if numberOfChunks == 0 and len(response) == minBytes:
                    break
                elif numberOfChunks != 0 and numberOfChunks == response.count("#"):
                    break

        except socket.timeout:
            self.log.debug(f"[{self.id}] socket timeout")
            return False, response

        except Exception as e:
            self.log.debug(f"[{self.id}] socket error: [{e}]")
            return False, response

        else:
            response = response.rstrip("#").split("#")
            self.log.trace(f"Response [{self.id}]: [{response}]")
            return True, response

    def communicate(self, commandString, responseCheck=""):
        """
        transfer open a socket to the mount, takes the command string for the
        mount, analyses it, check validity and finally if valid sends it to the
        mount. If a response is expected, wait for the response and return the data.
        """
        if not self.validCommandSet(commandString):
            return False, "", 0

        numberOfChunks, getData, minBytes = self.analyseCommand(commandString)
        client = self.buildClient()
        if client is None:
            return False, "", numberOfChunks

        if not self.sendData(client=client, commandString=commandString):
            return False, "", numberOfChunks

        if not getData:
            self.closeClientHard(client)
            return True, "", numberOfChunks

        suc, response = self.receiveData(
            client=client, numberOfChunks=numberOfChunks, minBytes=minBytes
        )
        self.closeClientHard(client)
        if responseCheck:
            suc = suc and response[0] == responseCheck

        return suc, response, numberOfChunks

    def communicateRaw(self, commandString: str) -> tuple:
        """ """
        client = self.buildClient()
        if client is None:
            return False, False, "Socket error"

        sucSend = self.sendData(client=client, commandString=commandString)
        try:
            chunkRaw = client.recv(2048)
            val = chunkRaw.decode("ASCII")
        except socket.timeout:
            self.log.debug(f"[{self.id}] socket timeout")
            val = "Timeout"
            sucRec = False
        except Exception as e:
            self.log.debug(f"[{self.id}] socket error: [{e}]")
            val = "Exception"
            sucRec = False
        else:
            self.log.trace(f"[{self.id}] response: [{val}]")
            sucRec = True

        return sucSend, sucRec, val
