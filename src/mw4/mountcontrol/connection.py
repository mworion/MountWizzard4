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
import logging
import socket
import uuid
from typing import Any


class Connection:
    """
    The class Connection provides the command and reply interface to a 10 micron
    mount. There should be all commands and their return values be sent to the
    mount via IP and the responses.

    Define the number of chunks for the return bytes in case of not having them
    in bulk mode this is needed, because the mount computer doesn't support a
    transaction base like the number of chunks to be expected. It's just plain data,
    and I have to find myself out how much it is. There are three types of
    commands:

          a) no reply               this is ok -> COMMAND_A
          b) reply without '#'      this is the bad part, don't like it -> COMMAND_B
          c) reply ended with '#'   this is normal feedback -> no special treatment

    The class itself needs parameters for the host and port to be able to interact
    with the mount.
    """

    log = logging.getLogger("MW4")
    SOCKET_TIMEOUT = 10
    COMMANDS: tuple[str, ...] = tuple(
        sorted(
            [
                ":AP",
                ":CM",
                ":CMCFG",
                ":FLIP",
                ":GAPO",
                ":GCFG",
                ":GDW",
                ":GDA",
                ":GDF",
                ":GDS",
                ":GDGPS",
                ":GDUT",
                ":GDUTV",
                ":GJD1",
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
                ":gtgpps",
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
                ":SAPO",
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
            ],
            reverse=True,
        )
    )

    # Command list for commands which don't reply to anything
    COMMAND_A: tuple[str, ...] = tuple(
        sorted(
            [
                ":AP",
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
            ],
            reverse=True,
        )
    )

    # Command list for commands which don't reply to anything, but give a parameter
    COMMAND_P: tuple[str, ...] = (":RC", ":Rc", ":RG", ":Suaf")

    # Command list for commands which have a response but have no end mark;
    # mostly these commands respond with a value of '0' or '1'
    COMMAND_B: tuple[str, ...] = tuple(
        sorted(
            [
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
            ],
            reverse=True,
        )
    )

    def __init__(self, parent: Any) -> None:
        self.host = (parent.config.hostAddress, parent.config.port)
        self.loggingTrace = parent.loggingTrace
        self.id = str(uuid.uuid4())[:8]

    def validCommand(self, command: str) -> bool:
        return any(command.startswith(key) for key in self.COMMANDS)

    def validCommandSet(self, commandString: str) -> bool:
        commandSet = commandString.split("#")[:-1]
        for command in commandSet:
            if not self.validCommand(command):
                self.log.warning(f"[{self.id}] unknown commands: {commandString}")
                return False
        return True

    def analyseCommand(self, commandString: str) -> tuple[int, bool, int]:
        chunksToReceive = 0
        getData = False
        commandSet = commandString.split("#")[:-1]
        minBytes = 0
        for command in commandSet:
            foundCOMMAND_A = False
            for key in self.COMMAND_A:
                if command.startswith(key):
                    if len(command) != len(key) and key not in self.COMMAND_P:
                        continue
                    foundCOMMAND_A = True
                    break
            if not foundCOMMAND_A:
                getData = True
                for keyBad in self.COMMAND_B:
                    if command.startswith(keyBad):
                        minBytes += 1
                        break
                else:
                    chunksToReceive += 1
        if self.loggingTrace:
            t = f"[Trace] Analyse  [{self.id}]: minBytes: [{minBytes}],"
            t += f" numOfChunks: [{chunksToReceive}], host: [{self.host}]"
            self.log.debug(t)
        return chunksToReceive, getData, minBytes

    def closeClientHard(self, client: socket.socket | None) -> None:
        if not client:
            return
        try:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        except Exception as e:
            self.log.warning(f"Error    [{self.id} {e}]: closing socket client")

    def buildClient(self) -> socket.socket | None:
        if not self.host:
            self.log.info(f"No host  [{self.id}]")
            return None
        if not isinstance(self.host, tuple):
            self.log.info(f"Host     [{self.id}]: host entry malformed [{self.host}]")
            return None

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(self.SOCKET_TIMEOUT)
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        try:
            client.connect(self.host)
        except TimeoutError:
            self.closeClientHard(client)
            self.log.debug(f"Timeout  [{self.id}]: socket timeout in build client")
            return None
        except Exception as e:
            self.closeClientHard(client)
            self.log.warning(f"Error    [{self.id}]: socket general: [{e}] in build client")
            return None
        else:
            return client

    def sendData(self, client: socket.socket, commandString: str) -> bool:
        try:
            if self.loggingTrace:
                self.log.debug(f"[Trace] Sending  [{self.id}]: [{commandString}]")
            client.sendall(commandString.encode())
        except TimeoutError:
            self.closeClientHard(client)
            if self.loggingTrace:
                self.log.debug(f"[Trace] Timeout  [{self.id}]: socket timeout in send data")
            return False
        except Exception as e:
            self.closeClientHard(client)
            self.log.warning(f"[Trace] Error    [{self.id}]: socket error: [{e}] in send data")
            return False
        else:
            return True

    def receiveData(
        self, client: socket.socket, numberOfChunks: int, minBytes: int
    ) -> tuple[bool, list[str]]:
        """
        receive Data waits on the give socket client for a number of chunks to
        be received or a minimum set of bytes received. the chunks are delimited
        with #. the min bytes are necessary because the mount computer has
        commands which give a response without a delimiter. this is bad, but status.
        """
        responseBytes = bytearray()
        responseStr = ""
        receiving = True
        chunkRaw = b""
        try:
            while receiving:
                chunkRaw = client.recv(2048)
                if not chunkRaw:
                    break
                responseBytes.extend(chunkRaw)
                responseStr = responseBytes.decode("ASCII")
                if (
                    numberOfChunks == 0
                    and len(responseStr) == minBytes
                    or numberOfChunks != 0
                    and numberOfChunks == responseStr.count("#")
                ):
                    break

        except TimeoutError:
            if self.loggingTrace:
                self.log.debug(f"[Trace] Timeout  [{self.id}]: socket timeout in receive data")
            return False, []
        except Exception as e:
            self.log.warning(f"Error    [{self.id}]: error: [{e}], received: [{chunkRaw}]")
            return False, []
        else:
            response = responseStr.rstrip("#").split("#")
            if self.loggingTrace:
                self.log.debug(f"[Trace] Response [{self.id}]: [{response}]")
            return True, response

    def communicate(
        self, commandString: str, responseCheck: str = ""
    ) -> tuple[bool, list[str], int]:
        if not self.validCommandSet(commandString):
            return False, [], 0

        client = self.buildClient()
        numberOfChunks, getData, minBytes = self.analyseCommand(commandString)

        if client is None:
            return False, [], numberOfChunks
        if not self.sendData(client, commandString):
            return False, [], numberOfChunks
        if not getData:
            self.closeClientHard(client)
            return True, [], numberOfChunks

        suc, response = self.receiveData(client, numberOfChunks, minBytes)
        self.closeClientHard(client)

        if responseCheck:
            suc = suc and response[0] == responseCheck
        return suc, response, numberOfChunks

    def communicateRaw(self, commandString: str) -> tuple[bool, bool, str]:
        client = self.buildClient()
        if client is None:
            return False, False, "Socket error"

        sucSend = self.sendData(client, commandString)
        try:
            chunkRaw = client.recv(2048)
            val = chunkRaw.decode("ASCII")
        except TimeoutError:
            if self.loggingTrace:
                self.log.debug(
                    f"[Trace] Timeout  [{self.id}]: socket timeout in communicate raw"
                )
            val = "Timeout"
            sucRec = False
        except Exception as e:
            self.log.warning(
                f"[Trace] Error    [{self.id}]: socket error: [{e}] in communicate raw"
            )
            val = "Exception"
            sucRec = False
        else:
            if self.loggingTrace:
                self.log.debug(f"[Trace] Response [{self.id}]:  [{val}] in communicate raw")
            sucRec = True

        return sucSend, sucRec, val
