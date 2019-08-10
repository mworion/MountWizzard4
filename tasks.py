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
    print('clean mountwizzard')
    c.run('rm -rf .pytest_cache')
    c.run('rm -rf mw4.egg-info')
    c.run('find ./mw4 | grep -E "(__pycache__)" | xargs rm -rf')


@task
def clean_mountcontrol(c):
    print('clean mountcontrol')
    with c.cd('../mountcontrol'):
        c.run('rm -rf .pytest_cache')
        c.run('rm -rf mountcontrol.egg-info')
        c.run('find ./mountcontrol | grep -E "(__pycache__)" | xargs rm -rf')


@task
def clean_indibase(c):
    print('clean')
    with c.cd('../indibase'):
        c.run('rm -rf .pytest_cache')
        c.run('rm -rf indibase.egg-info')
        c.run('find ./indibase | grep -E "(__pycache__)" | xargs rm -rf')

#
# building resource and widgets for qt
#


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

#
# doing all the testing stuff
#


@task()
def test_mountcontrol(c):
    print('testing mountcontrol')
    with c.cd('../mountcontrol'):
        c.run('flake8')
        c.run('pytest mountcontrol/test/test_units --cov-config tox.ini --cov mountcontrol/')


@task()
def test_indibase(c):
    print('testing indibase')
    with c.cd('../indibase'):
        c.run('flake8')
        c.run('pytest indibase/test/test_units --cov-config .coveragerc --cov mw4/')


@task(pre=[resource, widgets])
def test_mountwizzard(c):
    print('testing mountwizzard')
    c.run('flake8')
    c.run('pytest mw4/test/test_units --cov-config .coveragerc --cov mw4/')

#
# building the components
#


@task(pre=[])
def build_mountcontrol(c):

    print('building dist mountcontrol')
    with c.cd('../mountcontrol'):
        c.run('rm -f dist/*.tar.gz')
        c.run('python setup.py sdist bdist_egg')


@task(pre=[])
def build_indibase(c):

    print('building dist indibase')
    with c.cd('../indibase'):
        c.run('rm -f dist/*.tar.gz')
        c.run('python setup.py sdist')


@task(pre=[])
def build_mountwizzard(c):
    print('building dist mountwizzard4')
    c.run('rm -f dist/*.tar.gz')
    c.run('python setup.py sdist')

#
# setting up python virtual environments in all platforms for defined context
#


@task()
def venv_ubuntu(c):
    print('preparing ubuntu')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userUbuntu} < setup_ubuntu.sh')


@task()
def venv_windows(c):
    print('preparing windows')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userWindows} < setup_windows.bat')


@task()
def venv_mac(c):
    print('preparing mac')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userMAC} < setup_mac.sh')


@task()
def venv_work(c):
    # this is an actual production platform on my mount
    print('preparing work')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userWork} < setup_ubuntu.sh')

#
# building the apps based on pyinstaller packages
#


@task(pre=[])
def build_windows_app(c):
    print('build windows app and exe')

    # preparing the directories
    c.run('rm -rf ./dist/*.exe')
    c.run(f'ssh {userWindows} "if exist MountWizzard (rmdir /s/q MountWizzard)"')
    c.run(f'ssh {userWindows} "mkdir MountWizzard"')

    # copy necessary files
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {buildWindows}/mc.tar.gz')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {buildWindows}/ib.tar.gz')
    c.run(f'scp dist/*.tar.gz {buildWindows}/mw4.tar.gz')

    c.run(f'scp mw4_windows.spec {buildWindows}')
    c.run(f'scp mw4_windows_console.spec {buildWindows}')
    with c.cd('remote_scripts'):
        c.run(f'scp mw4.ico {buildWindows}')

    # doing the build job
    print('build windows windowed')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userWindows} < build_windows.bat')
    c.run(f'scp {buildWindows}/dist/MountWizzard4.exe ./dist/')


@task(pre=[venv_mac])
def build_mac_local(c):
    print('building mac app and dmg local')
    c.run('rm -rf ./dist/*.app')
    c.run('rm -rf ./dist/*.dmg')
    c.run('pip install ../mountcontrol/dist/mountcontrol-*.tar.gz')
    c.run('pip install ../indibase/dist/indibase-*.tar.gz')
    c.run('pyinstaller -y mw4_mac.spec')
    c.run('hdiutil create dist/MountWizzard4.dmg -srcfolder dist/*.app -ov')


