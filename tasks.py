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
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
from invoke import task
import glob
import time
import os

rn = ""
#
# defining all necessary virtual client login for building over all platforms
#

client = {
    "ubuntu20": {
        "user": "mw@astro-ubuntu-20.uranus",
        "work": "/home/mw/test",
        "scp": "mw@astro-ubuntu-20.uranus:/home/mw/test",
    },
    "ubuntu22": {
        "user": "mw@astro-ubuntu-22.uranus",
        "work": "/home/mw/test",
        "scp": "mw@astro-ubuntu-22.uranus:/home/mw/test",
    },
    "ubuntu24": {
        "user": "mw@astro-ubuntu-24.uranus",
        "work": "/home/mw/test",
        "scp": "mw@astro-ubuntu-24.uranus:/home/mw/test",
    },
    "ubuntuRig": {
        "user": "mw@astro-comp.uranus",
        "work": "/home/mw/test",
        "scp": "mw@astro-comp.uranus:/home/mw/test",
    },
    "win10": {
        "user": "mw@astro-win-10.uranus",
        "work": "test",
        "scp": "mw@astro-win-10.uranus:/Users/mw/test",
    },
    "win11": {
        "user": "mw@astro-win-11.uranus",
        "work": "test",
        "scp": "mw@astro-win-11.uranus:/Users/mw/test",
    },
    "mac11": {
        "user": "mw@astro-mac-10.uranus",
        "work": "test",
        "scp": "mw@astro-mac-12.uranus:/Users/mw/test",
    },
    "mac12": {
        "user": "mw@astro-mac-12.uranus",
        "work": "test",
        "scp": "mw@astro-mac-m12.uranus:/Users/mw/test",
    },
    "mac13": {
        "user": "mw@astro-mac-13.uranus",
        "work": "test",
        "scp": "mw@astro-mac-13.uranus:/Users/mw/test",
    },
    "mac14": {
        "user": "mw@astro-mac-14.uranus",
        "work": "test",
        "scp": "mw@astro-mac-14.uranus:/Users/mw/test",
    },
    "mac15": {
        "user": "mw@astro-mac-15.uranus",
        "work": "test",
        "scp": "mw@astro-mac-15.uranus:/Users/mw/test",
    },
    "mac26": {
        "user": "mw@astro-mac-26.uranus",
        "work": "test",
        "scp": "mw@astro-mac-26.uranus:/Users/mw/test",
    },
}


def runMW(c, param):
    c.run(param)


def printMW(param):
    print(param)


@task
def log(c):
    runMW(c, "python3 logViewer.py")


@task
def clean_mw(c):
    printMW("clean mountwizzard")
    runMW(c, "rm -rf .pytest_cache")
    runMW(c, "rm -rf mw4.egg-info")
    runMW(c, 'find ./src/mw4 | grep -E "(__pycache__)" | xargs rm -rf')
    runMW(c, 'find ./tests | grep -E "(__pycache__)" | xargs rm -rf')
    printMW("clean mountwizzard finished\n")


@task
def version_doc(c):
    printMW("changing the version number to setup.py")

    # getting version of desired package
    with open("pyproject.toml") as setup:
        text = setup.readlines()

    for line in text:
        if line.strip().startswith("version"):
            _, number, _ = line.split('"')

    # reading configuration file
    with open("./doc/conf.py") as conf:
        text = conf.readlines()
    textNew = list()

    print(f"version is >{number}<")

    # replacing the version number
    for line in text:
        if line.startswith("version"):
            line = f"version = '{number}'\n"
        if line.startswith("release"):
            line = f"release = '{number}'\n"
        textNew.append(line)

    # writing configuration file
    with open("./doc/conf.py", "w+") as conf:
        conf.writelines(textNew)
    printMW("changing the version number to setup.py finished\n")


@task
def update_builtins(c):
    printMW("updating builtins")
    runMW(c, "cp ./work/data/de440_mw4.bsp ./src_add/assets/data/de440_mw4.bsp")
    runMW(c, "cp ./work/data/finals2000A.all ./src_add/assets/data/finals2000A.all")
    runMW(c, "cp ./work/data/finals.data ./src_add/assets/data/finals.data")
    runMW(c, "cp ./work/data/CDFLeapSeconds.txt ./src_add/assets/data/CDFLeapSeconds.txt")
    printMW("updating builtins finished\n")


@task
def build_resource(c):
    printMW("building resources")
    resourceDir = "./src_add/assets/"
    resourceDestDir = "./src/mw4/assets/"
    with c.cd(resourceDir + "data"):
        with open(resourceDir + "data/content.txt", "w") as f:
            for file in glob.glob(resourceDir + "data/*.*"):
                t = os.stat(file).st_mtime
                f.write(f"{os.path.basename(file)} {t}\n")
    runMW(c, f"uv run pyside6-rcc -o {resourceDestDir}assetsData.py {resourceDir}assetData.qrc")
    printMW("building resources finished\n")


