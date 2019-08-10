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

#
# cleaning the caches before new build
#


@task
def clean_mountwizzard(c):
    print('\n\n\033[95m\033[1m' + 'clean mountwizzard' + '\033[0m\n')
    c.run('rm -rf .pytest_cache', echo=True, hide='out')
    c.run('rm -rf mw4.egg-info', echo=True, hide='out')
    c.run('find ./mw4 | grep -E "(__pycache__)" | xargs rm -rf', echo=True, hide='out')


@task
def clean_mountcontrol(c):
    print('\n\n\033[95m\033[1m' + 'clean mountcontrol' + '\033[0m\n')
    with c.cd('../mountcontrol'):
        c.run('rm -rf .pytest_cache', echo=True, hide='out')
        c.run('rm -rf mountcontrol.egg-info', echo=True, hide='out')
        c.run('find ./mountcontrol | grep -E "(__pycache__)" | xargs rm -rf', echo=True, hide='out')


@task
def clean_indibase(c):
    print('\n\n\033[95m\033[1m' + 'clean indibase' + '\033[0m\n')
    with c.cd('../indibase'):
        c.run('rm -rf .pytest_cache', echo=True, hide='out')
        c.run('rm -rf indibase.egg-info', echo=True, hide='out')
        c.run('find ./indibase | grep -E "(__pycache__)" | xargs rm -rf', echo=True, hide='out')

#
# building resource and widgets for qt
#


@task
def resource(c):
    print('\n\n\033[95m\033[1m' + 'building resources' + '\033[0m\n')
    resourceDir = 'mw4/gui/media/'
    c.run(f'pyrcc5 -o {resourceDir}resources.py {resourceDir}resources.qrc', echo=True, hide='out')


@task
def widgets(c):
    print('\n\n\033[95m\033[1m' + 'building widgets' + '\033[0m\n')
    widgetDir = 'mw4/gui/widgets/'
    widgets = ['hemisphere', 'image', 'main', 'measure', 'message', 'satellite']
    for widget in widgets:
        name = widgetDir + widget
        c.run(f'python -m PyQt5.uic.pyuic -x {name}.ui -o {name}_ui.py', echo=True, hide='out')

#
# doing all the testing stuff
#


@task()
def test_mountcontrol(c):
    print('\n\n\033[95m\033[1m' + 'testing mountcontrol' + '\033[0m\n')
    with c.cd('../mountcontrol'):
        c.run('flake8', echo=True, hide='out')
        c.run('pytest mountcontrol/test/test_units --cov-config tox.ini --cov mountcontrol/', echo=True, hide='out')


@task()
def test_indibase(c):
    print('\n\n\033[95m\033[1m' + 'testing indibase' + '\033[0m\n')
    with c.cd('../indibase'):
        c.run('flake8', echo=True, hide='out')
        c.run('pytest indibase/test/test_units --cov-config .coveragerc --cov mw4/', echo=True, hide='out')


@task(pre=[resource, widgets])
def test_mountwizzard(c):
    print('\n\n\033[95m\033[1m' + 'testing mountwizzard' + '\033[0m\n')
    c.run('flake8', echo=True, hide='out')
    c.run('pytest mw4/test/test_units --cov-config .coveragerc --cov mw4/', echo=True, hide='out')

#
# building the components
#


@task(pre=[])
def build_mountcontrol(c):
    print('\n\n\033[95m\033[1m' + 'building dist mountcontrol' + '\033[0m\n')
    with c.cd('../mountcontrol'):
        c.run('rm -f dist/*.tar.gz', echo=True, hide='out')
        c.run('python setup.py sdist bdist_egg', echo=True, hide='out')


@task(pre=[])
def build_indibase(c):
    print('\n\n\033[95m\033[1m' + 'building dist indibase' + '\033[0m\n')
    with c.cd('../indibase'):
        c.run('rm -f dist/*.tar.gz', echo=True, hide='out')
        c.run('python setup.py sdist', echo=True, hide='out')


@task(pre=[resource, widgets])
def build_mountwizzard(c):
    print('\n\n\033[95m\033[1m' + 'building dist mountwizzard4' + '\033[0m\n')
    c.run('rm -f dist/*.tar.gz', echo=True, hide='out')
    c.run('python setup.py sdist', echo=True, hide='out')

#
# setting up python virtual environments in all platforms for defined context
#


@task()
def venv_ubuntu(c):
    print('\n\n\033[95m\033[1m' + 'preparing ubuntu' + '\033[0m\n')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userUbuntu} < setup_ubuntu.sh', echo=True, hide='out')


