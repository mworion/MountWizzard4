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
from invoke import task
from PIL import Image
import glob
import time
import os

rn = ''
#
# defining all necessary virtual client login for building over all platforms
#

client = {
    'ubuntu': {
        'user': 'mw@astro-ubuntu.fritz.box',
        'work': '/home/mw/test',
        'scp': 'mw@astro-ubuntu.fritz.box:/home/mw/test',
    },
    'ubuntuRig': {
        'user': 'mw@astro-comp.fritz.box',
        'work': '/home/mw/test',
        'scp': 'mw@astro-comp.fritz.box:/home/mw/test',
    },
    'win10-32-old': {
        'user': 'mw@astro-win10-32-old.fritz.box',
        'work': 'test',
        'scp': 'mw@astro-win10-32-old.fritz.box:/Users/mw/test',
    },
    'win10-64-old': {
        'user': 'mw@astro-win10-64-old.fritz.box',
        'work': 'test',
        'scp': 'mw@astro-win10-64-old.fritz.box:/Users/mw/test',
    },
    'win10-32': {
        'user': 'mw@astro-win10-32.fritz.box',
        'work': 'test',
        'scp': 'mw@astro-win10-32.fritz.box:/Users/mw/test',
    },
    'win10-64': {
        'user': 'mw@astro-win10-64.fritz.box',
        'work': 'test',
        'scp': 'mw@astro-win10-64.fritz.box:/Users/mw/test',
    },
    'win11': {
        'user': 'mw@astro-win11.fritz.box',
        'work': 'test',
        'scp': 'mw@astro-win11.fritz.box:/Users/mw/test',
    },
    'macMojave': {
        'user': 'mw@astro-mac-mojave.fritz.box',
        'work': 'test',
        'scp': 'mw@astro-mac-mojave.fritz.box:/Users/mw/test',
    },
    'macCatalina': {
        'user': 'mw@astro-mac-catalina.fritz.box',
        'work': 'test',
        'scp': 'mw@astro-mac-catalina.fritz.box:/Users/mw/test',
    },
    'macBigsur': {
        'user': 'mw@astro-mac-bigsur.fritz.box',
        'work': 'test',
        'scp': 'mw@astro-mac-bigsur.fritz.box:/Users/mw/test',
    },
    'macMonterey': {
        'user': 'mw@astro-mac-monterey.fritz.box',
        'work': 'test',
        'scp': 'mw@astro-mac-monterey.fritz.box:/Users/mw/test',
    },
}


def runMW(c, param):
    c.run(param)


def printMW(param):
    print(param)


@task
def log(c):
    runMW(c, 'python3 logViewer.py')


@task
def clean_mw(c):
    printMW('clean mountwizzard')
    runMW(c, 'rm -rf .pytest_cache')
    runMW(c, 'rm -rf mw4.egg-info')
    runMW(c, 'find ./mw4 | grep -E "(__pycache__)" | xargs rm -rf')
    printMW('clean mountwizzard finished\n')


@task
def image_res(c):
    printMW('changing image resolution for docs to 150 dpi')
    files = glob.glob('./docs/source/**/*.png', recursive=True)
    for file in files:
        print(file)
        im = Image.open(file)
        im.save(file, dpi=(150, 150))
    printMW('changing image resolution for docs to 150 dpi finished\n')


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

    print(f'version is >{number}<')

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
    printMW('changing the version number to setup.py finished\n')


@task
def update_builtins(c):
    printMW('updating builtins')
    runMW(c, 'cp ./data/de421_23.bsp ./mw4/resource/data/de421_23.bsp')
    runMW(c, 'cp ./data/visual.txt ./mw4/resource/data/visual.txt')
    runMW(c, 'cp ./data/finals2000A.all ./mw4/resource/data/finals2000A.all')
    runMW(c, 'cp ./data/finals.data ./mw4/resource/data/finals.data')
    runMW(c, 'cp ./data/CDFLeapSeconds.txt ./mw4/resource/data/CDFLeapSeconds.txt')
    printMW('updating builtins finished\n')


@task
def build_resource(c):
    printMW('building resources')
    resourceDir = './mw4/resource/'
    with c.cd(resourceDir + 'data'):
        with open(resourceDir + 'data/content.txt', 'w') as f:
            for file in glob.glob(resourceDir + 'data/*.*'):
                t = os.stat(file).st_mtime
                f.write(f'{os.path.basename(file)} {t}\n')
    runMW(c, f'pyrcc5 -o {resourceDir}resources.py {resourceDir}resources.qrc')
    printMW('building resources finished\n')


@task
def build_widgets(c):
    printMW('building widgets')
    widgetDir = './mw4/gui/widgets/'
    widgets = [
        'analyse', 'devicePopup', 'downloadPopup', 'hemisphere', 'image',
        'keypad', 'main', 'measure', 'message', 'satellite', 'simulator'
    ]
    for widget in widgets:
        name = widgetDir + widget
        runMW(c, f'python -m PyQt5.uic.pyuic -x {name}.ui -o {name}_ui.py')
    printMW('building widgets finished\n')


