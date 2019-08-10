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
from invoke import task, context

#
# defining all necessary virtual client login for building over all platforms
#

# defining environment for ubuntu
clientUbuntu = 'astro-ubuntu.fritz.box'
userUbuntu = 'mw@' + clientUbuntu
workUbuntu = userUbuntu + ':/home/mw/mountwizzard4'

# defining work environment for mate working
clientWork = 'astro-comp.fritz.box'
userWork = 'mw@' + clientWork
workWork = userWork + ':/home/mw/mountwizzard4'

# defining work environment for mate test
clientMate = 'astro-comp.fritz.box'
userMate = 'mw@' + clientMate
workMate = userMate + ':/home/mw/test'

# same for windows10 with cmd.exe as shell
clientWindows = 'astro-windows.fritz.box'
userWindows = 'mw@' + clientWindows
workWindows = userWindows + ':/Users/mw/mountwizzard4'
buildWindows = userWindows + ':/Users/mw/MountWizzard'

# same for mac
clientMAC = 'astro-mac.fritz.box'
userMAC = 'mw@' + clientMAC
workMAC = userMAC + ':/Users/mw/mountwizzard4'
buildMAC = userMAC + ':/Users/mw/MountWizzard'

# cleaning up and refactoring


def runMW(c, param):
    c.run(param, echo=True, hide='out')


def printMW(param):
    print('\n\n\033[95m\033[1m' + param + '\033[0m\n')
#
# cleaning the caches before new build
#


@task
def clean_mountwizzard(c):
    printMW('clean mountwizzard')
    runMW(c, 'rm -rf .pytest_cache')
    runMW(c, 'rm -rf mw4.egg-info')
    runMW(c, 'find ./mw4 | grep -E "(__pycache__)" | xargs rm -rf')


@task
def clean_mountcontrol(c):
    printMW('clean mountcontrol')
    with c.cd('../mountcontrol'):
        runMW(c, 'rm -rf .pytest_cache')
        runMW(c, 'rm -rf mountcontrol.egg-info')
        runMW(c, 'rm -rf ./build/*')
        runMW(c, 'find ./mountcontrol | grep -E "(__pycache__)" | xargs rm -rf')


@task
def clean_indibase(c):
    printMW('clean indibase')
    with c.cd('../indibase'):
        runMW(c, 'rm -rf .pytest_cache')
        runMW(c, 'rm -rf indibase.egg-info')
        runMW(c, 'find ./indibase | grep -E "(__pycache__)" | xargs rm -rf')

#
# setting up python virtual environments in all platforms for defined context
#


@task()
def venv_ubuntu(c):
    printMW('preparing ubuntu')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userUbuntu} < setup_ubuntu.sh')


@task()
def venv_windows(c):
    printMW('preparing windows')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userWindows} < setup_windows.bat')


@task()
def venv_mac(c):
    printMW('preparing mac')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userMAC} < setup_mac.sh')

#
# building resource and widgets for qt
#


@task
def resource(c):
    printMW('building resources')
    resourceDir = 'mw4/gui/media/'
    runMW(c, f'pyrcc5 -o {resourceDir}resources.py {resourceDir}resources.qrc')


@task
def widgets(c):
    printMW('building widgets')
    widgetDir = 'mw4/gui/widgets/'
    widgets = ['hemisphere', 'image', 'main', 'measure', 'message', 'satellite']
    for widget in widgets:
        name = widgetDir + widget
        runMW(c, f'python -m PyQt5.uic.pyuic -x {name}.ui -o {name}_ui.py')

#
# doing all the testing stuff
#


@task()
def test_mountcontrol(c):
    printMW('testing mountcontrol')
    with c.cd('../mountcontrol'):
        runMW(c, 'flake8')
        runMW(c, 'pytest mountcontrol/test/test_units --cov-config tox.ini --cov mountcontrol/')


@task()
def test_indibase(c):
    printMW('testing indibase')
    with c.cd('../indibase'):
        runMW(c, 'flake8')
        runMW(c, 'pytest indibase/test/test_units --cov-config .coveragerc --cov mw4/')


@task(pre=[resource, widgets])
def test_mountwizzard(c):
    printMW('testing mountwizzard')
    runMW(c, 'flake8')
    runMW(c, 'pytest mw4/test/test_units --cov-config .coveragerc --cov mw4/')

#
# building the components
#


@task(pre=[])
def build_mountcontrol(c):
    printMW('building dist mountcontrol')
    with c.cd('../mountcontrol'):
        runMW(c, 'rm -f dist/*.tar.gz')
        runMW(c, 'python setup.py sdist bdist_egg')


@task(pre=[])
def build_indibase(c):
    printMW('building dist indibase')
    with c.cd('../indibase'):
        runMW(c, 'rm -f dist/*.tar.gz')
        runMW(c, 'python setup.py sdist')