@task
def build_widgets(c):
    printMW("building widgets")
    widgetDirIn = "./src_add/widgets/"
    widgetDirOut = "./src/mw4/gui/widgets/"
    widgets = [
        "analyse",
        "devicePopup",
        "downloadPopup",
        "hemisphere",
        "image",
        "keypad",
        "main",
        "measure",
        "message",
        "satellite",
        "simulator",
        "video",
        "bigPopup",
        "uploadPopup",
        "material",
    ]
    for widget in widgets:
        nameIn = widgetDirIn + widget
        nameOut = widgetDirOut + widget
        runMW(c, f"uv run pyside6-uic {nameIn}.ui > {nameOut}_ui.py")
    printMW("building widgets finished\n")


@task()
def test_mw(c):
    printMW("testing mountwizzard4")
    runMW(c, "flake8")
    runMW(c, "pytest tests/unit_tests/zLoader")
    runMW(c, "pytest tests/unit_tests/zMainApp")
    runMW(c, "pytest tests/unit_tests/zUpdate")
    runMW(c, "pytest tests/unit_tests/base")
    runMW(c, "pytest tests/unit_tests/gui/extWindows")
    runMW(c, "pytest tests/unit_tests/gui/mainWindow")
    runMW(c, "pytest tests/unit_tests/gui/mainWmixin1")
    runMW(c, "pytest tests/unit_tests/gui/mainWmixin2")
    runMW(c, "pytest tests/unit_tests/gui/mainWmixin3")
    runMW(c, "pytest tests/unit_tests/gui/utilities")
    runMW(c, "pytest tests/unit_tests/indibase")
    runMW(c, "pytest tests/unit_tests/logic/automation")
    runMW(c, "pytest tests/unit_tests/logic/camera")
    runMW(c, "pytest tests/unit_tests/logic/cover")
    runMW(c, "pytest tests/unit_tests/logic/databaseProcessing")
    runMW(c, "pytest tests/unit_tests/logic/dome")
    runMW(c, "pytest tests/unit_tests/logic/environment")
    runMW(c, "pytest tests/unit_tests/logic/filter")
    runMW(c, "pytest tests/unit_tests/logic/focuser")
    runMW(c, "pytest tests/unit_tests/logic/keypad")
    runMW(c, "pytest tests/unit_tests/logic/measure")
    runMW(c, "pytest tests/unit_tests/logic/modeldata")
    runMW(c, "pytest tests/unit_tests/logic/plateSolve")
    runMW(c, "pytest tests/unit_tests/logic/powerswitch")
    runMW(c, "pytest tests/unit_tests/logic/remote")
    runMW(c, "pytest tests/unit_tests/logic/telescope")
    runMW(c, "pytest tests/unit_tests/mountcontrol")
    printMW("testing mountwizzard finished\n")


@task(pre=[])
def pypiCleanup(c):
    printMW("...clean pypi from alpha versions")
    regex = "1\\.\\w*\\.\\d\\D\\d*$"
    runMW(c, f"pypi-cleanup -u mworion -p mountwizzard4 -r {regex} -y")


def test_windows(c, user, work, scp):
    printMW("...delete test dir")
    runMW(c, f'ssh {user} "if exist {work} rd /s /q {work}"')
    time.sleep(1)
    printMW("...make test dir")
    runMW(c, f'ssh {user} "if not exist {work} mkdir {work}"')
    time.sleep(1)

    with c.cd("dist"):
        printMW("...copy *.tar.gz to test dir")
        runMW(c, f"scp -r mountwizzard4.tar.gz {scp}")

    runMW(c, f'ssh {user} "cd {work} && echo > test.run"')
    runMW(c, f'ssh {user} "cd {work} && uv venv -p 3.13"')
    runMW(c, f'ssh {user} "cd {work} && uv pip install mountwizzard4.tar.gz"')
    runMW(c, f'ssh {user} "cd {work} && uv run mw4"')


def test_ubuntu(c, user, work, scp):
    printMW("...delete test dir")
    runMW(c, f'ssh {user} "rm -rf {work}"')
    time.sleep(1)
    printMW("...make test dir")
    runMW(c, f'ssh {user} "mkdir {work}"')
    time.sleep(1)

    with c.cd("dist"):
        printMW("...copy *.tar.gz to test dir")
        runMW(c, f"scp -r mountwizzard4.tar.gz {scp}")

    runMW(c, f'ssh {user} "cd {work} && echo > test.run"')
    runMW(c, f'ssh {user} "cd {work} && ~/.local/bin/uv venv -p 3.13"')
    runMW(c, f'ssh {user} "cd {work} && ~/.local/bin/uv pip install mountwizzard4.tar.gz"')
    runMW(c, f'ssh {user} "cd {work} && export DISPLAY=:0 && ~/.local/bin/uv run mw4"')