@task(pre=[])
def build_mac_app(c):
    print('build mac app')

    # preparing the directories
    c.run('rm -rf ./dist/*.app')
    c.run(f'ssh {userMAC} rm -rf MountWizzard')
    c.run(f'ssh {userMAC} mkdir MountWizzard')

    # copy necessary files
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {buildMAC}/mc.tar.gz')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {buildMAC}/ib.tar.gz')
    c.run(f'scp dist/*.tar.gz {buildMAC}/mw4.tar.gz')

    c.run(f'scp mw4_mac.spec {buildMAC}')
    with c.cd('remote_scripts'):
        c.run(f'scp mw4.icns {buildMAC}')
        c.run(f'scp dmg_settings.py {buildMAC}')
        c.run(f'scp drive_mw4.png {buildMAC}')
        c.run(f'scp drive_mw4.icns {buildMAC}')
        c.run(f'scp set_image.py {buildMAC}')

    # doing the build job
    print('build app')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userMAC} < build_mac.sh')
    c.run(f'scp {buildMAC}/dist/MountWizzard4.dmg ./dist')
    c.run(f'scp -r {buildMAC}/dist/MountWizzard4.app ./dist')

#
# start deploying the final apps and distributions for first test run on target
# platform. it starts th app with 'test' parameter -> this end the app after 3 sec
#


@task(pre=[])
def deploy_ubuntu_dist(c):

    print('deploy ubuntu dist')
    c.run(f'ssh {userUbuntu} rm -rf mountwizzard4')
    c.run(f'ssh {userUbuntu} mkdir mountwizzard4')

    # copy necessary files
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {workUbuntu}/mc.tar.gz')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {workUbuntu}/ib.tar.gz')
    c.run(f'scp dist/*.tar.gz {workUbuntu}/mw4.tar.gz')

    # run the
    with c.cd('remote_scripts'):
        c.run(f'scp start_ubuntu.sh {workUbuntu}')
        c.run(f'ssh {userUbuntu} < install_dist_ubuntu.sh')


@task(pre=[])
def deploy_mate_dist(c):

    print('deploy mate dist')
    c.run(f'ssh {userMate} rm -rf test')
    c.run(f'ssh {userMate} mkdir test')

    # copy necessary files
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {workMate}/mc.tar.gz')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {workMate}/ib.tar.gz')
    c.run(f'scp dist/*.tar.gz {workMate}/mw4.tar.gz')

    # run the
    with c.cd('remote_scripts'):
        c.run(f'scp MountWizzard4.desktop {workMate}')
        c.run(f'scp mw4.png {workMate}')
        c.run(f'ssh {userMate} < install_dist_mate.sh')


@task(pre=[])
def deploy_work_dist(c):

    print('deploy work dist')

    # copy necessary files
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {workWork}/mc.tar.gz')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {workWork}/ib.tar.gz')
    c.run(f'scp dist/*.tar.gz {workWork}/mw4.tar.gz')

    # run the
    with c.cd('remote_scripts'):
        c.run(f'scp MountWizzard4.desktop {workWork}')
        c.run(f'scp mw4.png {workWork}')
        c.run(f'ssh {userWork} < install_dist_work.sh')
        c.run(f'scp start_work.sh {workMate}')
    c.run(f'ssh {userWork} chmod 777 ./mountwizzard4/start_work.sh')
    c.run(f'ssh {userWork} rm -rf *.tar.gz')


@task(pre=[])
def deploy_windows_dist(c):

    print('deploy windows dist for test')
    c.run(f'ssh {userWindows} "if exist mountwizzard4 (rmdir /s/q mountwizzard4)"')
    c.run(f'ssh {userWindows} "mkdir mountwizzard4"')
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {workWindows}/mc.tar.gz')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {workWindows}/ib.tar.gz')
    c.run(f'scp dist/*.tar.gz {workWindows}/mw4.tar.gz')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userWindows} < install_dist_windows.bat')