@task()
def venv_windows(c):
    print('\n\n\033[95m\033[1m' + 'preparing windows' + '\033[0m\n')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userWindows} < setup_windows.bat', echo=True, hide='out')


@task()
def venv_mac(c):
    print('\n\n\033[95m\033[1m' + 'preparing mac' + '\033[0m\n')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userMAC} < setup_mac.sh', echo=True, hide='out')


@task()
def venv_work(c):
    print('\n\n\033[95m\033[1m' + 'preparing work' + '\033[0m\n')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userWork} < setup_ubuntu.sh', echo=True, hide='out')

#
# building the apps based on pyinstaller packages
#


@task(pre=[])
def build_windows_app(c):
    print('\n\n\033[95m\033[1m' + 'build windows app and exe' + '\033[0m\n')
    # preparing the directories
    c.run('rm -rf ./dist/*.exe')
    c.run(f'ssh {userWindows} "if exist MountWizzard (rmdir /s/q MountWizzard)"', echo=True, hide='out')
    c.run(f'ssh {userWindows} "mkdir MountWizzard"', echo=True, hide='out')
    # copy necessary files
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {buildWindows}/mc.tar.gz', echo=True, hide='out')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {buildWindows}/ib.tar.gz', echo=True, hide='out')
    c.run(f'scp dist/*.tar.gz {buildWindows}/mw4.tar.gz', echo=True, hide='out')

    c.run(f'scp mw4_windows.spec {buildWindows}', echo=True, hide='out')
    c.run(f'scp mw4_windows_console.spec {buildWindows}', echo=True, hide='out')
    with c.cd('remote_scripts'):
        c.run(f'scp mw4.ico {buildWindows}', echo=True, hide='out')
    # doing the build job
    print('build windows windowed')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userWindows} < build_windows.bat', echo=True, hide='out')
    c.run(f'scp {buildWindows}/dist/MountWizzard4.exe ./dist/', echo=True, hide='out')


@task(pre=[venv_mac])
def build_mac_local(c):
    print('\n\n\033[95m\033[1m' + 'building mac app and dmg local' + '\033[0m\n')
    c.run('rm -rf ./dist/*.app', echo=True, hide='out')
    c.run('rm -rf ./dist/*.dmg', echo=True, hide='out')
    c.run('pip install ../mountcontrol/dist/mountcontrol-*.tar.gz', echo=True, hide='out')
    c.run('pip install ../indibase/dist/indibase-*.tar.gz', echo=True, hide='out')
    c.run('pyinstaller -y mw4_mac.spec', echo=True, hide='out')
    c.run('hdiutil create dist/MountWizzard4.dmg -srcfolder dist/*.app -ov', echo=True, hide='out')


@task(pre=[])
def build_mac_app(c):
    print('\n\n\033[95m\033[1m' + 'build mac app' + '\033[0m\n')
    # preparing the directories
    c.run('rm -rf ./dist/*.app')
    c.run(f'ssh {userMAC} rm -rf MountWizzard', echo=True, hide='out')
    c.run(f'ssh {userMAC} mkdir MountWizzard', echo=True, hide='out')
    # copy necessary files
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {buildMAC}/mc.tar.gz', echo=True, hide='out')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {buildMAC}/ib.tar.gz', echo=True, hide='out')
    c.run(f'scp dist/*.tar.gz {buildMAC}/mw4.tar.gz', echo=True, hide='out')
    c.run(f'scp mw4_mac.spec {buildMAC}', echo=True, hide='out')
    with c.cd('remote_scripts'):
        c.run(f'scp mw4.icns {buildMAC}', echo=True, hide='out')
        c.run(f'scp dmg_settings.py {buildMAC}', echo=True, hide='out')
        c.run(f'scp drive_mw4.png {buildMAC}', echo=True, hide='out')
        c.run(f'scp drive_mw4.icns {buildMAC}', echo=True, hide='out')
        c.run(f'scp set_image.py {buildMAC}', echo=True, hide='out')
    # doing the build job
    with c.cd('remote_scripts'):
        c.run(f'ssh {userMAC} < build_mac.sh', echo=True, hide='out')
    c.run(f'scp {buildMAC}/dist/MountWizzard4.dmg ./dist', echo=True, hide='out')
    c.run(f'scp -r {buildMAC}/dist/MountWizzard4.app ./dist', echo=True, hide='out')

#
# start deploying the final apps and distributions for first test run on target
# platform. it starts th app with 'test' parameter -> this end the app after 3 sec
#


