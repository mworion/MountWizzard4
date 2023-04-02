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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import requests

# external packages
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem

# local import
from logic.databaseProcessing.dataWriter import DataWriter


class MinorPlanet:
    """
    """

    def __init__(self):
        self.installPath = ''
        self.databaseProcessing = DataWriter(self.app)
        self.minorPlanets = {}
        self.listMinorPlanetNamesProxy = None

        self.mpcUrl = 'https://minorplanetcenter.net/web_service/search_orbits'
        self.tableForm = [
            {'parameter': 'name',
             'header': 'Name',
             'width': 100,
             'format': '40s'},
            {'parameter': 'number',
             'header': 'Number',
             'width': 80,
             'format': '15s'},
            {'parameter': 'epoch',
             'header': 'Epoch',
             'width': 100,
             'format': '40s'},
            {'parameter': 'period',
             'header': 'Period\n[years]',
             'width': 60,
             'format': '10s'},
            {'parameter': 'eccentricity',
             'header': 'Eccent\n[0..1]',
             'width': 80,
             'format': '30s'},
            {'parameter': 'mean_anomaly',
             'header': 'Mean\nAnomaly',
             'width': 80,
             'format': '30s'},
        ]

        self.ui.progMinorPlanetsSelected.clicked.connect(self.progMinorPlanetsSelected)
        self.ui.progMinorPlanetsFull.clicked.connect(self.progMinorPlanetsFull)
        self.ui.mpcName.editingFinished.connect(self.fetchMinorPlanets)
        # self.ui.isOnline.stateChanged.connect(self.loadMPCDataFromSourceURLs)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to
        the gui elements. if some initialisations have to be proceeded with the
        loaded persistent data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        if not self.app.automation:
            self.installPath = self.app.mwGlob['dataDir']
        elif self.app.automation.installPath:
            self.installPath = self.app.automation.installPath
        else:
            self.installPath = self.app.mwGlob['dataDir']
        self.prepareMPCTable()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        return True

    def progMinorPlanets(self, mpc):
        """
        :param mpc:
        :return:
        """
        isComet = self.ui.minorPlanetSource.currentText().startswith('Comet')
        if isComet:
            suc = self.databaseProcessing.writeCometMPC(mpc, self.installPath)
        else:
            suc = self.databaseProcessing.writeAsteroidMPC(mpc, self.installPath)

        if not suc:
            self.msg.emit(2, 'MPC', 'Data',
                          'Data could not be exported - stopping')
            return False

        self.msg.emit(0, 'MPC', 'Program', 'Uploading to mount')
        suc = self.app.automation.uploadMPCData(comets=isComet)
        if not suc:
            self.msg.emit(2, 'MPC', 'Program error',
                          'Uploading error but files available')
        else:
            self.msg.emit(1, 'MPC', 'Program', 'Successful uploaded')
        return suc

    def prepareMPCTable(self):
        """
        :return:
        """

        mpcTab = self.ui.listMPCNames
        mpcTab.setRowCount(0)
        mpcTab.setColumnCount(len(self.tableForm))
        headerLabels = [x['header'] for x in self.tableForm]
        mpcTab.setHorizontalHeaderLabels(headerLabels)
        for i, header in enumerate(self.tableForm):
            mpcTab.setColumnWidth(i, header['width'])
        mpcTab.verticalHeader().setDefaultSectionSize(16)
        return True

    def mpcSearch(self, params):
        """
        :return:
        """
        params['json'] = '1'
        params['limit'] = '20'
        params['order_by'] = 'name'
        data = requests.get(self.mpcUrl, params,
                            auth=('mpc_ws', 'mpc!!ws'), timeout=30)
        return data.json()

    def fillMPCTable(self, data):
        """
        :param data:
        :return:
        """
        self.prepareMPCTable()
        for i, dataPoint in enumerate(data):
            self.ui.listMPCNames.insertRow(i)
            for j, val in enumerate(self.tableForm):
                entry = QTableWidgetItem(str(dataPoint[val['parameter']]))
                entry.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.ui.listMPCNames.setItem(i, j, entry)
            print()

        return True

    def fetchMinorPlanets(self):
        """
        :return:
        """
        self.msg.emit(0, 'MPC', 'Fetch', 'Fetching data from MPC')
        params = {'name_min': self.ui.mpcName.text(),
                  }
        data = self.mpcSearch(params)
        self.fillMPCTable(data)
        self.msg.emit(0, 'MPC', 'Fetch', 'Data fetched')
        return True

    def mpcGUI(self):
        """
        :return:
        """
        source = self.ui.minorPlanetSource.currentText()
        suc = self.checkUpdaterOK()
        if not suc:
            return False

        question = '<b>Filtered MPC Data programming</b>'
        question += '<br><br>The 10micron updater will be used.'
        question += '<br>Selected source: '
        question += f'<font color={self.M_BLUE}>{source}</font>'
        question += '<br>Would you like to start?<br>'
        question += f'<br><i><font color={self.M_YELLOW}>'
        question += 'Please wait until updater is closed!</font></i>'
        suc = self.messageDialog(self, 'Program with 10micron Updater', question)
        if not suc:
            return False

        self.msg.emit(1, 'MPC', 'Program', f'{source}')
        self.msg.emit(1, '', '', 'Exporting MPC data')
        return True

    def progMinorPlanetsSelected(self):
        """
        :return: success
        """
        suc = self.mpcGUI()
        if not suc:
            return False

        mpcSelectedIndexes = self.ui.listMinorPlanetNames.selectedIndexes()
        mpcSelected = []
        for entry in mpcSelectedIndexes:
            index = entry.row()
            mpcSelected.append(self.minorPlanets[index])
        self.progMinorPlanets(mpcSelected)
        return True

    def progMinorPlanetsFull(self):
        """
        :return: success
        """
        suc = self.mpcGUI()
        if not suc:
            return False

        self.progMinorPlanets(self.minorPlanets)
        return True