def test_mac(c, user, work, scp):
    printMW("...delete test dir")
    runMW(c, f'ssh {user} "rm -rf {work}"')
    time.sleep(1)
    printMW("...make test dir")
    runMW(c, f'ssh {user} "mkdir {work}"')
    time.sleep(1)

    with c.cd("dist"):
        printMW("...copy *.tar.gz to test dir")
        runMW(c, f"scp -r mountwizzard4.tar.gz {scp}")

    runMW(c, f'ssh {user} "cd {work} && echo > test.run"')
    runMW(c, f'ssh {user} "cd {work} && ~/.local/bin/uv venv -p 3.13"')
    runMW(c, f'ssh {user} "cd {work} && ~/.local/bin/uv pip install mountwizzard4.tar.gz"')
    runMW(c, f'ssh {user} "cd {work} && ~/.local/bin/uv run mw4"')


@task(pre=[])
def test_win10(c):
    printMW("test win10 install")
    user = client["win10"]["user"]
    work = client["win10"]["work"]
    scp = client["win10"]["scp"]
    test_windows(c, user, work, scp)
    printMW("test win10 install finished\n")


@task(pre=[])
def test_win11(c):
    printMW("test win11 install")
    user = client["win11"]["user"]
    work = client["win11"]["work"]
    scp = client["win11"]["scp"]
    test_windows(c, user, work, scp)
    printMW("test win11 install finished\n")


@task(pre=[])
def test_ubuntu20(c):
    printMW("test ubuntu20 install")
    user = client["ubuntu20"]["user"]
    work = client["ubuntu20"]["work"]
    scp = client["ubuntu20"]["scp"]
    test_ubuntu(c, user, work, scp)
    printMW("test ubuntu20 install finished\n")


@task(pre=[])
def test_ubuntu22(c):
    printMW("test ubuntu22 install")
    user = client["ubuntu22"]["user"]
    work = client["ubuntu22"]["work"]
    scp = client["ubuntu22"]["scp"]
    test_ubuntu(c, user, work, scp)
    printMW("test ubuntu22 install finished\n")


@task(pre=[])
def test_ubuntu24(c):
    printMW("test ubuntu24 install")
    user = client["ubuntu24"]["user"]
    work = client["ubuntu24"]["work"]
    scp = client["ubuntu24"]["scp"]
    test_ubuntu(c, user, work, scp)
    printMW("test ubuntu24 install finished\n")


@task(pre=[])
def test_astro_comp(c):
    printMW("test ubuntu rig install")
    user = client["ubuntuRig"]["user"]
    work = client["ubuntuRig"]["work"]
    scp = client["ubuntuRig"]["scp"]
    test_ubuntu(c, user, work, scp)
    printMW("test ubuntu rig install finished\n")


@task(pre=[])
def test_mac11(c):
    printMW("test mac11 install")
    user = client["mac11"]["user"]
    work = client["mac11"]["work"]
    scp = client["mac11"]["scp"]
    test_mac(c, user, work, scp)
    printMW("test mac11 install finished\n")


@task(pre=[])
def test_mac12(c):
    printMW("test mac12 install")
    user = client["mac12"]["user"]
    work = client["mac12"]["work"]
    scp = client["mac12"]["scp"]
    test_mac(c, user, work, scp)
    printMW("test mac12 install finished\n")


@task(pre=[])
def test_mac13(c):
    printMW("test mac13 install")
    user = client["mac13"]["user"]
    work = client["mac13"]["work"]
    scp = client["mac13"]["scp"]
    test_mac(c, user, work, scp)
    printMW("test mac13 install finished\n")


@task(pre=[])
def test_mac14(c):
    printMW("test mac14 install")
    user = client["mac14"]["user"]
    work = client["mac14"]["work"]
    scp = client["mac14"]["scp"]
    test_mac(c, user, work, scp)
    printMW("test mac14 install finished\n")


@task(pre=[])
def test_mac15(c):
    printMW("test mac15 install")
    user = client["mac15"]["user"]
    work = client["mac15"]["work"]
    scp = client["mac15"]["scp"]
    test_mac(c, user, work, scp)
    printMW("test mac15 install finished\n")


@task(pre=[])
def test_mac26(c):
    printMW("test mac26 install")
    user = client["mac26"]["user"]
    work = client["mac26"]["work"]
    scp = client["mac26"]["scp"]
    test_mac(c, user, work, scp)
    printMW("test mac26 install finished\n")


@task(pre=[build_resource, build_widgets])
def build_mw(c):
    printMW("building dist mountwizzard4")
    runMW(c, "rm -f dist/mountwizzard4*.tar.gz")
    runMW(c, "uv build")
    runMW(
        c,
        "cp dist/mountwizzard4*.tar.gz ../MountWizzard4/dist/mountwizzard4.tar.gz",
    )
    printMW("building dist mountwizzard4 finished\n")
    printMW("generating documentation")


@task(pre=[version_doc, build_mw])
def upload_mw(c):
    printMW("uploading dist mountwizzard4")
    with c.cd("./dist"):
        print(f'twine upload mountwizzard4-*.tar.gz')
        rn = "New major release !\nPlease do not update via internal updater!"
        runMW(c, f'twine upload mountwizzard4-*.tar.gz -r pypi -c "{rn}"')
    printMW("uploading dist mountwizzard4 finished\n")