@task(pre=[resource, widgets])
def build_mountwizzard(c):
    printMW('building dist mountwizzard4')
    runMW(c, 'rm -f dist/*.tar.gz')
    runMW(c, 'python setup.py sdist')


@task()
def venv_work(c):
    printMW('preparing work')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userWork} < setup_ubuntu.sh')

#
# building the apps based on pyinstaller packages
#


@task(pre=[])
def build_windows_app(c):
    printMW('build windows app and exe')
    # preparing the directories
    runMW(c, 'rm -rf ./dist/*.exe')
    runMW(c, f'ssh {userWindows} "if exist MountWizzard (rmdir /s/q MountWizzard)"')
    runMW(c, f'ssh {userWindows} "mkdir MountWizzard"')
    # copy necessary files
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {buildWindows}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {buildWindows}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {buildWindows}/mw4.tar.gz')

    runMW(c, f'scp mw4_windows.spec {buildWindows}')
    runMW(c, f'scp mw4_windows_console.spec {buildWindows}')
    with c.cd('remote_scripts'):
        runMW(c, f'scp mw4.ico {buildWindows}')
    # doing the build job
    print('build windows windowed')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userWindows} < build_windows.bat')
    runMW(c, f'scp {buildWindows}/dist/MountWizzard4.exe ./dist/')


@task(pre=[venv_mac])
def build_mac_local(c):
    printMW('building mac app and dmg local')
    runMW(c, 'rm -rf ./dist/*.app')
    runMW(c, 'rm -rf ./dist/*.dmg')
    runMW(c, 'pip install ../mountcontrol/dist/mountcontrol-*.tar.gz')
    runMW(c, 'pip install ../indibase/dist/indibase-*.tar.gz')
    runMW(c, 'pyinstaller -y mw4_mac.spec')
    runMW(c, 'hdiutil create dist/MountWizzard4.dmg -srcfolder dist/*.app -ov')


@task(pre=[])
def build_mac_app(c):
    printMW('build mac app')
    # preparing the directories
    runMW(c, 'rm -rf ./dist/*.app')
    runMW(c, f'ssh {userMAC} rm -rf MountWizzard')
    runMW(c, f'ssh {userMAC} mkdir MountWizzard')
    # copy necessary files
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {buildMAC}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {buildMAC}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {buildMAC}/mw4.tar.gz')
    runMW(c, f'scp mw4_mac.spec {buildMAC}')
    with c.cd('remote_scripts'):
        runMW(c, f'scp mw4.icns {buildMAC}')
        runMW(c, f'scp dmg_settings.py {buildMAC}')
        runMW(c, f'scp drive_mw4.png {buildMAC}')
        runMW(c, f'scp drive_mw4.icns {buildMAC}')
        runMW(c, f'scp set_image.py {buildMAC}')
    # doing the build job
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userMAC} < build_mac.sh')
    runMW(c, f'scp {buildMAC}/dist/MountWizzard4.dmg ./dist')
    runMW(c, f'scp -r {buildMAC}/dist/MountWizzard4.app ./dist')

#
# start deploying the final apps and distributions for first test run on target
# platform. it starts th app with 'test' parameter -> this end the app after 3 sec
#


@task(pre=[])
def deploy_ubuntu_dist(c):
    printMW('deploy ubuntu dist')
    runMW(c, f'ssh {userUbuntu} rm -rf mountwizzard4')
    runMW(c, f'ssh {userUbuntu} mkdir mountwizzard4')
    # copy necessary files
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {workUbuntu}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {workUbuntu}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {workUbuntu}/mw4.tar.gz')
    with c.cd('remote_scripts'):
        runMW(c, f'scp start_ubuntu.sh {workUbuntu}')
        runMW(c, f'ssh {userUbuntu} < install_dist_ubuntu.sh')


@task(pre=[])
def deploy_mate_dist(c):
    printMW('deploy mate dist')
    runMW(c, f'ssh {userMate} rm -rf test')
    runMW(c, f'ssh {userMate} mkdir test')
    # copy necessary files
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {workMate}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {workMate}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {workMate}/mw4.tar.gz')

    with c.cd('remote_scripts'):
        runMW(c, f'scp MountWizzard4.desktop {workMate}')
        runMW(c, f'scp mw4.png {workMate}')
        runMW(c, f'ssh {userMate} < install_dist_mate.sh')


@task(pre=[])
def deploy_work_dist(c):
    printMW('deploy work dist')
    # copy necessary files
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {workWork}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {workWork}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {workWork}/mw4.tar.gz')

    # run the
    with c.cd('remote_scripts'):
        runMW(c, f'scp MountWizzard4.desktop {userWork}/.local/share/applications')
        runMW(c, f'scp mw4.png {workWork}')
        runMW(c, f'ssh {userWork} < install_dist_work.sh')
        runMW(c, f'scp start_work.sh {userWork}')
    runMW(c, f'ssh {userWork} chmod 777 ./mountwizzard4/start_work.sh')
    runMW(c, f'ssh {userWork} rm -rf ./mountwizzard4/*.tar.gz')