@task(pre=[])
def deploy_ubuntu_dist(c):
    print('\n\n\033[95m\033[1m' + 'deploy ubuntu dist' + '\033[0m\n')
    c.run(f'ssh {userUbuntu} rm -rf mountwizzard4', echo=True, hide='out')
    c.run(f'ssh {userUbuntu} mkdir mountwizzard4', echo=True, hide='out')
    # copy necessary files
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {workUbuntu}/mc.tar.gz', echo=True, hide='out')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {workUbuntu}/ib.tar.gz', echo=True, hide='out')
    c.run(f'scp dist/*.tar.gz {workUbuntu}/mw4.tar.gz', echo=True, hide='out')
    with c.cd('remote_scripts'):
        c.run(f'scp start_ubuntu.sh {workUbuntu}', echo=True, hide='out')
        c.run(f'ssh {userUbuntu} < install_dist_ubuntu.sh', echo=True, hide='out')


@task(pre=[])
def deploy_mate_dist(c):
    print('\n\n\033[95m\033[1m' + 'deploy mate dist' + '\033[0m\n')
    c.run(f'ssh {userMate} rm -rf test', echo=True, hide='out')
    c.run(f'ssh {userMate} mkdir test', echo=True, hide='out')
    # copy necessary files
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {workMate}/mc.tar.gz', echo=True, hide='out')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {workMate}/ib.tar.gz', echo=True, hide='out')
    c.run(f'scp dist/*.tar.gz {workMate}/mw4.tar.gz', echo=True, hide='out')

    with c.cd('remote_scripts'):
        c.run(f'scp MountWizzard4.desktop {workMate}', echo=True, hide='out')
        c.run(f'scp mw4.png {workMate}', echo=True, hide='out')
        c.run(f'ssh {userMate} < install_dist_mate.sh', echo=True, hide='out')


@task(pre=[])
def deploy_work_dist(c):
    print('\n\n\033[95m\033[1m' + 'deploy work dist' + '\033[0m\n')
    # copy necessary files
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {workWork}/mc.tar.gz', echo=True, hide='out')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {workWork}/ib.tar.gz', echo=True, hide='out')
    c.run(f'scp dist/*.tar.gz {workWork}/mw4.tar.gz', echo=True, hide='out')

    # run the
    with c.cd('remote_scripts'):
        c.run(f'scp MountWizzard4.desktop {workWork}', echo=True, hide='out')
        c.run(f'scp mw4.png {workWork}', echo=True, hide='out')
        c.run(f'ssh {userWork} < install_dist_work.sh', echo=True, hide='out')
        c.run(f'scp start_work.sh {workMate}', echo=True, hide='out')
    c.run(f'ssh {userWork} chmod 777 ./mountwizzard4/start_work.sh', echo=True, hide='out')
    c.run(f'ssh {userWork} rm -rf *.tar.gz', echo=True, hide='out')


@task(pre=[])
def deploy_windows_dist(c):
    print('\n\n\033[95m\033[1m' + 'deploy windows dist' + '\033[0m\n')
    c.run(f'ssh {userWindows} "if exist mountwizzard4 (rmdir /s/q mountwizzard4)"', echo=True, hide='out')
    c.run(f'ssh {userWindows} "mkdir mountwizzard4"', echo=True, hide='out')
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {workWindows}/mc.tar.gz', echo=True, hide='out')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {workWindows}/ib.tar.gz', echo=True, hide='out')
    c.run(f'scp dist/*.tar.gz {workWindows}/mw4.tar.gz', echo=True, hide='out')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userWindows} < install_dist_windows.bat', echo=True, hide='out')


@task(pre=[venv_mac])
def deploy_mac_dist(c):
    print('\n\n\033[95m\033[1m' + 'deploy mac dist' + '\033[0m\n')
    c.run(f'ssh {userMAC} rm -rf mountwizzard4', echo=True, hide='out')
    c.run(f'ssh {userMAC} mkdir mountwizzard4', echo=True, hide='out')
    # copy necessary files
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {workMAC}/mc.tar.gz', echo=True, hide='out')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {workMAC}/ib.tar.gz', echo=True, hide='out')
    c.run(f'scp dist/*.tar.gz {workMAC}/mw4.tar.gz', echo=True, hide='out')

    # run the installation
    with c.cd('remote_scripts'):
        c.run(f'ssh {userMAC} < install_dist_mac.sh', echo=True, hide='out')


