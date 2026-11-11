# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
import uuid
from mw4.mountcontrol import timing
from mw4.mountcontrol.mountContext import MountContext
from mw4.mountcontrol.mountLink import BULK, INTERACTIVE, getWorker
from PySide6.QtCore import SignalInstance


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
                ":SUDT",
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
    COMMAND_P: frozenset[str] = frozenset({":RC", ":Rc", ":RG", ":Suaf"})

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
                ":SUDT",
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

    def __init__(self, parent: MountContext) -> None:
        self.parent = parent
        self.host = (parent.config.hostAddress, parent.config.port)
        self.loggingTrace = parent.loggingTrace
        self.id = str(uuid.uuid4())[:8]

    def validCommand(self, command: str) -> bool:
        return any(command.startswith(key) for key in self.COMMANDS)

    def validCommandSet(self, commandString: str) -> bool:
        commandSet = commandString.split("#")[:-1]
        for command in commandSet:
            if not self.validCommand(command):
                self.log.warning("[%s] unknown commands: %s", self.id, commandString)
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

    def linkReady(self) -> bool:
        if not self.host:
            self.log.info("No host  [%s]", self.id)
            return False
        if not isinstance(self.host, tuple) or len(self.host) != 2:
            self.log.info("Host     [%s]: host entry malformed [%s]", self.id, self.host)
            return False
        if self.host[0] is None or self.host[1] is None:
            self.log.info("Host     [%s]: host entry malformed [%s]", self.id, self.host)
            return False
        return bool(self.parent.mountIsUp)

    def communicate(
        self,
        commandString: str,
        responseCheck: str = "",
        priority: int = INTERACTIVE,
        deadline: float = timing.COMMAND_DEADLINE_S,
    ) -> tuple[bool, list[str], int]:
        if not self.validCommandSet(commandString):
            return False, [], 0
        numberOfChunks, getData, _ = self.analyseCommand(commandString)
        if not self.linkReady():
            return False, [], numberOfChunks

        worker = getWorker(*self.host)
        suc, response, _ = worker.submit("std", commandString, deadline, priority)
        if not suc:
            return False, [], numberOfChunks
        if not getData:
            return True, [], numberOfChunks
        if responseCheck:
            suc = suc and bool(response) and response[0] == responseCheck
        return suc, response, numberOfChunks

    def communicateBulk(
        self, commandString: str, progress: SignalInstance | None = None
    ) -> tuple[bool, list[str], int]:
        if not self.validCommandSet(commandString):
            return False, [], 0
        numberOfChunks = self.analyseCommand(commandString)[0]
        if not self.linkReady():
            return False, [], numberOfChunks
        count = commandString.count("#")
        deadline = max(timing.BATCH_DEADLINE_S, count * timing.BULK_DEADLINE_PER_COMMAND_S)
        worker = getWorker(*self.host)
        suc, response, _ = worker.submit("bulk", commandString, deadline, BULK, progress)
        return suc, response, numberOfChunks

    def communicateRaw(self, commandString: str) -> tuple[bool, bool, str]:
        if not self.linkReady():
            return False, False, "Socket error"
        worker = getWorker(*self.host)
        return worker.submit("raw", commandString, timing.COMMAND_DEADLINE_S, INTERACTIVE)
