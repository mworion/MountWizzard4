############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import time
from invoke import task

rn = ""
#
# defining all necessary virtual client login for building over all platforms
#

client = {
    "ubuntu26": {
        "user": "mw@astro-ubuntu26.uranus",
        "work": "/home/mw/test",
        "scp": "mw@astro-ubuntu26.uranus:/home/mw/test",
    },
    "astrocomp": {
        "user": "mw@astro-comp.uranus",
        "work": "/home/mw/test",
        "scp": "mw@astro-comp.uranus:/home/mw/test",
    },
    "win11": {
        "user": "mw@astro-win11.uranus",
        "work": "test",
        "scp": "mw@astro-win11.uranus:/Users/mw/test",
    },
}


def runMW(c, param):
    c.run(param)


def printMW(param):
    pass


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
def update_builtins(c):
    printMW("updating builtins")
    runMW(c, "cp ./work/data/de440_mw4.bsp ./src/mw4/assets/data/de440_mw4.bsp")
    runMW(c, "cp ./work/data/finals2000A.all ./src/mw4/assets/data/finals2000A.all")
    runMW(c, "cp ./work/data/finals.data ./src/mw4/assets/data/finals.data")
    runMW(c, "cp ./work/data/CDFLeapSeconds.txt ./src/mw4/assets/data/CDFLeapSeconds.txt")
    printMW("updating builtins finished\n")


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
        "satelliteHor",
        "satelliteMap",
        "simulator",
        "setting",
        "video",
        "uploadPopup",
        "material",
    ]
    for widget in widgets:
        nameIn = widgetDirIn + widget
        nameOut = widgetDirOut + widget
        runMW(c, f"uv run pyside6-uic {nameIn}.ui > {nameOut}_ui.py")
    printMW("building widgets finished\n")


@task(pre=[build_widgets, update_builtins])
def build(c):
    printMW("building dist mountwizzard4")
    runMW(c, "rm -f dist/*.tar.gz")
    runMW(c, "uv build")
    runMW(
        c,
        "cp dist/mountwizzard4*.tar.gz ../MountWizzard4/dist/mountwizzard4.tar.gz",
    )
    printMW("building dist mountwizzard4 finished\n")


@task(pre=[build])
def build_test(c):
    printMW("build mountwizzard4")
    runMW(c, "rm -f dist/*.tar.gz")
    runMW(c, "uv build")
    runMW(
        c,
        "cp dist/mountwizzard4*.tar.gz ../MountWizzard4/dist/mountwizzard4.tar.gz",
    )
    printMW("build-test mountwizzard4 finished\n")


@task(pre=[build])
def publish(c):
    printMW("publishing mountwizzard4")
    runMW(c, "rm -f dist/*.tar.gz")
    runMW(c, "uvx uv-publish")
    printMW("publishing mountwizzard4 finished\n")


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

    runMW(c, f'ssh {user} "cd {work} && uv venv -p 3.13"')
    runMW(c, f'ssh {user} "cd {work} && uv pip install mountwizzard4.tar.gz"')
    runMW(c, f'ssh {user} "cd {work} && uv run mw4 -t 1"')


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

    runMW(c, f'ssh {user} "cd {work} && ~/.local/bin/uv venv -p 3.13"')
    runMW(c, f'ssh {user} "cd {work} && ~/.local/bin/uv pip install mountwizzard4.tar.gz"')
    runMW(c, f'ssh {user} "cd {work} &&  DISPLAY=:0 ~/.local/bin/uv run mw4 -t 1"')

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

    runMW(c, f'ssh {user} "cd {work} && ~/.local/bin/uv venv -p 3.13"')
    runMW(c, f'ssh {user} "cd {work} && ~/.local/bin/uv pip install mountwizzard4.tar.gz"')
    runMW(c, f'ssh {user} "cd {work} && ~/.local/bin/uv run mw4 -t 1"')


@task(pre=[])
def test_win11(c):
    printMW("test win11 install")
    user = client["win11"]["user"]
    work = client["win11"]["work"]
    scp = client["win11"]["scp"]
    test_windows(c, user, work, scp)
    printMW("test win11 install finished\n")


@task(pre=[])
def test_ubuntu26(c):
    printMW("test ubuntu26 install")
    user = client["ubuntu26"]["user"]
    work = client["ubuntu26"]["work"]
    scp = client["ubuntu26"]["scp"]
    test_ubuntu(c, user, work, scp)
    printMW("test ubuntu26 install finished\n")


@task(pre=[])
def test_astrocomp(c):
    printMW("test astrocomp install")
    user = client["astrocomp"]["user"]
    work = client["astrocomp"]["work"]
    scp = client["astrocomp"]["scp"]
    test_ubuntu(c, user, work, scp)
    printMW("test astrocomp install finished\n")


@task(pre=[])
def test_mac26(c):
    printMW("test mac26 install")
    user = client["mac26"]["user"]
    work = client["mac26"]["work"]
    scp = client["mac26"]["scp"]
    test_mac(c, user, work, scp)
    printMW("test mac26 install finished\n")
