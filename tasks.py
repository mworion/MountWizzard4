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

global clientUbuntu, userUbuntu
clientUbuntu = 'astro-ubuntu.fritz.box'
userUbuntu = 'mw@' + clientUbuntu


@task
def clean(c):
    print('clean')
    c.run('rm -rf .pytest_cache')
    c.run('find ./mw4 | grep -E "(__pycache__)" | xargs rm -rf')


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


@task(pre=[clean, resource, widgets])
def test(c):
    print('testing')
    c.run('flake8')
    c.run('pytest mw4/test/test_units --cov-config .coveragerc --cov mw4/')


@task()
def build_dist(c):
    print('building dist')
    c.run('rm -f dist/*.tar.gz')
    c.run('python setup.py sdist')


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


@task()
def prepare_linux(c):
    print('preparing linux')
    c.run(f'ssh -t {userUbuntu} "bash -s" < setup_linux.sh')


@task(pre=[prepare_linux])
def deploy_ubuntu(c):
    print('deploy ubuntu')
    c.run(f'scp ../mountcontrol/dist/mountcontrol-*.tar.gz {userUbuntu}:/home/mw/mountwizzard4')
    c.run(f'scp ../indibase/dist/indibase-*.tar.gz {userUbuntu}:/home/mw/mountwizzard4')
    c.run(f'scp dist/mw4-*.tar.gz {userUbuntu}:/home/mw/mountwizzard4')
    c.run(f'ssh {userUbuntu} "bash -s" < mount_install.sh')
