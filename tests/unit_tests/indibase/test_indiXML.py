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
# written in python3 , (c) 2019, 2020 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
import xml.etree.ElementTree as ETree

# local import
from indibase.indiXML import *
from indibase import indiXML


@pytest.fixture(autouse=True, scope='function')
def function():
    yield function


def test_IndiXMLException(function):
    IndiXMLException('test')


def test_INDIBase_1(function):
    INDIBase('defLight', [], {'name': 'test'}, None)


def test_INDIBase_2(function):
    class ET:
        tag = 'testtag'
        attrib = {'testtag': 'testattrib'}
    INDIBase('defLight', [], None, ET())


def test_INDIBase_3(function):
    INDIBase('defLight', [], None, None)


def test_INDIBase_4(function):
    class ET:
        tag = 'testtag'
        attrib = {'testtag': 'testattrib'}

    test = INDIBase("defLight", [], None, ET())
    f'{test}'


def test_INDIBase_5(function):
    class ET:
        tag = 'testtag'
        attrib = {'testtag': 'testattrib'}

    test = INDIBase("defLight", [], None, ET())
    test.attr = {'name': 'test',
                 'device': 'test',
                 'perm': 'test',
                 'state': 'test',
                 'timeout': '10'}
    f'{test}'


def test_INDIBase_6(function):
    class ET:
        tag = 'testtag'
        attrib = {'testtag': 'testattrib'}

    test = INDIBase("defLight", [], None, ET())
    test.addAttr('test', 'test')
    val = test.getAttr('test')
    assert val == 'test'


def test_INDIBase_7(function):
    class ET:
        tag = 'testtag'
        attrib = {'testtag': 'testattrib'}

    test = INDIBase("defLight", [], None, ET())
    test.addAttr('test', 'test')
    test.delAttr('test')
    assert 'test' not in test.attr


def test_INDIBase_8(function):
    class ET:
        tag = 'testtag'
        attrib = {'testtag': 'testattrib'}

    test = INDIBase("defLight", [], None, ET())
    test.addAttr('test', 'test')
    test.setAttr('test', 'testnew')
    val = test.getAttr('test')
    assert val == 'testnew'


def test_INDIBase_9(function):
    class ET:
        tag = 'testtag'
        attrib = {'testtag': 'testattrib'}

    test = INDIBase("defLight", [], None, ET())
    test.attr = {'name': 'test',
                 'device': 'test',
                 'perm': 'test',
                 'state': 'test',
                 'timeout': '10'}

    test.toETree()
    test.toXML()


def test_INDIElement_1(function):
    class ET:
        tag = 'testtag'
        attrib = {'testtag': 'testattrib'}
        text = '  test value  '

    a = {'name': 'test',
         'device': 'test',
         'perm': 'test',
         'state': 'test',
         'timeout': '10',
         'label': 'label'}

    test = INDIElement("defLight", 'On', a, ET())
    f'{test}'


def test_INDIElement_2(function):
    class ET:
        tag = 'testtag'
        attrib = {'testtag': 'testattrib'}
        text = None

    a = {'name': 'test',
         'device': 'test',
         'perm': 'test',
         'state': 'test',
         'timeout': '10',
         'label': 'label'}

    test = INDIElement("defLight", 'On', a, ET())
    test.setValue('On')
    val = test.getValue()
    assert val == 'On'
    test.toETree()


def test_INDIVector_1(function):
    class ET:
        tag = 'defLight'
        attrib = {'testtag': 'testattrib'}
        text = '  test value  '

    a = {'name': 'test',
         'device': 'test',
         'perm': 'test',
         'state': 'test',
         'timeout': '10',
         'label': 'label'}

    test = INDIVector("defLight", [], a, [ET()])
    f'{test}'


def test_INDIVector_2(function):
    class ET:
        tag = 'defLight'
        attrib = {'testtag': 'testattrib'}
        text = '  test value  '

    a = {'name': 'test',
         'device': 'test',
         'perm': 'test',
         'state': 'test',
         'timeout': '10',
         'label': 'label'}

    test = INDIVector("defLight", [], a, [ET()])
    test.getElt(0)
    test.getEltList()
    test.toETree()


def test_Message_1(function):
    class ET:
        tag = 'defLight'
        attrib = {'testtag': 'testattrib'}
        text = '  test value  '

    a = {'name': 'test',
         'device': 'test',
         'perm': 'test',
         'state': 'test',
         'timeout': '10',
         'label': 'label'}

    test = Message("defLight", None, a, ET())
    assert f'{test}' == 'defLight (test, test, test, test, 10) - empty message'


def test_Message_2(function):
    class ET:
        tag = 'defLight'
        attrib = {'testtag': 'testattrib'}
        text = '  test value  '

    a = {'name': 'test',
         'device': 'test',
         'perm': 'test',
         'state': 'test',
         'timeout': '10',
         'label': 'label',
         'message': 'testmessage'}

    test = Message("defLight", None, a, ET())
    assert f'{test}' == 'defLight (test, test, test, test, 10) - testmessage'


def test_OneBLOB_1(function):
    class ET:
        tag = 'defLight'
        attrib = {'testtag': 'testattrib'}
        text = '  test value  '

    a = {'name': 'test',
         'device': 'test',
         'perm': 'test',
         'state': 'test',
         'timeout': '10',
         'label': 'label',
         'size': '100',
         'format': 'b64',
         'message': 'testmessage'}

    val = base64.standard_b64encode(b'1234567890')

    test = OneBLOB("defBLOB", val, a, ET())
    f'{test}'