@task()
def test_mw(c):
    printMW('testing mountwizzard')
    runMW(c, 'flake8')
    runMW(c, 'pytest  tests/unit_tests/zLoader')
    runMW(c, 'pytest  tests/unit_tests/zMainApp')
    runMW(c, 'pytest  tests/unit_tests/zUpdate')
    runMW(c, 'pytest tests/unit_tests/base')
    runMW(c, 'pytest tests/unit_tests/gui/extWindows')
    runMW(c, 'pytest tests/unit_tests/gui/mainWindow')
    runMW(c, 'pytest tests/unit_tests/gui/mainWmixin1')
    runMW(c, 'pytest tests/unit_tests/gui/mainWmixin2')
    runMW(c, 'pytest tests/unit_tests/gui/mainWmixin3')
    runMW(c, 'pytest tests/unit_tests/gui/utilities')
    runMW(c, 'pytest tests/unit_tests/indibase')
    runMW(c, 'pytest tests/unit_tests/logic/astrometry')
    runMW(c, 'pytest tests/unit_tests/logic/automation')
    runMW(c, 'pytest tests/unit_tests/logic/camera')
    runMW(c, 'pytest tests/unit_tests/logic/cover')
    runMW(c, 'pytest tests/unit_tests/logic/databaseProcessing')
    runMW(c, 'pytest tests/unit_tests/logic/dome')
    runMW(c, 'pytest tests/unit_tests/logic/environment')
    runMW(c, 'pytest tests/unit_tests/logic/filter')
    runMW(c, 'pytest tests/unit_tests/logic/focuser')
    runMW(c, 'pytest tests/unit_tests/logic/keypad')
    runMW(c, 'pytest tests/unit_tests/logic/measure')
    runMW(c, 'pytest tests/unit_tests/logic/modeldata')
    runMW(c, 'pytest tests/unit_tests/logic/powerswitch')
    runMW(c, 'pytest tests/unit_tests/logic/remote')
    runMW(c, 'pytest tests/unit_tests/logic/telescope')
    runMW(c, 'pytest tests/unit_tests/mountcontrol')
    printMW('testing mountwizzard finished\n')


@task(pre=[build_resource, build_widgets, version_doc])
def build_mw(c):
    printMW('building dist mountwizzard4')
    with c.cd('.'):
        runMW(c, 'rm -f dist/mountwizzard4*.tar.gz')
        runMW(c, 'python setup.py sdist')
        runMW(c, 'cp dist/mountwizzard4*.tar.gz ../MountWizzard4/dist/mountwizzard4.tar.gz')

    with open('notes.txt') as f:
        tmp = f.readlines()
    rn = ''
    for line in tmp:
        rn += line
    printMW('building dist mountwizzard4 finished\n')


@task(pre=[build_mw])
def upload_mw(c):
    printMW('uploading dist mountwizzard4')
    with c.cd('./dist'):
        print(f'twine upload mountwizzard4-*.tar.gz -r pypi -c "{rn}"')
        runMW(c, f'twine upload mountwizzard4-*.tar.gz -r pypi -c "{rn}"')
    runMW(c, 'rm notes.txt')
    printMW('uploading dist mountwizzard4 finished\n')


def test_windows(c, user, work, scp):
    printMW('...delete test dir')
    runMW(c, f'ssh {user} "if exist {work} rd /s /q {work}"')
    time.sleep(1)
    printMW('...make test dir')
    runMW(c, f'ssh {user} "if not exist {work} mkdir {work}"')
    time.sleep(1)

    with c.cd('dist'):
        printMW('...copy *.tar.gz to test dir')
        runMW(c, f'scp -r mountwizzard4.tar.gz {scp}')

    with c.cd('support/2.0/Windows'):
        printMW('...copy install script to test dir')
        runMW(c, f'scp -r MW4_InstallTest.bat {scp}')
        runMW(c, f'scp -r MW4_Install.bat {scp}')
        printMW('...run install script in test dir')
        runMW(c, f'ssh {user} "cd {work} && MW4_InstallTest.bat"')
        printMW('...copy run script to test dir')
        runMW(c, f'ssh {user} "cd {work} && echo > test.txt"')
        runMW(c, f'scp -r MW4_Run.bat {scp}')
        printMW('...run MountWizzard4 for 3 seconds')
        runMW(c, f'ssh {user} "cd {work} && MW4_Run.bat"')