@task(pre=[])
def deploy_windows_dist(c):
    printMW('deploy windows dist')
    runMW(c, f'ssh {userWindows} "if exist mountwizzard4 (rmdir /s/q mountwizzard4)"')
    runMW(c, f'ssh {userWindows} "mkdir mountwizzard4"')
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {workWindows}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {workWindows}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {workWindows}/mw4.tar.gz')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userWindows} < install_dist_windows.bat')


@task(pre=[venv_mac])
def deploy_mac_dist(c):
    printMW('deploy mac dist')
    runMW(c, f'ssh {userMAC} rm -rf mountwizzard4')
    runMW(c, f'ssh {userMAC} mkdir mountwizzard4')
    # copy necessary files
    with c.cd('../mountcontrol'):
        runMW(c, f'scp dist/*.tar.gz {workMAC}/mc.tar.gz')
    with c.cd('../indibase'):
        runMW(c, f'scp dist/*.tar.gz {workMAC}/ib.tar.gz')
    runMW(c, f'scp dist/*.tar.gz {workMAC}/mw4.tar.gz')

    # run the installation
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userMAC} < install_dist_mac.sh')


@task(pre=[])
def run_windows_app(c):
    printMW('deploy windows app')
    runMW(c, f'ssh {userWindows} "if exist mountwizzard4 (rmdir /s/q mountwizzard4)"')
    runMW(c, f'ssh {userWindows} "mkdir mountwizzard4"')
    with c.cd('./dist'):
        runMW(c, f'scp MountWizzard4.exe {workWindows}')
    with c.cd('remote_scripts'):
        runMW(c, f'ssh {userWindows} < start_windows_app.bat')


@task(pre=[])
def run_mac_app(c):
    printMW('run mac app')
    runMW(c, f'ssh {userMAC} rm -rf mountwizzard4')
    runMW(c, f'ssh {userMAC} mkdir mountwizzard4')
    # copy necessary files
    with c.cd('./dist'):
        runMW(c, f'scp -r MountWizzard4.app {workMAC}')
        comm = '/Users/mw/mountwizzard4/MountWizzard4.app/Contents/MacOS/MountWizzard4 test'
        runMW(c, f'ssh {userMAC} {comm}')


@task(pre=[])
def run_mac_dist(c):
    printMW('run mac dist')
    with c.cd('remote_scripts'):
        runMW(c, f'scp start_mac.sh {workMAC}')
    runMW(c, f'ssh {userMAC} chmod 777 ./mountwizzard4/start_mac.sh')
    runMW(c, f'ssh {userMAC} ./mountwizzard4/start_mac.sh')


@task(pre=[])
def run_windows_dist(c):
    printMW('run windows app')
    with c.cd('remote_scripts'):
        runMW(c, f'scp start_windows.bat {workWindows}')
    runMW(c, f'ssh {userWindows} "mountwizzard4\\\\start_windows.bat"')


@task(pre=[])
def run_ubuntu_dist(c):
    printMW('un ubuntu dist')
    with c.cd('remote_scripts'):
        runMW(c, f'scp start_ubuntu.sh {workUbuntu}')
    runMW(c, f'ssh {userUbuntu} chmod 777 ./mountwizzard4/start_ubuntu.sh')
    runMW(c, f'ssh {userUbuntu} ./mountwizzard4/start_ubuntu.sh')


@task(pre=[])
def run_mate_dist(c):
    printMW('run work dist')
    with c.cd('remote_scripts'):
        runMW(c, f'scp start_mate.sh {userMate}')
    runMW(c, f'ssh {userMate} chmod 777 ./test/start_mate.sh')
    runMW(c, f'ssh {userMate} ./test/start_mate.sh')


@task(pre=[])
def clean_all(c):
    printMW('clean all')
    clean_mountcontrol(c)
    clean_indibase(c)
    clean_mountwizzard(c)


@task(pre=[])
def venv_all(c):
    printMW('venv all')
    venv_mac(c)
    venv_ubuntu(c)
    venv_windows(c)
    venv_work(c)


@task(pre=[])
def test_all(c):
    printMW('test all')
    test_mountcontrol(c)
    test_mountwizzard(c)


@task(pre=[])
def build_all(c):
    printMW('build all')
    build_mountcontrol(c)
    build_indibase(c)
    build_mountwizzard(c)
    build_windows_app(c)
    build_mac_app(c)


@task(pre=[])
def deploy_all(c):
    printMW('deploy all')
    deploy_ubuntu_dist(c)
    deploy_mate_dist(c)
    deploy_windows_dist(c)
    deploy_mac_dist(c)


@task(pre=[])
def run_all(c):
    printMW('run all')
    run_ubuntu_dist(c)
    run_mate_dist(c)
    run_windows_dist(c)
    run_windows_app(c)
    run_mac_dist(c)
    run_mac_app(c)
