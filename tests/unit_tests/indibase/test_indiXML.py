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
# standard libraries
import pytest
import unittest.mock as mock
import builtins

# external packages
import xml.etree.ElementTree as ETree

# local import
from indibase.indiXML import *
from indibase import indiXML


@pytest.fixture(autouse=True, scope='function')
def function():
    yield function


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
        text = base64.standard_b64encode(b'AAAA')

    a = {'name': 'test',
         'device': 'test',
         'perm': 'test',
         'state': 'test',
         'timeout': '10',
         'label': 'label',
         'size': '100',
         'format': 'b64',
         'message': 'testmessage'}

    test = OneBLOB("defBLOB", None, a, ET())
    f'{test}'


def test_BLOBEnable(function):
    val = BLOBEnable(10)
    assert val == 10


def test_BLOBFormat(function):
    val = BLOBFormat(10)
    assert val == 10


def test_BLOBLength(function):
    val = BLOBLength(10)
    assert val == 10


def test_BLOBValue(function):
    val = BLOBValue(10)
    assert val == 10


def test_groupTag(function):
    val = groupTag(10)
    assert val == 10


def test_labelValue(function):
    val = labelValue(10)
    assert val == 10


def test_listValue(function):
    val = listValue(10)
    assert val == 10


def test_nameValue(function):
    val = nameValue(10)
    assert val == 10


def test_numberFormat(function):
    val = numberFormat(10)
    assert val == 10


def test_numberValue_1(function):
    val = numberValue(10)
    assert val == 10


def test_numberValue_2(function):
    val = numberValue('a')
    assert val is None


def test_propertyPerm(function):
    val = propertyPerm(10)
    assert val == 10


def test_propertyState(function):
    val = propertyState(10)
    assert val == 10


def test_switchRule(function):
    val = switchRule(10)
    assert val == 10


def test_switchState_1(function):
    val = switchState(True)
    assert val == 'On'


def test_switchState_2(function):
    val = switchState(False)
    assert val == 'Off'


def test_switchState_3(function):
    val = switchState('test')
    assert val is None


def test_timeValue(function):
    val = timeValue(10)
    assert val == 10


def test_textValue(function):
    val = textValue(10)
    assert val == 10


def test_makeINDIFn_1(function):
    makeINDIFn('test')


def test_makeINDIFn_2(function):
    makeObj = makeINDIFn('defTextVector')
    makeObj('device', 'test')


def test_makeINDIFn_3(function):
    makeObj = makeINDIFn('defTextVector')
    makeObj('device', {'device': 'test', 'name': 'test'})


def test_makeINDIFn_4(function):
    makeObj = makeINDIFn('defTextVector')
    makeObj('test', {'device': 'test', 'test': 'test'})
