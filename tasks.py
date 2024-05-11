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
from invoke import task
from PIL import Image
import glob
import time
import os
import zipapp
import zipfile

rn = ''
#
# defining all necessary virtual client login for building over all platforms
#

client = {
    'ubuntu-20': {
        'user': 'mw@astro-ubuntu-20.fritz.box',
        'work': '/home/mw/test',
        'scp': 'mw@astro-ubuntu-20.fritz.box:/home/mw/test',
    },
    'ubuntu-22': {
        'user': 'mw@astro-ubuntu-22.fritz.box',
        'work': '/home/mw/test',
        'scp': 'mw@astro-ubuntu-22.fritz.box:/home/mw/test',
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
    'macVentura': {
        'user': 'mw@astro-mac-ventura.fritz.box',
        'work': 'test',
        'scp': 'mw@astro-mac-ventura.fritz.box:/Users/mw/test',
    },
    'macSonoma': {
        'user': 'mw@astro-mac-sonoma.fritz.box',
        'work': 'test',
        'scp': 'mw@astro-mac-sonoma.fritz.box:/Users/mw/test',
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
    files = glob.glob('./doc/source/**/*.png', recursive=True)
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
    with open('./doc/source/conf.py', 'r') as conf:
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
    with open('./doc/source/conf.py', 'w+') as conf:
        conf.writelines(textNew)
    printMW('changing the version number to setup.py finished\n')


@task
def update_builtins(c):
    printMW('updating builtins')
    runMW(c, 'cp ./work/data/de440_mw4.bsp ./mw4/resource/data/de440_mw4.bsp')
    runMW(c, 'cp ./work/data/visual.txt ./mw4/resource/data/visual.txt')
    runMW(c, 'cp ./work/data/finals2000A.all ./mw4/resource/data/finals2000A.all')
    runMW(c, 'cp ./work/data/finals.data ./mw4/resource/data/finals.data')
    runMW(c, 'cp ./work/data/CDFLeapSeconds.txt ./mw4/resource/data/CDFLeapSeconds.txt')
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
        'keypad', 'main', 'measure', 'message', 'satellite', 'simulator',
        'video', 'bigPopup',
    ]
    for widget in widgets:
        name = widgetDir + widget
        runMW(c, f'python -m PyQt5.uic.pyuic -x {name}.ui -o {name}_ui.py')
    printMW('building widgets finished\n')


@task()
def test_mw(c):
    printMW('testing mountwizzard4')
    runMW(c, 'flake8')
    runMW(c, 'pytest tests/unit_tests/zLoader')
    runMW(c, 'pytest tests/unit_tests/zMainApp')
    runMW(c, 'pytest tests/unit_tests/zUpdate')
    runMW(c, 'pytest tests/unit_tests/base')
    runMW(c, 'pytest tests/unit_tests/gui/extWindows')
    runMW(c, 'pytest tests/unit_tests/gui/mainWindow')
    runMW(c, 'pytest tests/unit_tests/gui/mainWmixin1')
    runMW(c, 'pytest tests/unit_tests/gui/mainWmixin2')
    runMW(c, 'pytest tests/unit_tests/gui/mainWmixin3')
    runMW(c, 'pytest tests/unit_tests/gui/utilities')
    runMW(c, 'pytest tests/unit_tests/indibase')
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
    runMW(c, 'pytest tests/unit_tests/logic/plateSolve')
    runMW(c, 'pytest tests/unit_tests/logic/powerswitch')
    runMW(c, 'pytest tests/unit_tests/logic/remote')
    runMW(c, 'pytest tests/unit_tests/logic/telescope')
    runMW(c, 'pytest tests/unit_tests/mountcontrol')
    printMW('testing mountwizzard finished\n')


@task(pre=[])
def build_startup(c):
    printMW('...make zip archive')
    zipapp.create_archive('./generators/startup/startup.py',
                          target='./support/3.0/startup.pyz',
                          compressed=True,
                          main='startup:main')
    runMW(c, 'cp ./generators/startup/startup.py ./support/3.0')
    os.chdir('./support/3.0')
    with zipfile.ZipFile('startupPackage.zip', 'w') as myzip:
        myzip.write('startup.pyz')
        myzip.write('MountWizzard4.desktop')
        myzip.write('mw4.ico')
        myzip.write('mw4.png')
    runMW(c, 'cp startup.pyz ../../work')
    os.chdir('../../')
    printMW('...copy install script to test dir')


@task(pre=[])
def pypiCleanup(c):
    printMW('...clean pypi from alpha versions')
    regex = '1\\.\\w*\\.\\d\\D\\d*$'
    runMW(c, f'pypi-cleanup -u mworion -p mountwizzard4 -r {regex} -y')


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

    with c.cd('support'):
        runMW(c, f'scp -r ./3.0/startup.pyz {scp}')
        runMW(c, f'ssh {user} "cd {work} && echo > test.run"')
        runMW(c, f'ssh {user} "cd {work} && python startup.pyz --no-start"')
        runMW(c, f'ssh {user} "cd {work} && python startup.pyz"')


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

    with c.cd('support'):
        runMW(c, f'scp -r ./3.0/startup.pyz {scp}')
        runMW(c, f'ssh {user} "cd {work} && echo > test.run"')
        runMW(c, f'ssh {user} "cd {work} && python3 startup.pyz --no-start"')
        runMW(c, f'ssh {user} "cd {work} && python3 startup.pyz"')


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

    with c.cd('support'):
        runMW(c, f'scp -r ./3.0/startup.pyz {scp}')
        runMW(c, f'ssh {user} "cd {work} && echo > test.run"')
        runMW(c, f'ssh {user} "cd {work} && python3 startup.pyz --no-start"')
        runMW(c, f'ssh {user} "cd {work} && python3 startup.pyz"')


@task(pre=[build_startup])
def test_win1032old(c):
    printMW('test windows10 32 old install')
    user = client['win10-32-old']['user']
    work = client['win10-32-old']['work']
    scp = client['win10-32-old']['scp']
    test_windows(c, user, work, scp)
    printMW('test windows10 install finished\n')


@task(pre=[build_startup])
def test_win1064old(c):
    printMW('test windows10 64 old install')
    user = client['win10-64-old']['user']
    work = client['win10-64-old']['work']
    scp = client['win10-64-old']['scp']
    test_windows(c, user, work, scp)
    printMW('test windows10 install finished\n')


@task(pre=[build_startup])
def test_win1032(c):
    printMW('test windows10 32 install')
    user = client['win10-32']['user']
    work = client['win10-32']['work']
    scp = client['win10-32']['scp']
    test_windows(c, user, work, scp)
    printMW('test windows10 install finished\n')


@task(pre=[build_startup])
def test_win1064(c):
    printMW('test windows10 64 install')
    user = client['win10-64']['user']
    work = client['win10-64']['work']
    scp = client['win10-64']['scp']
    test_windows(c, user, work, scp)
    printMW('test windows10 install finished\n')


@task(pre=[build_startup])
def test_win11(c):
    printMW('test windows11 install')
    user = client['win11']['user']
    work = client['win11']['work']
    scp = client['win11']['scp']
    test_windows(c, user, work, scp)
    printMW('test windows11 install finished\n')


@task(pre=[build_startup])
def test_ubuntu_20(c):
    printMW('test ubuntu install')
    user = client['ubuntu-20']['user']
    work = client['ubuntu-20']['work']
    scp = client['ubuntu-20']['scp']
    test_ubuntu_main(c, user, work, scp)
    printMW('test ubuntu install finished\n')


@task(pre=[build_startup])
def test_ubuntu_22(c):
    printMW('test ubuntu install')
    user = client['ubuntu-22']['user']
    work = client['ubuntu-22']['work']
    scp = client['ubuntu-22']['scp']
    test_ubuntu_main(c, user, work, scp)
    printMW('test ubuntu install finished\n')


@task(pre=[build_startup])
def test_comp(c):
    printMW('test ubuntu rig install')
    user = client['ubuntuRig']['user']
    work = client['ubuntuRig']['work']
    scp = client['ubuntuRig']['scp']
    test_ubuntu_main(c, user, work, scp)
    printMW('test ubuntu rig install finished\n')


@task(pre=[build_startup])
def test_macBigsur(c):
    printMW('test BigSur install')
    user = client['macBigsur']['user']
    work = client['macBigsur']['work']
    scp = client['macBigsur']['scp']
    test_mac(c, user, work, scp)
    printMW('test BigSur install finished\n')


@task(pre=[build_startup])
def test_macMonterey(c):
    printMW('test Monterey install')
    user = client['macMonterey']['user']
    work = client['macMonterey']['work']
    scp = client['macMonterey']['scp']
    test_mac(c, user, work, scp)
    printMW('test Monterey install finished\n')


@task(pre=[build_startup])
def test_macVentura(c):
    printMW('test Ventura install')
    user = client['macVentura']['user']
    work = client['macVentura']['work']
    scp = client['macVentura']['scp']
    test_mac(c, user, work, scp)
    printMW('test Ventura install finished\n')


@task(pre=[build_startup])
def test_macSonoma(c):
    printMW('test Sonoma install')
    user = client['macSonoma']['user']
    work = client['macSonoma']['work']
    scp = client['macSonoma']['scp']
    test_mac(c, user, work, scp)
    printMW('test Sonoma install finished\n')


@task(pre=[version_doc])
def make_pdf(c):
    drawio = '/Applications/draw.io.app/Contents/MacOS/draw.io'
    printMW('Generate PDF for distro')
    for fullFilePath in glob.glob('./doc/**/**.drawio', recursive=True):
        output = fullFilePath[:-6] + 'png'
        command = f'{drawio} -x -f png -o {output} {fullFilePath}'
        runMW(c, command)
    with c.cd('doc'):
        runMW(c, 'make latexpdf')
    runMW(c, 'mv ./doc/build/latex/mountwizzard4.pdf ./mw4/resource/data')
    printMW('Generation finished\n')


@task(pre=[version_doc])
def make_html(c):
    drawio = '/Applications/draw.io.app/Contents/MacOS/draw.io'
    printMW('Generate HTML for distro')
    for fullFilePath in glob.glob('./doc/**/**.drawio', recursive=True):
        output = fullFilePath[:-6] + 'png'
        command = f'{drawio} -x -f png -o {output} {fullFilePath}'
        runMW(c, command)
    with c.cd('doc'):
        runMW(c, 'make html')
    with c.cd('docs'):
        runMW(c, 'rm -rf *')
        runMW(c, 'rm -rf .nojekyll')
        runMW(c, 'rm -rf .buildinfo')
    with c.cd('doc/build'):
        runMW(c, 'mv html/* ../../docs')
        runMW(c, 'mv html/.nojekyll ../../docs')
        runMW(c, 'mv html/.buildinfo ../../docs')
    printMW('Generation finished\n')


@task(pre=[make_html, make_pdf, build_resource, build_widgets])
def build_mw(c):
    printMW('building dist mountwizzard4')
    with c.cd('.'):
        runMW(c, 'rm -f dist/mountwizzard4*.tar.gz')
        runMW(c, 'python setup.py sdist')
        runMW(c, 'cp dist/mountwizzard4*.tar.gz '
                 '../MountWizzard4/dist/mountwizzard4.tar.gz')

    with open('notes.txt') as f:
        printMW(f.read())

    printMW('building dist mountwizzard4 finished\n')
    printMW('generating documentation')


@task(pre=[make_pdf, make_html])
def show_doc(c):
    with c.cd('docs'):
        runMW(c, 'open ./index.html')
    runMW(c, 'open ./mw4/resource/data/mountwizzard4.pdf')


@task(pre=[version_doc, build_mw])
def upload_mw(c):
    printMW('uploading dist mountwizzard4')
    with open('notes.txt') as f:
        rn = f.read()
    with c.cd('./dist'):
        print(f'twine upload mountwizzard4-*.tar.gz --verbose -r pypi -c "{rn}"')
        runMW(c, f'twine upload mountwizzard4-*.tar.gz -r pypi -c "{rn}"')
    runMW(c, 'rm notes.txt')
    printMW('uploading dist mountwizzard4 finished\n')
