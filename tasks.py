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
from invoke import task
from PIL import Image
import glob
import time

#
# defining all necessary virtual client login for building over all platforms
#

# defining environment for ubuntu
clientUbuntu = 'astro-ubuntu.fritz.box'
userUbuntu = 'mw@' + clientUbuntu
workUbuntu = '/home/mw/test'
workUbuntuSCP = userUbuntu + ':/home/mw/test'

# same for windows1 with cmd.exe as shell
clientWindows = 'astro-windows.fritz.box'
uWin = 'mw@' + clientWindows
wWin = 'test'
wWinSCP = uWin + ':/Users/mw/test'

# same for macOS
clientMac = 'astro-mac-bigsur.fritz.box'
# clientMac = 'astro-mac-catalina.fritz.box'
# clientMac = 'astro-mac-mojave.fritz.box'
userMac = 'mw@' + clientMac
workMac = 'test'
workMacSCP = userMac + ':/Users/mw/test'


def runMWd(c, param):
    c.run(param)


def runMW(c, param):
    # c.run(param, echo=False, hide='out')
    c.run(param)


def printMW(param):
    print(param)


@task
def clean_mw(c):
    printMW('clean mountwizzard')
    runMW(c, 'rm -rf .pytest_cache')
    runMW(c, 'rm -rf mw4.egg-info')
    runMW(c, 'find ./mw4 | grep -E "(__pycache__)" | xargs rm -rf')


@task
def image_res(c):
    printMW('changing image resolution for docs to 150 dpi')
    files = glob.glob('./docs/**/*.png', recursive=True)
    for file in files:
        print(file)
        im = Image.open(file)
        im.save(file, dpi=(150, 150))


@task
def version_doc(c):
    printMW('changing the version number to setup.py')

    # getting version of desired package
    with open('setup.py', 'r') as setup:
        text = setup.readlines()

    for line in text:
        if line.strip().startswith('version'):
            _, number, _ = line.split("'")

    # reading configuration file
    with open('./docs/source/conf.py', 'r') as conf:
        text = conf.readlines()
    textNew = list()

    print(f'>{number}<')

    # replacing the version number
    for line in text:
        if line.startswith('version'):
            line = f"version = '{number}'\n"
        if line.startswith('release'):
            line = f"release = '{number}'\n"
        textNew.append(line)

    # writing configuration file
    with open('./docs/source/conf.py', 'w+') as conf:
        conf.writelines(textNew)


@task
def update_builtins(c):
    printMW('building resources')
    runMW(c, 'cp ./data/de421_23.bsp ./mw4/resource/data/de421_23.bsp')
    runMW(c, 'cp ./data/active.txt ./mw4/resource/data/active.txt')
    runMW(c, 'cp ./data/finals2000A.all ./mw4/resource/data/finals2000A.all')


@task
def build_resource(c):
    printMW('building resources')
    resourceDir = './mw4/resource/'
    runMW(c, f'pyrcc5 -o {resourceDir}resources.py {resourceDir}resources.qrc')


@task
def build_widgets(c):
    printMW('building widgets')
    widgetDir = './mw4/gui/widgets/'
    widgets = ['hemisphere', 'image', 'main', 'measure', 'message',
               'satellite', 'keypad', 'devicePopup', 'analyse',
               'simulator', 'downloadPopup']
    for widget in widgets:
        name = widgetDir + widget
        runMW(c, f'python -m PyQt5.uic.pyuic -x {name}.ui -o {name}_ui.py')


@task()
def test_mw(c):
    printMW('testing mountwizzard')
    runMW(c, 'flake8')
    runMW(c, 'pytest  tests/unit_tests/zLoader')
    runMW(c, 'pytest  tests/unit_tests/zMainApp')
    runMW(c, 'pytest tests/unit_tests/base')
    runMW(c, 'pytest tests/unit_tests/logic/astrometry')
    runMW(c, 'pytest tests/unit_tests/logic/cover')
    runMW(c, 'pytest tests/unit_tests/logic/databaseProcessing')
    runMW(c, 'pytest tests/unit_tests/logic/dome')
    runMW(c, 'pytest tests/unit_tests/logic/environment')
    runMW(c, 'pytest tests/unit_tests/logic/imaging')
    runMW(c, 'pytest tests/unit_tests/logic/measure')
    runMW(c, 'pytest tests/unit_tests/logic/modeldata')
    runMW(c, 'pytest tests/unit_tests/logic/powerswitch')
    runMW(c, 'pytest tests/unit_tests/logic/remote')
    runMW(c, 'pytest tests/unit_tests/logic/telescope')
    runMW(c, 'pytest tests/unit_tests/gui/extWindows')
    runMW(c, 'pytest tests/unit_tests/gui/mainWindow')
    runMW(c, 'pytest tests/unit_tests/gui/mainWmixin')
    runMW(c, 'pytest tests/unit_tests/gui/utilities')
    runMW(c, 'pytest tests/unit_tests/mountcontrol')
    runMW(c, 'pytest tests/unit_tests/indibase')
    runMW(c, 'pytest tests/unit_tests/logic/automation')


