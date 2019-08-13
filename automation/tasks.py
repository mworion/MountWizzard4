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
import sys
sys.path.append('/Users/mw/PycharmProjects/MountWizzard4')
from invoke import task, context, Collection
from automation.collections.gui import printMW, runMW

from automation.collections import clean
from automation.collections import venv
from automation.collections import support
from automation.collections import test
from automation.collections import run_app
from automation.collections import run_dist
from automation.collections import deploy_dist
from automation.collections import build_dmg
from automation.collections import build_app
from automation.collections import build_dist
#
# build collections
#
ns = Collection()
#
# adding external collections
#
ns.add_collection((Collection.from_module(clean)))
ns.add_collection((Collection.from_module(venv)))
ns.add_collection((Collection.from_module(support)))
ns.add_collection((Collection.from_module(test)))
ns.add_collection((Collection.from_module(run_app)))
ns.add_collection((Collection.from_module(run_dist)))
ns.add_collection((Collection.from_module(deploy_dist)))
ns.add_collection((Collection.from_module(build_dmg)))
ns.add_collection((Collection.from_module(build_app)))
ns.add_collection((Collection.from_module(build_dist)))


@task(pre=[])
def clean_all(c):
    printMW('clean all')
    clean.mountcontrol(c)
    clean.indibase(c)
    clean.mountwizzard(c)


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


#
# adding local ones
#
ns.add_task(clean_all)
ns.add_task(venv_all)
ns.add_task(test_all)
ns.add_task(build_all)
ns.add_task(deploy_all)
ns.add_task(run_all)
