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
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
from invoke import task


@task
def clean(c):
    print('clean')


@task
def resource(c):
    print('building resources')
    resourceDir = 'mw4/gui/media/'
    c.run(f'pyrcc5 -o {resourceDir}resources.py {resourceDir}resources.qrc')


@task
def widgets(c):
    print('building widgets')
    widgetDir = 'mw4/gui/widgets/'
    widgets = ['hemisphere', 'image', 'main', 'measure', 'message', 'satellite']
    for widget in widgets:
        name = widgetDir + widget
        c.run(f'python -m PyQt5.uic.pyuic -x {name}.ui -o {name}_ui.py')


@task(pre=[resource, widgets])
def test(c):
    print('testing')
    c.run('flake8')
    c.run('pytest mw4/test/test_units --cov-config .coveragerc --cov mw4/')


@task
def build(c):
    print('building dist')
    c.run('python setup.py sdist')
    print('')
    print('building mac')
    print('update mountcontrol')
    c.run('pip install ../mountcontrol/dist/mountcontrol-*.tar.gz')
    print('update indibase')
    c.run('pip install ../indibase/dist/indibase-*.tar.gz')
    print('pyinstaller')
    c.run('pyinstaller -y mw4_mac.spec')
    print('building dmg')
    c.run('hdiutil create dist/MountWizzard4.dmg -srcfolder dist/*.app -ov')


@task(pre=[test])
def clean_build(c):
    print('building dist')
    c.run('python setup.py sdist')
    print('')
    print('building mac')
    print('update mountcontrol')
    c.run('pip install ../mountcontrol/dist/mountcontrol-*.tar.gz')
    print('update indibase')
    c.run('pip install ../indibase/dist/indibase-*.tar.gz')
    print('pyinstaller')
    c.run('pyinstaller -y mw4_mac.spec')
    print('building dmg')
    c.run('hdiutil create dist/MountWizzard4.dmg -srcfolder dist/*.app -ov')


@task(pre=[build])
def deploy(c):
    print('deploy dist')
    print('deploy mac')