def test_ubuntu_main(c, user, work, scp):
    printMW('...delete test dir')
    runMW(c, f'ssh {user} "rm -rf {work}"')
    time.sleep(1)
    printMW('...make test dir')
    runMW(c, f'ssh {user} "mkdir {work}"')
    time.sleep(1)

    with c.cd('dist'):
        printMW('...copy *.tar.gz to test dir')
        runMW(c, f'scp -r mountwizzard4.tar.gz {scp}')

    with c.cd('support/2.0/Ubuntu'):
        printMW('...copy install script to test dir')
        runMW(c, f'scp -r MW4_InstallTest.sh {scp}')
        runMW(c, f'scp -r MW4_Install.sh {scp}')
        printMW('...run install script in test dir')
        runMW(c, f'ssh {user} "cd {work} && ./MW4_InstallTest.sh"')
        printMW('...copy run script and environ to test dir')
        runMW(c, f'ssh {user} "cd {work} && touch test.txt"')
        runMW(c, f'scp -r MW4_Run.sh {scp}')
        runMW(c, f'scp -r MountWizzard4.desktop {scp}')
        runMW(c, f'scp -r mw4.png {scp}')
        printMW('...run MountWizzard4 for 3 seconds')
        runMW(c, f'ssh {user} "cd {work} && xvfb-run ./MW4_Run.sh"')


def test_mac(c, user, work, scp):
    printMW('...delete test dir')
    runMW(c, f'ssh {user} "rm -rf {work}"')
    time.sleep(1)
    printMW('...make test dir')
    runMW(c, f'ssh {user} "mkdir {work}"')
    time.sleep(1)

    with c.cd('dist'):
        printMW('...copy *.tar.gz to test dir')
        runMW(c, f'scp -r mountwizzard4.tar.gz {scp}')

    with c.cd('support/2.0/MacOSx'):
        printMW('...copy install script to test dir')
        runMW(c, f'scp -r MW4_InstallTest.command {scp}')
        runMW(c, f'scp -r MW4_Install.command {scp}')
        printMW('...run install script in test dir')
        runMW(c, f'ssh {user} "cd {work} && ./MW4_InstallTest.command"')
        printMW('...copy run script and environ to test dir')
        runMW(c, f'ssh {user} "cd {work} && touch test.txt"')
        runMW(c, f'scp -r MW4_Run.command {scp}')
        printMW('...run MountWizzard4 for 3 seconds')
        runMW(c, f'ssh {user} "cd {work} && ./MW4_Run.command"')


@task(pre=[])
def test_win1032old(c):
    printMW('test windows10 32 old install')
    user = client['win10-32-old']['user']
    work = client['win10-32-old']['work']
    scp = client['win10-32-old']['scp']
    test_windows(c, user, work, scp)
    printMW('test windows10 install finished\n')


@task(pre=[])
def test_win1064old(c):
    printMW('test windows10 64 old install')
    user = client['win10-64-old']['user']
    work = client['win10-64-old']['work']
    scp = client['win10-64-old']['scp']
    test_windows(c, user, work, scp)
    printMW('test windows10 install finished\n')


@task(pre=[])
def test_win1032(c):
    printMW('test windows10 32 install')
    user = client['win10-32']['user']
    work = client['win10-32']['work']
    scp = client['win10-32']['scp']
    test_windows(c, user, work, scp)
    printMW('test windows10 install finished\n')


@task(pre=[])
def test_win1064(c):
    printMW('test windows10 64 install')
    user = client['win10-64']['user']
    work = client['win10-64']['work']
    scp = client['win10-64']['scp']
    test_windows(c, user, work, scp)
    printMW('test windows10 install finished\n')


@task(pre=[])
def test_win11(c):
    printMW('test windows11 install')
    user = client['win11']['user']
    work = client['win11']['work']
    scp = client['win11']['scp']
    test_windows(c, user, work, scp)
    printMW('test windows11 install finished\n')


@task(pre=[])
def test_ubuntu(c):
    printMW('test ubuntu install')
    user = client['ubuntu']['user']
    work = client['ubuntu']['work']
    scp = client['ubuntu']['scp']
    test_ubuntu_main(c, user, work, scp)
    printMW('test ubuntu install finished\n')


@task(pre=[])
def test_comp(c):
    printMW('test ubuntu rig install')
    user = client['ubuntuRig']['user']
    work = client['ubuntuRig']['work']
    scp = client['ubuntuRig']['scp']
    test_ubuntu_main(c, user, work, scp)
    printMW('test ubuntu rig install finished\n')


@task(pre=[])
def test_macMojave(c):
    printMW('test Mojave install')
    user = client['macMojave']['user']
    work = client['macMojave']['work']
    scp = client['macMojave']['scp']
    test_mac(c, user, work, scp)
    printMW('test Mojave install finished\n')


@task(pre=[])
def test_macCatalina(c):
    printMW('test Catalina install')
    user = client['macCatalina']['user']
    work = client['macCatalina']['work']
    scp = client['macCatalina']['scp']
    test_mac(c, user, work, scp)
    printMW('test Catalina install finished\n')


@task(pre=[])
def test_macBigsur(c):
    printMW('test BigSur install')
    user = client['macBigsur']['user']
    work = client['macBigsur']['work']
    scp = client['macBigsur']['scp']
    test_mac(c, user, work, scp)
    printMW('test BigSur install finished\n')


@task(pre=[])
def test_macMonterey(c):
    printMW('test Monterey install')
    user = client['macMonterey']['user']
    work = client['macMonterey']['work']
    scp = client['macMonterey']['scp']
    test_mac(c, user, work, scp)
    printMW('test Monterey install finished\n')
