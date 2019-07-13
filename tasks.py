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


@task()
def clean():
    print('clean')
    pass


@task()
def resource(c):
    print('building resources')
    pass


@task():
def test(c):
    print('testing')
    pass


@task(pre=[clean, resource, test]):
def build(c):
    print('building dist')
    print('building mac')
    pass


@task(pre=[build])
def deploy(c):
    print('deploy dist')
    print('deploy mac')
    pass