@task(pre=[build_resource, build_widgets, version_doc])
def build_mw(c):
    printMW('building dist mountwizzard4')
    with c.cd('.'):
        runMW(c, 'rm -f dist/mountwizzard4*.tar.gz')
        runMW(c, 'python setup.py sdist')
        runMW(c, 'cp dist/mountwizzard4*.tar.gz ../MountWizzard4/dist/mountwizzard4.tar.gz')


@task(pre=[build_mw])
def upload_mw(c):
    printMW('uploading dist mountwizzard4')
    with c.cd('./dist'):
        runMW(c, 'twine upload mountwizzard4-*.tar.gz -r pypi')


@task(pre=[])
def test_win(c):
    printMW('test windows install')
    printMW('...delete test dir')
    runMW(c, f'ssh {uWin} "if exist {wWin} rd /s /q {wWin}"')
    time.sleep(1)
    printMW('...make test dir')
    runMW(c, f'ssh {uWin} "if not exist {wWin} mkdir {wWin}"')
    time.sleep(1)

    with c.cd('dist'):
        printMW('...copy *.tar.gz to test dir')
        runMWd(c, f'scp -r mountwizzard4.tar.gz {wWinSCP}')

    with c.cd('support/Windows'):
        printMW('...copy install script to test dir')
        runMWd(c, f'scp -r MW4_InstallTest.bat {wWinSCP}')
        runMWd(c, f'scp -r MW4_Install.bat {wWinSCP}')
        printMW('...run install script in test dir')
        runMWd(c, f'ssh {uWin} "cd {wWin} && MW4_InstallTest.bat"')
        printMW('...copy run script to test dir')
        runMWd(c, f'scp -r test.txt {wWinSCP}')
        runMWd(c, f'scp -r MW4_Run.bat {wWinSCP}')
        printMW('...run MountWizzard4 for 3 seconds')
        runMWd(c, f'ssh {uWin} "cd {wWin} && MW4_Run.bat"')


@task(pre=[])
def test_ubuntu(c):
    printMW('test ubuntu install')
    printMW('...delete test dir')
    runMW(c, f'ssh {userUbuntu} "rm -rf {workUbuntu}"')
    time.sleep(1)
    printMW('...make test dir')
    runMW(c, f'ssh {userUbuntu} "mkdir {workUbuntu}"')
    time.sleep(1)

    with c.cd('dist'):
        printMW('...copy *.tar.gz to test dir')
        runMWd(c, f'scp -r mountwizzard4.tar.gz {workUbuntuSCP}')

    with c.cd('support/Ubuntu'):
        printMW('...copy install script to test dir')
        runMWd(c, f'scp -r MW4_InstallTest.sh {workUbuntuSCP}')
        runMWd(c, f'scp -r MW4_Install.sh {workUbuntuSCP}')
        printMW('...run install script in test dir')
        runMWd(c, f'ssh {userUbuntu} "cd {workUbuntu} && ./MW4_InstallTest.sh"')
        printMW('...copy run script and environ to test dir')
        runMWd(c, f'scp -r test.txt {workUbuntuSCP}')
        runMWd(c, f'scp -r MW4_Run.sh {workUbuntuSCP}')
        runMWd(c, f'scp -r MountWizzard4.desktop {workUbuntuSCP}')
        runMWd(c, f'scp -r mw4.png {workUbuntuSCP}')
        printMW('...run MountWizzard4 for 3 seconds')
        runMWd(c, f'ssh {userUbuntu} "cd {workUbuntu} && xvfb-run ./MW4_Run.sh"')


@task(pre=[])
def test_mac(c):
    printMW('test catalina install')
    printMW('...delete test dir')
    runMW(c, f'ssh {userMac} "rm -rf {workMac}"')
    time.sleep(1)
    printMW('...make test dir')
    runMW(c, f'ssh {userMac} "mkdir {workMac}"')
    time.sleep(1)

    with c.cd('dist'):
        printMW('...copy *.tar.gz to test dir')
        runMWd(c, f'scp -r mountwizzard4.tar.gz {workMacSCP}')

    with c.cd('support/MacOSx'):
        printMW('...copy install script to test dir')
        runMWd(c, f'scp -r MW4_InstallTest.command {workMacSCP}')
        runMWd(c, f'scp -r MW4_Install.command {workMacSCP}')
        printMW('...run install script in test dir')
        runMWd(c, f'ssh {userMac} "cd {workMac} && ./MW4_InstallTest.command"')
        printMW('...copy run script and environ to test dir')
        runMWd(c, f'scp -r test.txt {workMacSCP}')
        runMWd(c, f'scp -r MW4_Run.command {workMacSCP}')
        printMW('...run MountWizzard4 for 3 seconds')
        runMWd(c, f'ssh {userMac} "cd {workMac} && ./MW4_Run.command"')
