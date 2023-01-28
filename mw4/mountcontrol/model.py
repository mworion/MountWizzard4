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
# Python  v3.7.4
#
# Michael Würtenberger
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
import skyfield.api

# local imports
from mountcontrol.connection import Connection
from mountcontrol.convert import valueToFloat
from mountcontrol.convert import valueToInt
from mountcontrol.convert import valueToAngle
from mountcontrol.convert import sexagesimalizeToInt
from mountcontrol.alignStar import AlignStar
from mountcontrol.modelStar import ModelStar


class Model(object):
    """
    The class Model inherits all information and handling of the actual
    alignment model used by the mount and the data, which models are stored
    in the mount and provides the abstracted interface to a 10 micron mount.

        >>> settings = Model(host='')

    """

    __all__ = ['Model']

    log = logging.getLogger(__name__)

    def __init__(self,
                 parent=None,
                 host=None,
                 ):

        self.host = host
        self.parent = parent
        self.numberNames = None
        self.numberStars = None
        self._starList = list()
        self._nameList = list()
        self._altitudeError = None
        self._azimuthError = None
        self._polarError = None
        self._positionAngle = None
        self._orthoError = None
        self._altitudeTurns = None
        self._azimuthTurns = None
        self._terms = None
        self._errorRMS = None

    @property
    def altitudeError(self):
        return self._altitudeError

    @altitudeError.setter
    def altitudeError(self, value):
        self._altitudeError = valueToAngle(value)

    @property
    def azimuthError(self):
        return self._azimuthError

    @azimuthError.setter
    def azimuthError(self, value):
        self._azimuthError = valueToAngle(value)

    @property
    def polarError(self):
        return self._polarError

    @polarError.setter
    def polarError(self, value):
        self._polarError = valueToAngle(value)

    @property
    def positionAngle(self):
        return self._positionAngle

    @positionAngle.setter
    def positionAngle(self, value):
        if isinstance(value, skyfield.api.Angle):
            self._positionAngle = value
            return
        self._positionAngle = valueToAngle(value)

    @property
    def orthoError(self):
        return self._orthoError

    @orthoError.setter
    def orthoError(self, value):
        self._orthoError = valueToAngle(value)

    @property
    def altitudeTurns(self):
        return self._altitudeTurns

    @altitudeTurns.setter
    def altitudeTurns(self, value):
        self._altitudeTurns = valueToFloat(value)

    @property
    def azimuthTurns(self):
        return self._azimuthTurns

    @azimuthTurns.setter
    def azimuthTurns(self, value):
        self._azimuthTurns = valueToFloat(value)

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, value):
        # qci mount don't deliver this value
        if value == '':
            self.log.warning('QCI mount does not provide terms')
        self._terms = valueToFloat(value)

    @property
    def errorRMS(self):
        return self._errorRMS

    @errorRMS.setter
    def errorRMS(self, value):
        if value == '':
            self.log.warning('QCI mount does not provide RMS')
            return
        self._errorRMS = valueToFloat(value)

    @property
    def starList(self):
        return self._starList

    @starList.setter
    def starList(self, value):
        if not isinstance(value, list):
            self._starList = list()
            return
        if all([isinstance(x, ModelStar) for x in value]):
            self._starList = value
        else:
            self._starList = list()

    @property
    def numberStars(self):
        return self._numberStars

    @numberStars.setter
    def numberStars(self, value):
        if value is None:
            self._numberStars = None
        else:
            self._numberStars = valueToInt(value)

    def addStar(self, value):
        """
        Adds a star to the list of stars. Type of name should be class AlignStar.

        :param      value:  name as type AlignStar
        :return:    nothing
        """

        if isinstance(value, ModelStar):
            self._starList.insert(len(self._starList), value)
            return
        if not isinstance(value, (list, str)):
            self.log.warning('malformed value: {0}'.format(value))
            return
        if isinstance(value, str):
            value = value.split(',')
        if len(value) == 5:
            ha, dec, err, angle, number = value
            value = ModelStar(coord=(ha, dec),
                              errorRMS=err,
                              errorAngle=angle,
                              number=number,
                              obsSite=self.parent.obsSite,
                              )
            self._starList.insert(len(self._starList), value)

    def delStar(self, value):
        """
        Deletes a name from the list of stars at position value. The numbering
        is from 0 to len -1 of list.

        :param value: position as int
        """

        value = valueToInt(value)
        if value < 0 or value > len(self._starList) - 1:
            self.log.warning('invalid value: {0}'.format(value))
            return
        self._starList.pop(value)

    def checkStarListOK(self):
        """
        Make a check if the actual alignment star count by polling gets the same
        number of stars compared to the number of stars in the list.
        Otherwise something was changed.

        :return: True if same size
        """

        if not self._numberStars:
            return False
        if self._numberStars == len(self._starList):
            return True
        else:
            return False

    @property
    def nameList(self):
        return self._nameList

    @nameList.setter
    def nameList(self, value):
        if not isinstance(value, list):
            self._nameList = list()
            return
        if all([isinstance(x, str) for x in value]):
            self._nameList = value
        else:
            self._nameList = list()

    @property
    def numberNames(self):
        return self._numberNames

    @numberNames.setter
    def numberNames(self, value):
        if value is None:
            self._numberNames = None
        else:
            self._numberNames = valueToInt(value)

    def addName(self, value):
        """
        Adds a name to the list of names. Type of name should be str.

        :param value: name as str
        :return: nothing
        """
        if not isinstance(value, str):
            self.log.warning('malformed value: {0}'.format(value))
            return
        self._nameList.insert(len(self._nameList), value)

    def delName(self, value):
        """
        Deletes a name from the list of names at position value. The numbering
        is from 0 to len -1 of list.

        :param value: position as int
        :return: nothing
        """
        value = valueToInt(value)
        if value < 0 or value > len(self._nameList) - 1:
            self.log.warning('invalid value: {0}'.format(value))
            return
        self._nameList.pop(value)

    def checkNameListOK(self):
        """
        Make a check if the actual model name count by polling gets the same
        number of names compared to the number of names in the list.
        Otherwise something was changed.

        :return: True if same size
        """
        if not self._numberNames:
            return False
        if self._numberNames == len(self._nameList):
            return True
        else:
            return False

    def parseNames(self, response, numberOfChunks):
        """
        Parsing the model names cluster. The command <:modelnamN#> returns:
            - the string "#" if N is not valid
            - the name of model N, terminated by the character "#"

        :param response:        data load from mount
        :param numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """
        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        for name in response:
            if not name:
                continue
            self.addName(name)
        return True

    def parseNumberNames(self, response, numberOfChunks):
        """
        Parsing the model star number. The command <:modelcnt#> returns:
            - the string "nnn#", where nnn is the number of models available

        :param response:        data load from mount
        :param numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """
        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        if len(response) != 1:
            self.log.warning('wrong number of chunks')
            return False
        self.numberNames = response[0]
        return True

    def getNameCount(self):
        """
        :return:
        """
        conn = Connection(self.host)
        commandString = ':modelcnt#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        suc = self.parseNumberNames(response, numberOfChunks)
        return suc

    def getNames(self):
        """
        :return:
        """
        conn = Connection(self.host)
        commandString = ''
        for i in range(1, self.numberNames + 1):
            commandString += (':modelnam{0:d}#'.format(i))

        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        self._nameList = list()
        suc = self.parseNames(response, numberOfChunks)
        return suc

    def pollNames(self):
        """
        Sending the polling ModelNames command. It collects for all the known
        names the string. The number of names have to be collected first, than it
        gathers all name at once.

        :return: success:   True if ok, False if not
        """
        suc = self.getNameCount()
        if suc:
            suc = self.getNames()
        return suc

    def parseStars(self, response, numberOfChunks):
        """
        Parsing the model names cluster. The command <:getalpN#> returns:
            - the string "E#" if N is out of range
            - otherwise a string formatted as follows
                "HH:MM:SS.SS,+dd*mm:ss.s,eeee.e,ppp#"
        where
        -   HH:MM:SS.SS is the hour angle of the alignment star in hours,
            minutes, seconds and hundredths of second (from 0h to 23h59m59.99s),
        -   +dd*mm:ss.s is the declination of the alignment star in degrees,
            arcminutes, arcseconds and tenths of arcsec, eeee.e is the error
            between the star and the alignment model in arcseconds,
        -   ppp is the polar angle of the measured star with respect to the
            modeled star in the equatorial system in degrees from 0 to 359 (0
            towards the north pole, 90 towards east)

        :param response:        data load from mount
        :param numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """
        if len(response) != numberOfChunks:
            self.log.warning('Wrong number of chunks')
            return False
        for number, starData in enumerate(response):
            if not starData:
                continue
            # mount counts stars from 1 beginning and adding the number (which
            # is not provided by the response, but counted in the mount computer
            # for reference reasons
            modelStar = '{0:s}, {1}'.format(starData, number + 1)
            self.addStar(modelStar)
        return True

    def parseNumberStars(self, response, numberOfChunks):
        """
        Parsing the model star number. The command <:getalst#> returns:
            - the number of alignment stars terminated by '#'

        :param response:        data load from mount
        :param numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """
        if len(response) != numberOfChunks or len(response) == 0:
            self.log.warning('Wrong number of chunks')
            return False

        self.numberStars = response[0]
        if numberOfChunks < 2:
            self.log.warning('Wrong number of chunks')
            return False

        responseSplit = response[1].split(',')
        # if there are less than 3 points, we get 'E' as result of getain
        if response[0] in ['0', '1', '2'] and response[1] == 'E':
            responseSplit = [None] * 9
        if len(responseSplit) != 9:
            self.log.warning('Wrong number of chunks in getain')
            return False

        self.azimuthError = responseSplit[0]
        self.altitudeError = responseSplit[1]
        self.polarError = responseSplit[2]
        self.positionAngle = responseSplit[3]
        self.orthoError = responseSplit[4]
        self.azimuthTurns = responseSplit[5]
        self.altitudeTurns = responseSplit[6]
        self.terms = responseSplit[7]
        self.errorRMS = responseSplit[8]

        return True

    def getStarCount(self):
        """
        :return:
        """
        conn = Connection(self.host)
        commandString = ':getalst#:getain#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        suc = self.parseNumberStars(response, numberOfChunks)
        return suc

    def getStars(self):
        """
        :return:
        """
        conn = Connection(self.host)
        self._starList = list()
        if self.numberStars == 0:
            return True

        commandString = ''
        for i in range(1, self.numberStars + 1):
            commandString += (':getalp{0:d}#'.format(i))
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        suc = self.parseStars(response, numberOfChunks)
        return suc

    def pollStars(self):
        """
        Sending the polling ModelNames command. It collects for all the known
        names the string. The number of names have to be collected first, than it
        gathers all name at once.

        :return:    success:    True if ok, False if not
        """
        suc = self.getStarCount()
        if suc:
            suc = self.getStars()
        return suc

    def pollCount(self):
        """
        pollSetting counts collects the data of number of alignment stars and
        number of model names and updates them in the model class

        :return:    success
        """
        conn = Connection(self.host)
        commandString = ':modelcnt#:getalst#'

        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if len(response) != numberOfChunks:
            self.log.warning('Wrong number of chunks')
            return False

        if len(response) != 2:
            self.log.warning('Wrong number of chunks')
            return False

        self.numberNames = response[0]
        self.numberStars = response[1]

        return True

    def clearAlign(self):
        """
        clear model sends the clear command to the mount and deletes the current
        alignment model and alignment stars

        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':delalig#')
        if not suc:
            return False
        if response[0] != '':
            return False

        return True

    def deletePoint(self, number):
        """
        deletePoint deletes the point with number from the actual alignment
        model. the model will be recalculated by the mount computer afterwards.
        number has to be an existing point in the database. the counting is
        from 1 to N.

        :param      number: number of point in int / float
        :return:    success
        """
        if isinstance(number, str):
            return False

        number = int(number)
        if number < 1 or number > self._numberStars:
            return False

        conn = Connection(self.host)
        commandString = ':delalst{0:d}#'.format(number)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if response[0] not in ['1']:
            return False

        return True

    def storeName(self, name):
        """
        storeName saves the actual alignment model to the database of the mount
        computer under the given name. the name is context sensitive and does
        contain maximum 15 characters.

        :param      name: name of model as string
        :return:    success
        """
        if not isinstance(name, str):
            return False
        if len(name) > 15:
            return False

        conn = Connection(self.host)
        commandString = ':modeldel0{0}#:modelsv0{1}#'.format(name, name)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if response[0] != '1':
            self.log.info('model >{0}< overwritten'.format(name))
        if response[1] != '1':
            return False

        return True

    def loadName(self, name):
        """
        loadName loads from the database of the mount computer the model under
        the given name as the actual alignment model . the name is context
        sensitive and does contain maximum 15 characters.

        :param      name: name of model as string
        :return:    success
        """
        if not isinstance(name, str):
            return False
        if len(name) > 15:
            return False

        conn = Connection(self.host)
        commandString = ':modelld0{0}#'.format(name)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if response[0] != '1':
            return False

        return True

    def deleteName(self, name):
        """
        deleteName deletes the model from the database of the mount computer under
        the given name. the name is context sensitive and does contain maximum 15
        characters.

        :param      name: name of model as string
        :return:    success
        """
        if not isinstance(name, str):
            return False
        if len(name) > 15:
            return False

        conn = Connection(self.host)
        commandString = ':modeldel0{0}#'.format(name)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if response[0] != '1':
            return False

        return True

    def programAlign(self, build):
        """
        programAlign builds a new alignment model in the mount computer by
        transferring the necessary data to the mount. the command is:

            :newalptMRA,MDEC,MSIDE,PRA,PDEC,SIDTIME#

        where the parameters are
            MRA     – the mount-reported right ascension, expressed as HH:MM:SS.S
            MDEC    – the mount-reported declination, expressed as sDD:MM:SS
            MSIDE   – the mount-reported pier side (the letter 'E' or 'W'),
                      as reported by the :pS# command)
            PRA     – the plate-solved right ascension (i.e. the right ascension
                      the telescope was effectively pointing to), expressed as
                      HH:MM:SS.S
            PDEC    – the plate-solved declination (i.e. the declination the
                      telescope was effectively pointing to), expressed
                      as sDD:MM:SS
            SIDTIME – the local sidereal time at the time of the measurement
                      of the point, expressed as HH:MM:SS.S derived from Angle in
                      hours
            Returns:
                the string "nnn#" if the point is valid, where nnn is the
                current number of points in the alignment specification
                (including this one) the string "E#" if the point is not valid

        :param      build: list of aPoint
        :return:    success
        """
        if not isinstance(build, list):
            return False

        if not all([isinstance(x, AlignStar) for x in build]):
            return False

        conn = Connection(self.host)
        commandString = ':newalig#'

        for aPoint in build:
            if not aPoint.sCoord or not aPoint.mCoord:
                continue
            sgn, h, m, s, frac = sexagesimalizeToInt(aPoint.mCoord.ra.hours, 1)
            ra = f'{h:02d}:{m:02d}:{s:02d}.{frac:1d}'

            sgn, h, m, s, frac = sexagesimalizeToInt(aPoint.mCoord.dec.degrees, 1)
            sign = '+' if sgn >= 0 else '-'
            dec = f'{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}'

            pierside = aPoint.pierside

            sgn, h, m, s, frac = sexagesimalizeToInt(aPoint.sCoord.ra.hours, 1)
            raSolve = f'{h:02d}:{m:02d}:{s:02d}.{frac:1d}'

            sgn, h, m, s, frac = sexagesimalizeToInt(aPoint.sCoord.dec.degrees, 1)
            sign = '+' if sgn >= 0 else '-'
            decSolve = f'{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}'

            sgn, h, m, s, frac = sexagesimalizeToInt(aPoint.sidereal.hours, 2)
            sidereal = f'{h:02d}:{m:02d}:{s:02d}.{frac:02d}'

            comFormat = ':newalpt{0},{1},{2},{3},{4},{5}#'
            value = comFormat.format(ra,
                                     dec,
                                     pierside,
                                     raSolve,
                                     decSolve,
                                     sidereal,
                                     )
            commandString += value

        commandString += ':endalig#'

        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if 'E' in response:
            return False

        return True
