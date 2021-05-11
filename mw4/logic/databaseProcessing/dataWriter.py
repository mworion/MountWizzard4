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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import shutil
import os

# external packages
from sgp4.exporter import export_tle

# local import


class DataWriter:
    """

    """
    __all__ = ['DataWriter',
               ]

    log = logging.getLogger(__name__)

    def __init__(self, app):
        super().__init__()
        self.app = app

    def writeEarthRotationData(self, installPath=''):
        """
        :param installPath:
        :return:
        """
        sourceDir = self.app.mwGlob['dataDir'] + '/'
        destDir = installPath + '/'

        if not os.path.isfile(sourceDir + 'CDFLeapSeconds.txt'):
            return False

        if not os.path.isfile(sourceDir + 'finals.data'):
            return False

        if destDir != sourceDir:
            shutil.copy(sourceDir + 'CDFLeapSeconds.txt', destDir + 'CDFLeapSeconds.txt')

        if destDir != sourceDir:
            shutil.copy(sourceDir + 'finals.data', destDir + 'finals.data')

        return True

    @staticmethod
    def writeCometMPC(datas=None, installPath=''):
        """
        data format of json and file description in
        https://minorplanetcenter.net/Extended_Files/Extended_MPCORB_Data_Format_Manual.pdf

        :param datas:
        :param installPath:
        :return:
        """
        if not datas:
            return False

        if not isinstance(datas, list):
            return False

        dest = installPath + '/minorPlanets.mpc'

        with open(dest, 'w') as f:
            for data in datas:
                line = ''
                line += f'{"":4s}'
                line += f'{data.get("Orbit_type", ""):1s}'
                line += f'{data.get("Provisional_packed_desig", ""):7s}'
                line += f'{"":2s}'
                line += f'{data.get("Year_of_perihelion", 0):04d}'
                line += f'{"":1s}'
                line += f'{data.get("Month_of_perihelion", 0):02d}'
                line += f'{"":1s}'
                line += f'{data.get("Day_of_perihelion", 0):7.4f}'
                line += f'{"":1s}'
                line += f'{data.get("Perihelion_dist", 0):9.6f}'
                line += f'{"":2s}'
                line += f'{data.get("e", 0):8.6f}'
                line += f'{"":2s}'
                line += f'{data.get("Peri", 0):8.4f}'
                line += f'{"":2s}'
                line += f'{data.get("Node", 0):8.4f}'
                line += f'{"":2s}'
                line += f'{data.get("i", 0):8.4f}'
                line += f'{"":2s}'

                if 'Epoch_year' in data:
                    line += f'{data.get("Epoch_year", 0):04d}'
                    line += f'{data.get("Epoch_month", 0):02d}'
                    line += f'{data.get("Epoch_day", 0):02d}'
                else:
                    line += f'{"":8s}'

                line += f'{"":2s}'
                line += f'{data.get("H", 0):4.1f}'
                line += f'{"":1s}'
                line += f'{data.get("G", 0):4.1f}'
                line += f'{"":2s}'
                line += f'{data.get("Designation_and_name", ""):56s}'
                line += f'{"":1s}'
                line += f'{data.get("Ref", " "):>9s}'
                line += '\n'
                f.write(line)

        return True

    @staticmethod
    def convertDatePacked(value):
        """
        conversion is described on
        https://www.minorplanetcenter.net/iau/info/PackedDates.html
        :param value:
        :return:
        """
        value = int(value)

        if 0 <= value < 10:
            resultChar = f'{value:1d}'

        elif 10 <= value < 36:
            resultChar = chr(ord('A') + value - 10)

        elif 36 <= value < 62:
            resultChar = chr(ord('a') + value - 36)

        else:
            resultChar = ' '

        return resultChar

    def generateCycleCountTextPacked(self, cycle):
        """
        :param cycle:
        :return:
        """
        digit1Value = cycle % 10
        digit2Value = int(cycle / 10)
        cycleChar1 = f'{digit1Value:1d}'
        cycleChar2 = self.convertDatePacked(digit2Value)
        cycleText = cycleChar2 + cycleChar1

        return cycleText

    @staticmethod
    def generateCenturyPacked(century):
        """

        :param century:
        :return:
        """
        centConvert = {'18': 'I',
                       '19': 'J',
                       '20': 'K',
                       '21': 'L'}

        centuryP = centConvert.get(century, ' ')

        return centuryP

    def generateDesignationPacked(self, designation):
        """
        description of conversion in
        https://minorplanetcenter.net//iau/info/PackedDes.html
        :param designation:
        :return:
        """
        if not designation:
            return 'xxxxxxx'

        designation = designation.strip()
        century = designation[0:2]
        centuryPacked = self.generateCenturyPacked(century)

        year = designation[2:4]
        halfMonth = designation[5]
        halfMonthOrder = designation[6]
        cycleText = designation[7:11]

        if cycleText and cycleText.isdigit():
            cycle = int(cycleText)

        else:
            cycle = 0

        cycleText = self.generateCycleCountTextPacked(cycle)

        designationPacked = f'{centuryPacked}{year}{halfMonth}{cycleText}{halfMonthOrder}'
        return designationPacked

    def generateDatePacked(self, month, day):
        """
        conversion is described on
        https://www.minorplanetcenter.net/iau/info/PackedDates.html
        :param month:
        :param day:
        :return:
        """
        dateChar1 = self.convertDatePacked(month)
        dateChar2 = self.convertDatePacked(day)

        dayPacked = dateChar1 + dateChar2
        return dayPacked

    def generateEpochPacked(self, epoch):
        """
        conversion is described on
        https://www.minorplanetcenter.net/iau/info/PackedDates.html
        :param epoch:
        :return:
        """
        if not epoch:
            return 'xxxxx'

        date = self.app.mount.obsSite.ts.tt_jd(int(epoch + 0.5))
        year, month, day = date.tt_strftime('%Y-%m-%d').split('-')
        century = year[0:2]
        centuryPacked = self.generateCenturyPacked(century)
        year = year[2:4]
        dayPacked = self.generateDatePacked(month, day)

        epochPackedText = f'{centuryPacked:1s}{year:2s}{dayPacked}'
        return epochPackedText

    def generateOldDesignationPacked(self, numberText):
        """
        :param numberText:
        :return:
        """
        if not numberText:
            return 'xxxxxxx'

        number = int(numberText.rstrip(')').lstrip('('))

        numberChar = self.convertDatePacked(number / 10000)
        designationPacked = f'{numberChar}{number % 10000:04d}  '

        return designationPacked

    def writeAsteroidMPC(self, datas=None, installPath=''):
        """
        data format of json and file description in
        https://minorplanetcenter.net/Extended_Files/Extended_MPCORB_Data_Format_Manual.pdf

        we have a mix of new and old style designation to manage. the old style seem to
        have the ley 'Number' in json, new style not.

        :param datas:
        :param installPath:
        :return:
        """
        if not datas:
            return False

        if not isinstance(datas, list):
            return False

        dest = installPath + '/minorPlanets.mpc'

        with open(dest, 'w') as f:
            for data in datas:
                line = ''

                if 'Number' in data:
                    numberText = data.get('Number', '')
                    designationPacked = self.generateOldDesignationPacked(numberText)

                else:
                    designation = data.get('Principal_desig', '')
                    designationPacked = self.generateDesignationPacked(designation)

                line += f'{designationPacked:7s}'
                line += f'{"":1s}'
                line += f'{data.get("H", 0):<5g}'
                line += f'{"":1s}'
                line += f'{data.get("G", 0):5g}'
                line += f'{"":1s}'

                epochPacked = self.generateEpochPacked(data.get('Epoch', 0))

                line += f'{epochPacked:5s}'
                line += f'{"":1s}'
                line += f'{data.get("M", 0):9.5f}'
                line += f'{"":2s}'
                line += f'{data.get("Peri", 0):9.5f}'
                line += f'{"":2s}'
                line += f'{data.get("Node", 0):9.5f}'
                line += f'{"":2s}'
                line += f'{data.get("i", 0):9.5f}'
                line += f'{"":2s}'
                line += f'{data.get("e", 0):9.7f}'
                line += f'{"":1s}'
                line += f'{data.get("n", 0):11.8f}'
                line += f'{"":1s}'
                line += f'{data.get("a", 0):11.7f}'
                line += f'{"":2s}'
                line += f'{data.get("U", ""):1s}'
                line += f'{"":1s}'
                line += f'{data.get("Ref", ""):9s}'
                line += f'{"":1s}'
                line += f'{data.get("Num_obs", 0):5.0f}'
                line += f'{"":1s}'
                line += f'{data.get("Num_opps", 0):3.0f}'

                line += f'{"":1s}'
                if 'Arc_years' in data:
                    line += f'{data.get("Arc_years",""):9s}'

                elif 'Arc_length' in data:
                    arcLength = data.get("Arc_length", 0)
                    line += f'{arcLength:4.0f} days'

                else:
                    line += f'{"":9s}'

                line += f'{"":1s}'
                line += f'{data.get("rms", 0):4.2f}'
                line += f'{"":1s}'
                line += f'{data.get("Perturbers", ""):3s}'
                line += f'{"":1s}'
                line += f'{data.get("Perturbers_2", ""):3s}'
                line += f'{"":1s}'
                line += f'{data.get("Computer", ""):10s}'
                line += f'{"":1s}'
                line += f'{data.get("Hex_flags", ""):4s}'
                line += f'{"":1s}'

                if 'Number' in data:
                    line += f'{data.get("Number", ""):>8s} {data.get("Name", ""):18s}'

                else:
                    line += f'{"":9s}'
                    line += f'{data.get("Principal_desig", ""):18s}'

                line += f'{"":1s}'
                line += f'{data.get("Last_obs", "").replace("-", ""):8s}'
                line += f'{"":1s}'
                line += f'{data.get("Tp", 0):13.5f}'
                line += '\n'
                f.write(line)

        return True

    @staticmethod
    def writeSatelliteTLE(datas=None, installPath=''):
        """
        data format of TLE and file description in

        :param datas:
        :param installPath:
        :return:
        """
        if not datas:
            return False

        if not isinstance(datas, dict):
            return False

        dest = installPath + '/satellites.tle'

        with open(dest, 'w') as f:
            for name in datas:
                line1, line2 = export_tle(datas[name].model)
                f.write(name + '\n')
                f.write(line1 + '\n')
                f.write(line2 + '\n')

        return True