@task(pre=[])
def run_windows_app(c):
    print('\n\n\033[95m\033[1m' + 'deploy windows app' + '\033[0m\n')
    c.run(f'ssh {userWindows} "if exist mountwizzard4 (rmdir /s/q mountwizzard4)"', echo=True, hide='out')
    c.run(f'ssh {userWindows} "mkdir mountwizzard4"', echo=True, hide='out')
    with c.cd('./dist'):
        c.run(f'scp MountWizzard4.exe {workWindows}', echo=True, hide='out')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userWindows} < start_windows_app.bat', echo=True, hide='out')


@task(pre=[])
def run_mac_app(c):
    print('\n\n\033[95m\033[1m' + 'run mac app' + '\033[0m\n')
    c.run(f'ssh {userMAC} rm -rf mountwizzard4', echo=True, hide='out')
    c.run(f'ssh {userMAC} mkdir mountwizzard4', echo=True, hide='out')
    # copy necessary files
    with c.cd('./dist'):
        c.run(f'scp -r MountWizzard4.app {workMAC}', echo=True, hide='out')
        comm = '/Users/mw/mountwizzard4/MountWizzard4.app/Contents/MacOS/MountWizzard4 test'
        c.run(f'ssh {userMAC} {comm}', echo=True, hide='out')


@task(pre=[])
def run_mac_dist(c):
    print('\n\n\033[95m\033[1m' + 'run mac dist' + '\033[0m\n')
    with c.cd('remote_scripts'):
        c.run(f'scp start_mac.sh {workMAC}', echo=True, hide='out')
    c.run(f'ssh {userMAC} chmod 777 ./mountwizzard4/start_mac.sh', echo=True, hide='out')
    c.run(f'ssh {userMAC} ./mountwizzard4/start_mac.sh', echo=True, hide='out')


@task(pre=[])
def run_windows_dist(c):
    print('\n\n\033[95m\033[1m' + 'run windows app' + '\033[0m\n')
    with c.cd('remote_scripts'):
        c.run(f'scp start_windows.bat {workWindows}', echo=True, hide='out')
    c.run(f'ssh {userWindows} "mountwizzard4\\\\start_windows.bat"', echo=True, hide='out')


@task(pre=[])
def run_ubuntu_dist(c):
    print('\n\n\033[95m\033[1m' + 'un ubuntu dist' + '\033[0m\n')
    with c.cd('remote_scripts'):
        c.run(f'scp start_ubuntu.sh {workUbuntu}', echo=True, hide='out')
    c.run(f'ssh {userUbuntu} chmod 777 ./mountwizzard4/start_ubuntu.sh', echo=True, hide='out')
    c.run(f'ssh {userUbuntu} ./mountwizzard4/start_ubuntu.sh', echo=True, hide='out')


@task(pre=[])
def run_mate_dist(c):
    print('\n\n\033[95m\033[1m' + 'run work dist' + '\033[0m\n')
    with c.cd('remote_scripts'):
        c.run(f'scp start_mate.sh {userMate}', echo=True, hide='out')
    c.run(f'ssh {userMate} chmod 777 ./test/start_mate.sh', echo=True, hide='out')
    c.run(f'ssh {userMate} ./test/start_mate.sh', echo=True, hide='out')


@task(pre=[])
def clean_all(c):
    print('\n\n\033[95m\033[1m' + 'clean all' + '\033[0m\n')
    clean_mountcontrol(c)
    clean_indibase(c)
    clean_mountwizzard(c)


@task(pre=[])
def venv_all(c):
    print('\n\n\033[95m\033[1m' + 'venv all' + '\033[0m\n')
    venv_mac(c)
    venv_ubuntu(c)
    venv_windows(c)
    venv_work(c)


@task(pre=[])
def test_all(c):
    print('\n\n\033[95m\033[1m' + 'test all' + '\033[0m\n')
    test_mountcontrol(c)
    test_mountwizzard(c)


@task(pre=[])
def build_all(c):
    print('\n\n\033[95m\033[1m' + 'build all' + '\033[0m\n')
    build_mountcontrol(c)
    build_indibase(c)
    build_mountwizzard(c)
    build_windows_app(c)
    build_mac_app(c)


@task(pre=[])
def deploy_all(c):
    print('\n\n\033[95m\033[1m' + 'deploy all' + '\033[0m\n')
    deploy_ubuntu_dist(c)
    deploy_mate_dist(c)
    deploy_windows_dist(c)
    deploy_mac_dist(c)


@task(pre=[])
def run_all(c):
    print('\n\n\033[95m\033[1m' + 'run all' + '\033[0m\n')
    run_ubuntu_dist(c)
    run_mate_dist(c)
    run_windows_dist(c)
    run_windows_app(c)
    run_mac_dist(c)
    run_mac_app(c)
