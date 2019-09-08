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
import platform

if platform.system() == 'Darwin':
    sys.path.append('/Users/mw/PycharmProjects/MountWizzard4')
else:
    sys.path.append('/home/mw/PycharmProjects/MountWizzard4')

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
    venv.mac(c)
    venv.ubuntu(c)
    venv.windows(c)
    venv.work(c)


@task(pre=[])
def test_all(c):
    printMW('test all')
    test.mountcontrol(c)
    test.mountwizzard(c)


@task(pre=[])
def build_all(c):
    printMW('build all')
    support.resource(c)
    support.widgets(c)
    build_dist.mountcontrol(c)
    build_dist.indibase(c)
    build_dist.mountwizzard(c)
    build_app.windows(c)
    build_app.windows_dbg(c)
    build_app.mac(c)


@task(pre=[])
def deploy_all(c):
    printMW('deploy all')
    deploy_dist.ubuntu(c)
    deploy_dist.mate(c)
    deploy_dist.windows(c)
    deploy_dist.windows_dbg(c)
    deploy_dist.mac(c)


@task(pre=[])
def run_all(c):
    printMW('run all')
    run_dist.ubuntu(c)
    run_dist.mate(c)
    run_dist.windows(c)
    run_app.windows(c)
    run_app.windows_dbg(c)
    run_dist.mac(c)
    run_app.mac(c)


#
# adding local ones
#
ns.add_task(clean_all)
ns.add_task(venv_all)
ns.add_task(test_all)
ns.add_task(build_all)
ns.add_task(deploy_all)
ns.add_task(run_all)
