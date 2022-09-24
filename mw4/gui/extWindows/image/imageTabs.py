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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget

# local import


class ImageTabs:

    def showTabImage(self):
        """
        :return:
        """
        self.changeStyleDynamic(self.ui.headerGroup, 'running', False)
        tab = self.ui.tabImage
        tabIndex = tab.indexOf(tab.findChild(QWidget, 'Image'))
        tab.setTabEnabled(tabIndex, True)

        if self.fileHandler.image is None:
            self.msg.emit(0, 'Image', 'Rendering error', 'Incompatible image format')
            return False

        self.ui.groupMouseCoord.setVisible(self.fileHandler.hasCelestial)
        self.ui.slewCenter.setEnabled(self.fileHandler.hasCelestial)
        self.imageSourceRange = None
        self.ui.image.setImage(imageDisp=self.fileHandler.image)
        self.setBarColor()
        self.setCrosshair()
        self.writeHeaderDataToGUI(self.fileHandler.header)
        return True

    def showTabHFR(self):
        """
        :return:
        """
        self.ui.hfr.setImage(imageDisp=self.photometry.hfrGrid)
        self.ui.hfr.barItem.setLevels(
            (self.photometry.hfrMin, self.photometry.hfrMax))
        self.ui.hfrPercentile.setText(f'{self.photometry.hfrPercentile:1.1f}')
        self.ui.medianHFR.setText(f'{self.photometry.hfrMedian:1.2f}')
        self.ui.numberStars.setText(f'{len(self.photometry.hfr):1.0f}')
        if self.ui.isoLayer.isChecked():
            self.ui.hfr.addIsoBasic(self.ui.hfr.p[0], self.photometry.hfrGrid, levels=20)
        tab = self.ui.tabImage
        tab.setTabEnabled(tab.indexOf(tab.findChild(QWidget, 'HFR')), True)
        return True

    def showTabTiltSquare(self):
        """
        :return:
        """
        segHFR = self.photometry.hfrSegSquare
        w = self.photometry.w
        h = self.photometry.h
        plotItem = self.ui.tiltSquare.p[0]
        self.clearImageTab(self.ui.tiltSquare)
        self.ui.tiltSquare.setImage(self.photometry.image)
        self.ui.tiltSquare.barItem.setLevels(self.ui.image.barItem.levels())

        # draw lines on image
        for i in range(1, 3):
            posX = i * w / 3
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.pen)
            lineItem.setLine(posX, 0, posX, h)
            plotItem.addItem(lineItem)

            posY = i * h / 3
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.pen)
            lineItem.setLine(0, posY, w, posY)
            plotItem.addItem(lineItem)

        # write values in boxes
        for ix in range(3):
            for iy in range(3):
                text = f'{segHFR[ix][iy]:1.2f}'
                textItem = pg.TextItem(anchor=(0.5, 0.5), color=self.M_BLUE)
                textItem.setText(text)
                textItem.setFont(self.fontText)
                posX = ix * w / 3 + w / 6
                posY = iy * h / 3 + h / 6
                textItem.setPos(posX, posY)
                textItem.setZValue(10)
                plotItem.addItem(textItem)

        # calc extreme hfr values
        # arrays upper left to lower right
        w3 = w / 3
        h3 = h / 3
        corners = np.array([segHFR[0][2], segHFR[1][2], segHFR[2][2],
                            segHFR[0][1], segHFR[2][1],
                            segHFR[0][0], segHFR[1][0], segHFR[2][0]])
        vectors = np.array([[- w3, h3], [0, h3], [w3, h3],
                            [- w3, 0], [w3, 0],
                            [- w3, - h3], [0, - h3], [w3, - h3]])
        best = np.min(corners)
        worst = np.max(corners)

        # calc vectors
        points = []
        for vector, corner in zip(vectors, corners):
            points.append(vector * corner / worst + np.array([w / 2, h / 2]))

        # draw vectors
        links = [[0, 1], [1, 2], [2, 4], [4, 7], [7, 6], [6, 5], [5, 3], [3, 0],
                 [0, 7], [2, 5]]
        for link in links:
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.penPink)
            lineItem.setLine(points[link[0]][0], points[link[0]][1],
                             points[link[1]][0], points[link[1]][1])
            plotItem.addItem(lineItem)

        tiltDiff = worst - best
        tiltPercent = 100 * tiltDiff / self.photometry.hfrMedian
        for tiltHint in self.TILT:
            if tiltPercent < self.TILT[tiltHint]:
                break

        t = f'{tiltDiff:1.2f} ({tiltPercent:1.0f}%) {tiltHint}'
        self.ui.textSquareTiltHFR.setText(t)

        offAxisDiff = self.photometry.hfrOuter - segHFR[1][1]
        offAxisPercent = 100 * offAxisDiff / self.photometry.hfrMedian
        t = f'{offAxisDiff:1.2f} ({offAxisPercent:1.0f}%)'
        self.ui.textSquareTiltOffAxis.setText(t)
        self.ui.squareMedianHFR.setText(f'{self.photometry.hfrMedian:1.2f}')
        self.ui.squareNumberStars.setText(f'{len(self.photometry.hfr):1.0f}')
        tab = self.ui.tabImage
        tab.setTabEnabled(tab.indexOf(tab.findChild(QWidget, 'TiltSquare')), True)
        return True

    def showTabTiltTriangle(self):
        """
        :return:
        """
        segHFR = self.photometry.hfrSegTriangle
        w = self.photometry.w
        h = self.photometry.h
        r = min(h, w) / 2
        cx = w / 2
        cy = h / 2
        r25 = 0.25 * r
        r62 = 0.625 * r
        r95 = 0.95 * r

        plotItem = self.ui.tiltTriangle.p[0]
        self.clearImageTab(self.ui.tiltTriangle)
        self.ui.tiltTriangle.setImage(self.photometry.image)
        self.ui.tiltTriangle.barItem.setLevels(self.ui.image.barItem.levels())

        # draw rings on image
        for rad in [r, r25]:
            ellipseItem = pg.QtWidgets.QGraphicsEllipseItem()
            ellipseItem.setRect(cx - rad, cy - rad, 2 * rad, 2 * rad)
            ellipseItem.setPen(self.pen)
            plotItem.addItem(ellipseItem)

        # add inner value
        text = f'{self.photometry.hfrInner:1.2f}'
        textItem = pg.TextItem(anchor=(0.5, 0.5), color=self.M_BLUE)
        textItem.setText(text)
        textItem.setFont(self.fontText)
        textItem.setZValue(10)
        textItem.setPos(cx, cy)
        plotItem.addItem(textItem)

        # add ring values
        segData = np.array([0.0, 0.0, 0.0])
        vectors = np.array([[0, 0], [0, 0], [0, 0]])
        offsetTiltAngle = self.ui.offsetTiltAngle.value()

        for i, angle in enumerate(range(0, 360, 120)):
            angleSep = np.radians(angle + offsetTiltAngle + 210)
            angleText = np.radians(angle + offsetTiltAngle + 270)
            posX1 = cx + r25 * np.cos(angleSep)
            posX2 = cx + r * np.cos(angleSep)
            posY1 = cy + r25 * np.sin(angleSep)
            posY2 = cy + r * np.sin(angleSep)
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setLine(posX1, posY1, posX2, posY2)
            lineItem.setPen(self.pen)
            plotItem.addItem(lineItem)

            startIndexSeg = int((angle + offsetTiltAngle + 210) / 10)
            endIndexSeg = int((angle + offsetTiltAngle + 330) / 10)
            segData[i] = np.mean(segHFR[startIndexSeg:endIndexSeg])
            text = f'{segData[i]:1.2f}'
            textItem = pg.TextItem(anchor=(0.5, 0.5), color=self.M_BLUE)
            textItem.setFont(self.fontText)
            textItem.setZValue(10)
            textItem.setText(text)
            posX = cx + r62 * np.cos(angleText)
            posY = cy + r62 * np.sin(angleText)
            vectors[i][0] = r95 * np.cos(angleText)
            vectors[i][1] = r95 * np.sin(angleText)
            textItem.setPos(posX, posY)
            plotItem.addItem(textItem)

        best = np.min(segData)
        worst = np.max(segData)
        tiltDiff = worst - best
        tiltPercent = 100 * tiltDiff / self.photometry.hfrMedian

        # calc vectors
        points = [[cx, cy]]
        for vector, corner in zip(vectors, segData):
            points.append(vector * corner / worst + np.array([w / 2, h / 2]))

        # draw vectors
        links = [[0, 1], [0, 2], [0, 3], [1, 2], [2, 3], [3, 1]]
        for link in links:
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.penPink)
            lineItem.setLine(points[link[0]][0], points[link[0]][1],
                             points[link[1]][0], points[link[1]][1])
            plotItem.addItem(lineItem)

        for tiltHint in self.TILT:
            if tiltPercent < self.TILT[tiltHint]:
                break

        t = f'{tiltDiff:1.2f} ({tiltPercent:1.0f}%) {tiltHint}'
        self.ui.textTriangleTiltHFR.setText(t)

        offAxisDiff = self.photometry.hfrOuter - self.photometry.hfrInner
        offAxisPercent = 100 * offAxisDiff / self.photometry.hfrMedian
        t = f'{offAxisDiff:1.2f} ({offAxisPercent:1.0f}%)'
        self.ui.textTriangleTiltOffAxis.setText(t)
        self.ui.triangleMedianHFR.setText(f'{self.photometry.hfrMedian:1.2f}')
        self.ui.triangleNumberStars.setText(f'{len(self.photometry.hfr):1.0f}')
        tab = self.ui.tabImage
        tab.setTabEnabled(tab.indexOf(tab.findChild(QWidget, 'TiltTriangle')), True)
        return True

    def showTabRoundness(self):
        """
        :return:
        """
        self.ui.roundness.setImage(imageDisp=self.photometry.roundnessGrid)
        self.ui.roundness.p[0].showAxes(False, showValues=False)
        self.ui.roundness.p[0].setMouseEnabled(x=False, y=False)
        self.ui.roundness.barItem.setLevels(
            (self.photometry.roundnessMin, self.photometry.roundnessMax))
        self.ui.aspectRatioPercentile.setText(f'{self.photometry.roundnessPercentile:1.1f}')
        if self.ui.isoLayer.isChecked():
            self.ui.roundness.addIsoBasic(self.ui.roundness.p[0],
                                          self.photometry.roundnessGrid, levels=20)
        tab = self.ui.tabImage
        tab.setTabEnabled(tab.indexOf(tab.findChild(QWidget, 'Roundness')), True)
        return True

    def showTabAberrationInspect(self):
        """
        :return:
        """
        self.ui.aberration.barItem.setVisible(False)
        self.ui.aberration.p[0].clear()
        self.ui.aberration.p[0].setAspectLocked(True)
        self.ui.aberration.p[0].showAxes(False, showValues=False)
        self.ui.aberration.p[0].setMouseEnabled(x=False, y=False)
        self.ui.aberration.setImage(self.photometry.aberrationImage)
        for i in range(1, 3):
            posX = i * self.photometry.ABERRATION_SIZE
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.pen)
            lineItem.setLine(posX, 0, posX, 3 * self.photometry.ABERRATION_SIZE)
            self.ui.aberration.p[0].addItem(lineItem)

            posY = i * self.photometry.ABERRATION_SIZE
            lineItem = pg.QtWidgets.QGraphicsLineItem()
            lineItem.setPen(self.pen)
            lineItem.setLine(0, posY, 3 * self.photometry.ABERRATION_SIZE, posY)
            self.ui.aberration.p[0].addItem(lineItem)

        tab = self.ui.tabImage
        tab.setTabEnabled(tab.indexOf(tab.findChild(QWidget, 'Aberration')), True)
        self.ui.aberration.p[0].getViewBox().rightMouseRange()
        return True

    def showTabImageSources(self):
        """
        :return:
        """
        temp = self.imageSourceRange
        self.ui.imageSource.setImage(imageDisp=self.photometry.image)
        self.ui.imageSource.p[0].getViewBox().sigRangeChanged.connect(
            self.getImageSourceRange)
        if temp:
            self.ui.imageSource.p[0].getViewBox().setRange(
                rect=temp)

        objs = self.photometry.objs
        for i in range(len(objs)):
            eItem = self.ui.imageSource.addEllipse(
                objs['x'][i], objs['y'][i],
                objs['a'][i] * 4, objs['b'][i] * 4,
                objs['theta'][i])
            if self.ui.showValues.isChecked():
                t = f'{self.photometry.hfr[i]:2.1f}'
                item = pg.TextItem(text=t, color=self.M_BLUE, anchor=(1, 1))
                item.setFont(self.fontAnno)
                item.setParentItem(eItem)
        tab = self.ui.tabImage
        tab.setTabEnabled(tab.indexOf(tab.findChild(QWidget, 'Sources')), True)
        return True

    def showTabBackground(self):
        """
        :return:
        """
        self.ui.background.setImage(imageDisp=self.photometry.background)
        self.ui.background.barItem.setLevels(
            (self.photometry.backgroundMin, self.photometry.backgroundMax))
        tab = self.ui.tabImage
        tab.setTabEnabled(tab.indexOf(tab.findChild(QWidget, 'Back')), True)
        return True

    def showTabBackgroundRMS(self):
        """
        :return:
        """
        self.ui.backgroundRMS.setImage(imageDisp=self.photometry.backgroundRMS)
        tab = self.ui.tabImage
        tab.setTabEnabled(tab.indexOf(tab.findChild(QWidget, 'BackRMS')), True)
        return True
