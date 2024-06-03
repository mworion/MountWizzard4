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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PySide6.QtGui import QColor
from PySide6.Qt3DRender import Qt3DRender
from PySide6.Qt3DExtras import Qt3DExtras

# local import
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets import material_ui
from gui.extWindows.simulator.tools import getLight, getMaterial


class MaterialWindow(MWidget):
    """
    """
    __all__ = ['MaterialWindow']

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = material_ui.Ui_MaterialDialog()
        self.ui.setupUi(self)
        self.pointLight = None
        self.directionalLight = None
        self.spotLight = None
        self.materialType = None

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'materialW' not in self.app.config:
            self.app.config['materialW'] = {}
        config = self.app.config['materialW']

        self.positionWindow(config)
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config
        if 'materialW' not in config:
            config['materialW'] = {}
        else:
            config['materialW'].clear()
        config = config['materialW']

        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        """
        self.ui.mr0.sliderMoved.connect(self.setMaterial)
        self.ui.mg0.sliderMoved.connect(self.setMaterial)
        self.ui.mb0.sliderMoved.connect(self.setMaterial)
        self.ui.mr1.sliderMoved.connect(self.setMaterial)
        self.ui.mg1.sliderMoved.connect(self.setMaterial)
        self.ui.mb1.sliderMoved.connect(self.setMaterial)
        self.ui.mr2.sliderMoved.connect(self.setMaterial)
        self.ui.mg2.sliderMoved.connect(self.setMaterial)
        self.ui.mb2.sliderMoved.connect(self.setMaterial)
        self.ui.ms0.sliderMoved.connect(self.setMaterial)
        self.ui.ms1.sliderMoved.connect(self.setMaterial)

        self.ui.t4_sr.sliderMoved.connect(self.setPointLight)
        self.ui.t4_sg.sliderMoved.connect(self.setPointLight)
        self.ui.t4_sb.sliderMoved.connect(self.setPointLight)
        self.ui.t4_s0.sliderMoved.connect(self.setPointLight)
        self.ui.t4_s1.sliderMoved.connect(self.setPointLight)
        self.ui.t4_s2.sliderMoved.connect(self.setPointLight)
        self.ui.t4_s3.sliderMoved.connect(self.setPointLight)
        self.app.material.connect(self.getValues)
        self.show()

    def getPointLight(self, component):
        self.pointLight = component
        intensity = int(component.intensity() * 1000)
        constant = int(component.constantAttenuation() * 1000)
        linear = int(component.linearAttenuation() * 1000)
        quadratic = int(component.quadraticAttenuation() * 1000)
        self.ui.t4_s0.setValue(intensity)
        self.ui.t4_s1.setValue(constant)
        self.ui.t4_s2.setValue(linear)
        self.ui.t4_s3.setValue(quadratic)
        color = component.color()
        self.ui.t4_sr.setValue(color.red())
        self.ui.t4_sg.setValue(color.green())
        self.ui.t4_sb.setValue(color.blue())

    def getDirectionalLight(self, component):
        self.directionalLight = component
        pass

    def getSpotLight(self, component):
        self.spotLight = component
        pass

    def getMetalRoughMaterial(self, component, name):
        self.materialType = component
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.name.setText(name)
        self.ui.material.setText('MetalRough')
        self.ui.lr0.setText('R Base')
        self.ui.lg0.setText('G Base')
        self.ui.lb0.setText('B Base')
        self.ui.lr1.setText('--empty--')
        self.ui.lg1.setText('--empty--')
        self.ui.lb1.setText('--empty--')
        self.ui.lr2.setText('--empty--')
        self.ui.lg2.setText('--empty--')
        self.ui.lb2.setText('--empty--')
        self.ui.l0.setText('Metalness')
        self.ui.l1.setText('Roughness')

        color = component.baseColor()
        self.ui.mr0.setValue(color.red())
        self.ui.mg0.setValue(color.green())
        self.ui.mb0.setValue(color.blue())

        metalness = int(component.metalness() * 1000)
        roughness = int(component.roughness() * 1000)
        self.ui.ms0.setValue(metalness)
        self.ui.ms1.setValue(roughness)
        self.setMaterial()

    def getDiffuseSpecularMaterial(self, component, name):
        self.materialType = component
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.name.setText(name)
        self.ui.material.setText('DiffuseSpecular')
        self.ui.lr0.setText('R Ambient')
        self.ui.lg0.setText('G Ambient')
        self.ui.lb0.setText('B Ambient')
        self.ui.lr1.setText('R Diffuse')
        self.ui.lg1.setText('G Diffuse')
        self.ui.lb1.setText('B Diffuse')
        self.ui.lr2.setText('R Specular')
        self.ui.lg2.setText('G Specular')
        self.ui.lb2.setText('B Specular')
        self.ui.l0.setText('Shininess')

        self.ui.mr0.setValue(component.ambient().red())
        self.ui.mg0.setValue(component.ambient().green())
        self.ui.mb0.setValue(component.ambient().blue())
        self.ui.mr1.setValue(component.diffuse().red())
        self.ui.mg1.setValue(component.diffuse().green())
        self.ui.mb1.setValue(component.diffuse().blue())
        self.ui.mr2.setValue(component.specular().red())
        self.ui.mg2.setValue(component.specular().green())
        self.ui.mb2.setValue(component.specular().blue())
        self.ui.ms0.setValue(int(component.shininess()))
        self.setMaterial()

    def getValues(self, entity, name):
        if isinstance(getLight(entity), Qt3DRender.QPointLight):
            self.getPointLight(getLight(entity))
        elif isinstance(getLight(entity), Qt3DRender.QDirectionalLight):
            self.getDirectionalLight(getLight(entity))
        elif isinstance(getLight(entity), Qt3DRender.QSpotLight):
            self.getSpotLight(getLight(entity))
        elif isinstance(getMaterial(entity), Qt3DExtras.QMetalRoughMaterial):
            self.getMetalRoughMaterial(getMaterial(entity), name)
        elif isinstance(getMaterial(entity), Qt3DExtras.QDiffuseSpecularMaterial):
            self.getDiffuseSpecularMaterial(getMaterial(entity), name)

    def setPointLight(self):
        self.ui.t4_r.setText(f'{self.ui.t4_sr.value():03d}')
        self.ui.t4_g.setText(f'{self.ui.t4_sg.value():03d}')
        self.ui.t4_b.setText(f'{self.ui.t4_sb.value():03d}')
        self.ui.t4_0.setText(f'{self.ui.t4_s0.value() / 1000:1.3f}')
        self.ui.t4_1.setText(f'{self.ui.t4_s1.value() / 1000:1.3f}')
        self.ui.t4_2.setText(f'{self.ui.t4_s2.value() / 1000:1.3f}')
        self.ui.t4_3.setText(f'{self.ui.t4_s3.value() / 1000:1.3f}')
        color = QColor(self.ui.t4_sr.value(),
                       self.ui.t4_sg.value(),
                       self.ui.t4_sb.value())
        self.pointLight.setColor(color)
        self.pointLight.setIntensity(self.ui.t4_s0.value() / 1000)
        self.pointLight.setConstantAttenuation(self.ui.t4_s1.value() / 1000)
        self.pointLight.setLinearAttenuation(self.ui.t4_s2.value() / 1000)
        self.pointLight.setQuadraticAttenuation(self.ui.t4_s3.value() / 1000)

    def setMaterial(self):
        if isinstance(self.materialType, Qt3DExtras.QMetalRoughMaterial):
            self.ui.mtr0.setText(f'{self.ui.mr0.value():03d}')
            self.ui.mtg0.setText(f'{self.ui.mg0.value():03d}')
            self.ui.mtb0.setText(f'{self.ui.mb0.value():03d}')
            color = QColor(self.ui.mr0.value(),
                           self.ui.mg0.value(),
                           self.ui.mb0.value())
            self.materialType.setBaseColor(color)
            self.ui.mt0.setText(f'{self.ui.ms0.value() / 1000:1.3f}')
            self.materialType.setMetalness(self.ui.ms0.value() / 1000)
            self.ui.mt1.setText(f'{self.ui.ms1.value() / 1000:1.3f}')
            self.materialType.setRoughness(self.ui.ms1.value() / 1000)

        elif isinstance(self.materialType, Qt3DExtras.QDiffuseSpecularMaterial):
            self.ui.mtr0.setText(f'{self.ui.mr0.value():03d}')
            self.ui.mtg0.setText(f'{self.ui.mg0.value():03d}')
            self.ui.mtb0.setText(f'{self.ui.mb0.value():03d}')
            color = QColor(self.ui.mr0.value(),
                           self.ui.mg0.value(),
                           self.ui.mb0.value())
            self.materialType.setAmbient(color)

            self.ui.mtr1.setText(f'{self.ui.mr1.value():03d}')
            self.ui.mtg1.setText(f'{self.ui.mg1.value():03d}')
            self.ui.mtb1.setText(f'{self.ui.mb1.value():03d}')
            color = QColor(self.ui.mr1.value(),
                           self.ui.mg1.value(),
                           self.ui.mb1.value())
            self.materialType.setDiffuse(color)

            self.ui.mtr2.setText(f'{self.ui.mr2.value():03d}')
            self.ui.mtg2.setText(f'{self.ui.mg2.value():03d}')
            self.ui.mtb2.setText(f'{self.ui.mb2.value():03d}')
            color = QColor(self.ui.mr2.value(),
                           self.ui.mg2.value(),
                           self.ui.mb2.value())
            self.materialType.setSpecular(color)

            self.ui.mt0.setText(f'{self.ui.ms0.value():03d}')
            self.materialType.setShininess(self.ui.ms0.value())