@task(pre=[venv_mac])
def deploy_mac_dist(c):

    print('deploy mac dist')
    c.run(f'ssh {userMAC} rm -rf mountwizzard4')
    c.run(f'ssh {userMAC} mkdir mountwizzard4')

    # copy necessary files
    with c.cd('../mountcontrol'):
        c.run(f'scp dist/*.tar.gz {workMAC}/mc.tar.gz')
    with c.cd('../indibase'):
        c.run(f'scp dist/*.tar.gz {workMAC}/ib.tar.gz')
    c.run(f'scp dist/*.tar.gz {workMAC}/mw4.tar.gz')

    # run the installation
    with c.cd('remote_scripts'):
        c.run(f'ssh {userMAC} < install_dist_mac.sh')


@task(pre=[])
def run_windows_app(c):

    print('deploy windows app')
    c.run(f'ssh {userWindows} "if exist mountwizzard4 (rmdir /s/q mountwizzard4)"')
    c.run(f'ssh {userWindows} "mkdir mountwizzard4"')
    with c.cd('./dist'):
        c.run(f'scp MountWizzard4.exe {workWindows}')
    with c.cd('remote_scripts'):
        c.run(f'ssh {userWindows} < start_windows_app.bat')


@task(pre=[])
def run_mac_app(c):
    print('run mac app')

    c.run(f'ssh {userMAC} rm -rf mountwizzard4')
    c.run(f'ssh {userMAC} mkdir mountwizzard4')

    # copy necessary files
    with c.cd('./dist'):
        c.run(f'scp -r MountWizzard4.app {workMAC}')
        comm = '/Users/mw/mountwizzard4/MountWizzard4.app/Contents/MacOS/MountWizzard4 test'
        c.run(f'ssh {userMAC} {comm}')


@task(pre=[])
def run_mac_dist(c):
    print('run mac dist')

    with c.cd('remote_scripts'):
        c.run(f'scp start_mac.sh {workMAC}')
    c.run(f'ssh {userMAC} chmod 777 ./mountwizzard4/start_mac.sh')
    c.run(f'ssh {userMAC} ./mountwizzard4/start_mac.sh')


@task(pre=[])
def run_windows_dist(c):
    print('run windows app')

    with c.cd('remote_scripts'):
        c.run(f'scp start_windows.bat {workWindows}')
    c.run(f'ssh {userWindows} "mountwizzard4\\\\start_windows.bat"')


@task(pre=[])
def run_ubuntu_dist(c):
    print('run ubuntu dist')

    with c.cd('remote_scripts'):
        c.run(f'scp start_ubuntu.sh {workUbuntu}')
    c.run(f'ssh {userUbuntu} chmod 777 ./mountwizzard4/start_ubuntu.sh')
    c.run(f'ssh {userUbuntu} ./mountwizzard4/start_ubuntu.sh')


@task(pre=[])
def run_mate_dist(c):
    print('run work dist')

    with c.cd('remote_scripts'):
        c.run(f'scp start_mate.sh {userMate}')
    c.run(f'ssh {userMate} chmod 777 ./test/start_mate.sh')
    c.run(f'ssh {userMate} ./test/start_mate.sh')


@task(pre=[])
def clean_all(c):

    print('clean all')
    clean_mountcontrol(c)
    clean_indibase(c)
    clean_mountwizzard(c)


@task(pre=[])
def venv_all(c):

    print('venv all')
    venv_mac(c)
    venv_ubuntu(c)
    venv_windows(c)
    venv_work(c)


@task(pre=[])
def test_all(c):

    print('test all')
    test_mountcontrol(c)
    test_mountwizzard(c)


@task(pre=[])
def build_all(c):

    print('build all')
    build_mountcontrol(c)
    build_indibase(c)
    build_mountwizzard(c)
    build_windows_app(c)
    build_mac_app(c)


@task(pre=[])
def deploy_all(c):

    print('deploy all')
    deploy_ubuntu_dist(c)
    deploy_mate_dist(c)
    deploy_windows_dist(c)
    deploy_windows_app(c)
    deploy_mac_dist(c)
    deploy_mac_app(c)


@task(pre=[])
def run_all(c):

    print('run all')
    run_ubuntu_dist(c)
    run_mate_dist(c)
    run_windows_dist(c)
    run_windows_app(c)
    run_mac_dist(c)
    run_mac_app(c)
