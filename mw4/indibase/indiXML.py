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
#
# original written by Hazen Babcock -> https://github.com/HazenBabcock/indi-python
# approved to be used with APL2.0 license via email from 04.11.2018:
#
# Hello Michael,
#
# No problem, you are welcome to use/re-use it in your code with an APL2.0
# license. I'm glad to hear that you found it useful.
#
# best,
# -Hazen
#
# based of the INDI protocol stack version 1.7
#
###########################################################
# standard libraries
import logging
import base64
import numbers

# external packages
import xml.etree.ElementTree as ETree

# local imports
log = logging.getLogger()
"""

An implementation of the INDI protocol - Copyright 2003-2007 Elwood Charles Downey

This module does 3 things:

(1) Given some XML as a string it will generate an object that
    represents the XML. This object has methods that can be
    used to inspect and manipulate the text and attributes of
    the XML represented by this object.

(2) Provide functions that generate the same objects as (1)
    given the appropriate arguments.

(3) Given an object created via (1) or (2) return it's
    corresponding XML string.

Notes:
 (1) To avoid Python keywords the following correspondence is used:
       'iformat' - 'format'
       'imin' - 'min'
       'imax' - 'max'

 (2) There are two forms of getProperties, deviceGetProperties() and clientGetProperties().

"""


class INDIBase(object):
    """
    INDI command base classes.
    """
    log = logging.getLogger(__name__)

    def __init__(self, etype, value, attr_dict, etree):
        self.etype = etype
        self.attr = {}

        if attr_dict is not None:
            for key in attr_dict:
                self.addAttr(key, attr_dict[key])
        elif etree is not None:
            self.etype = etree.tag
            for key in etree.attrib:
                self.addAttr(key, etree.attrib[key])
        else:
            self.log.critical("Dictionary of arguments or XML ETree required.")

    def __str__(self):
        if "name" in self.attr:
            base_str = self.etype + " (" + self.attr["name"]
            if "device" in self.attr:
                base_str += ", " + self.attr["device"]
            if "perm" in self.attr:
                base_str += ", " + self.attr["perm"]
            if "state" in self.attr:
                base_str += ", " + self.attr["state"]
            if "timeout" in self.attr:
                base_str += ", " + self.attr["timeout"]
            return base_str + ")"
        else:
            return self.etype + "()"

    def addAttr(self, name, value):
        self.attr[name] = value

    def delAttr(self, name):
        self.attr.pop(name)

    def getAttr(self, name):
        return self.attr[name]

    def setAttr(self, name, value):
        self.attr[name] = value

    def toETree(self):
        etree = ETree.Element(self.etype)

        # Add attributes.
        for key in self.attr:
            etree.set(key, str(self.attr[key]))
        return etree

    def toXML(self):
        return ETree.tostring(self.toETree(), 'utf-8')


class INDIElement(INDIBase):
    """
    INDI element command base class.
    """

    def __init__(self, etype, value, attr_dict, etree):
        INDIBase.__init__(self, etype, None, attr_dict, etree)
        self.value = value

        if etree is not None:
            self.value = ""
            if etree.text is not None:
                self.value = etree.text.strip()
            else:
                self.value = ''
                # self.log.error('Got None for {0}'.format(self.etype))

    def __str__(self):
        base_str = INDIBase.__str__(self)
        if "label" in self.attr:
            base_str += " '" + self.attr["label"] + "'"
        return base_str + " " + self.value

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.value = value

    def toETree(self):
        etree = INDIBase.toETree(self)
        etree.text = str(self.value)
        return etree


class INDIVector(INDIBase):
    """
    INDI vector command base class.
    """

    def __init__(self, etype, elt_list, attr_dict, etree):
        INDIBase.__init__(self, etype, None, attr_dict, etree)
        self.elt_list = elt_list

        if etree is not None:
            self.elt_list = []
            for node in etree:
                self.elt_list.append(parseETree(node))

    def __str__(self):
        elt_str = ""
        for elt in self.elt_list:
            elt_str += "  " + str(elt) + " "
        return INDIBase.__str__(self) + " " + elt_str

    def getElt(self, index):
        return self.elt_list[index]

    def getEltList(self):
        return self.elt_list

    def toETree(self):
        etree = INDIBase.toETree(self)
        for elt in self.elt_list:
            etree.append(elt.toETree())
        return etree


# Classes to represent the different commands.
class GetProperties(INDIBase):
    pass


class DefTextVector(INDIVector):
    pass


class DefText(INDIElement):
    pass


class DefNumberVector(INDIVector):
    pass


class DefNumber(INDIElement):
    pass


class DefSwitchVector(INDIVector):
    pass


class DefSwitch(INDIElement):
    pass


class DefLightVector(INDIVector):
    pass


class DefLight(INDIElement):
    pass


class DefBLOBVector(INDIVector):
    pass


class DefBLOB(INDIBase):
    pass


class SetTextVector(INDIVector):
    pass


class SetNumberVector(INDIVector):
    pass


class SetSwitchVector(INDIVector):
    pass


class SetLightVector(INDIVector):
    pass


class SetBLOBVector(INDIVector):
    pass


class Message(INDIBase):
    def __str__(self):
        if "message" in self.attr:
            return INDIBase.__str__(self) + " - " + self.attr["message"]
        else:
            return INDIBase.__str__(self) + " - empty message"


class DelProperty(INDIBase):
    pass


class OneLight(INDIElement):
    pass


class EnableBLOB(INDIElement):
    pass


class NewTextVector(INDIVector):
    pass


class NewNumberVector(INDIVector):
    pass


class NewSwitchVector(INDIVector):
    pass


class NewBLOBVector(INDIVector):
    pass


class OneText(INDIElement):
    pass


class OneNumber(INDIElement):
    pass


class OneSwitch(INDIElement):
    pass


class OneBLOB(INDIElement):
    def __init__(self, etype, value, attr_dict, etree):
        INDIElement.__init__(self, etype, None, attr_dict, etree)

        #
        # Convert value to bytes from base64 if this object
        # was created from XML from the indi server.
        #
        if etree is not None:
            self.value = base64.standard_b64decode(self.value)

    def __str__(self):
        return INDIBase.__str__(self) + " - " + self.attr["size"] + " - " + self.attr["format"]


#
# Validator functions.
#

def BLOBEnable(value):
    return value


def BLOBFormat(value):
    return value


def BLOBLength(value):
    return value


def BLOBValue(value):
    return value


def groupTag(value):
    return value


def labelValue(value):
    return value


def listValue(value):
    return value


def nameValue(value):
    return value


def numberFormat(value):
    return value


def numberValue(value):
    # Check if value is a number.
    if not isinstance(value, numbers.Number):
        log.error(str(value) + " is not a valid number.")
        return None
    return value


def propertyPerm(value):
    return value


def propertyState(value):
    return value


def switchRule(value):
    return value


def switchState(value):
    if isinstance(value, bool):
        if value:
            value = "On"

        else:
            value = "Off"

    if not value.lower() in ["on", "off"]:
        log.error(value + " is not a valid switch state.")
        return None

    return value


def timeValue(value):
    return value


def textValue(value):
    return value


#
# The INDI specification in a Pythonic form.
#
# Notes:
#
# 1. If the xml property is not specified it defaults to the specification key.
#
# 2. The structure of attribute element is [name, xml name (if different), required, validator, documentation].
#
indi_spec = {

    "getProperties": {
        "class": GetProperties,
        "xml": "getProperties"
    },

    # Commands from Device to Client.

    "deviceGetProperties": {
        "class": GetProperties,
        "xml": "getProperties",
        "docs": "Command to enable snooping messages from other devices. Once enabled, defXXX and setXXX messages for the Property with the given name and other messages from the device will be sent to this driver channel. Enables messages from all devices if device is not specified, and all Properties for the given device if name is not specified. Specifying name without device is not defined.",
        "attributes": [["device", None, False, nameValue, "device to snoop, or all if absent"],
                       ["name", None, False, nameValue, "property of device to snoop, or all if absent"]]
    },

    "defTextVector": {
        "class": DefTextVector,
        "docs": "Define a property that holds one or more text elements.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["label", None, False, labelValue, "GUI label, use name by default"],
                       ["group", None, False, groupTag, "Property group membership, blank by default"],
                       ["state", None, True, propertyState, "Current state of Property"],
                       ["perm", None, True, propertyPerm, "Ostensible Client controllability"],
                       ["timeout", None, False, numberValue, "Worse-case time to affect, 0 default, N/A for ro"],
                       ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                       ["message", None, False, textValue, "Commentary"]]
    },

    "defText": {
        "class": DefText,
        "docs": "Define one member of a text vector.",
        "arg": textValue,
        "attributes": [["name", None, True, nameValue, "Name of this text element"],
                       ["label", None, False, labelValue, "GUI label, or use name by default"]]
    },

    "defNumberVector": {
        "class": DefNumberVector,
        "docs": "Define a property that holds one or more numeric values.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["label", None, False, labelValue, "GUI label, use name by default"],
                       ["group", None, False, groupTag, "Property group membership, blank by default"],
                       ["state", None, True, propertyState, "Current state of Property"],
                       ["perm", None, True, propertyPerm, "Ostensible Client controllability"],
                       ["timeout", None, False, numberValue, "Worse-case time to affect, 0 default, N/A for ro"],
                       ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                       ["message", None, False, textValue, "Commentary"]]
    },

    "defNumber": {
        "class": DefNumber,
        "docs": "Define one member of a number vector.",
        "arg": numberValue,
        "attributes": [["name", None, True, nameValue, "Name of this text element"],
                       ["label", None, False, labelValue, "GUI label, or use name by default"],
                       ["iformat", "format", True, numberFormat, "print() style format for GUI display"],
                       ["imin", "min", True, numberValue, "Minimal value"],
                       ["imax", "max", True, numberValue, "Maximal value, ignore if min == max"],
                       ["step", None, True, numberValue, "Allowed increments, ignore if 0"]]
    },

    "defSwitchVector": {
        "class": DefSwitchVector,
        "docs": "Define a collection of switches. Rule is only a hint for use by a GUI to decide a suitable presentation style. Rules are actually implemented wholly within the Device.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["label", None, False, labelValue, "GUI label, use name by default"],
                       ["group", None, False, groupTag, "Property group membership, blank by default"],
                       ["state", None, True, propertyState, "Current state of Property"],
                       ["perm", None, True, propertyPerm, "Ostensible Client controlability"],
                       ["rule", None, True, switchRule, "Hint for GUI presentation"],
                       ["timeout", None, False, numberValue, "Worse-case time to affect, 0 default, N/A for ro"],
                       ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                       ["message", None, False, textValue, "Commentary"]]
    },

    "defSwitch": {
        "class": DefSwitch,
        "docs": "Define one member of a text vector.",
        "arg": switchState,
        "attributes": [["name", None, True, nameValue, "Name of this text element"],
                       ["label", None, False, labelValue, "GUI label, or use name by default"]]
    },

    "defLightVector": {
        "class": DefLightVector,
        "docs": "Define a collection of passive indicator lights.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["label", None, False, labelValue, "GUI label, use name by default"],
                       ["group", None, False, groupTag, "Property group membership, blank by default"],
                       ["state", None, True, propertyState, "Current state of Property"],
                       ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                       ["message", None, False, textValue, "Commentary"]]
    },

    "defLight": {
        "class": DefLight,
        "docs": "Define one member of a light vector.",
        "arg": propertyState,
        "attributes": [["name", None, True, nameValue, "Name of this text element"],
                       ["label", None, False, labelValue, "GUI label, or use name by default"]]
    },

    "defBLOBVector": {
        "class": DefBLOBVector,
        "docs": "Define a property that holds one or more Binary Large Objects, BLOBs.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["label", None, False, labelValue, "GUI label, use name by default"],
                       ["group", None, False, groupTag, "Property group membership, blank by default"],
                       ["state", None, True, propertyState, "Current state of Property"],
                       ["perm", None, True, propertyPerm, "Ostensible Client controlability"],
                       ["timeout", None, False, numberValue, "Worse-case time to affect, 0 default, N/A for ro"],
                       ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                       ["message", None, False, textValue, "Commentary"]]
    },

    "defBLOB": {
        "class": DefBLOB,
        "docs": "Define one member of a BLOB vector. Unlike other defXXX elements, this does not contain an initial value for the BLOB.",
        "attributes": [["name", None, True, nameValue, "Name of this text element"],
                       ["label", None, False, labelValue, "GUI label, or use name by default"]]
    },

    "setTextVector": {
        "class": SetTextVector,
        "docs": "Send a new set of values for a Text vector, with optional new timeout, state and message.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["state", None, False, propertyState, "State, no change if absent"],
                       ["timeout", None, False, numberValue, "Worse-case time to affect a change"],
                       ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                       ["message", None, False, textValue, "Commentary"]]
    },

    "setNumberVector": {
        "class": SetNumberVector,
        "docs": "Send a new set of values for a Number vector, with optional new timeout, state and message.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["state", None, False, propertyState, "State, no change if absent"],
                       ["timeout", None, False, numberValue, "Worse-case time to affect a change"],
                       ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                       ["message", None, False, textValue, "Commentary"]]
    },

    "setSwitchVector": {
        "class": SetSwitchVector,
        "docs": "Send a new set of values for a Switch vector, with optional new timeout, state and message.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["state", None, False, propertyState, "State, no change if absent"],
                       ["timeout", None, False, numberValue, "Worse-case time to affect a change"],
                       ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                       ["message", None, False, textValue, "Commentary"]]
    },

    "setLightVector": {
        "class": SetLightVector,
        "docs": "Send a new set of values for a Light vector, with optional new state and message.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["state", None, False, propertyState, "State, no change if absent"],
                       ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                       ["message", None, False, textValue, "Commentary"]]
    },

    "setBLOBVector": {
        "class": SetBLOBVector,
        "docs": "Send a new set of values for a BLOB vector, with optional new timeout, state and message.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["state", None, False, propertyState, "State, no change if absent"],
                       ["timeout", None, False, numberValue, "Worse-case time to affect a change"],
                       ["timestamp", None, False, timeValue, "Moment when these data were valid"],
                       ["message", None, False, textValue, "Commentary"]]
    },

    "message": {
        "class": Message,
        "docs": "Send a message associated with a device or entire system.",
        "attributes": [["device", None, True, nameValue, "Considered to be site-wide if absent"],
                       ["timestamp", None, False, timeValue, "Moment when this message was generated"],
                       ["message", None, False, textValue, "Commentary"]]
    },

    "delProperty": {
        "class": DelProperty,
        "docs": "Delete the given property, or entire device if no property is specified.",
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, False, nameValue, "Entire device if absent"],
                       ["timestamp", None, False, timeValue, "Moment when this delete was generated"],
                       ["message", None, False, textValue, "Commentary"]]
    },

    "oneLight": {
        "class": OneLight,
        "docs": "Send a message to specify state of one member of a Light vector.",
        "arg": propertyState,
        "attributes": [["name", None, True, nameValue, "Name of this light element"]]
    },

    # Commands from Client to Device.

    "clientGetProperties": {
        "class": GetProperties,
        "xml": "getProperties",
        "docs": "Command to ask Device to define all Properties, or those for a specific Device or specific Property, for which it is responsible. Must always include protocol version.",
        "attributes": [["version", None, True, nameValue, "protocol version"],
                       ["device", None, False, nameValue, "device to snoop, or all if absent"],
                       ["name", None, False, nameValue, "property of device to snoop, or all if absent"]]
    },

    "enableBLOB": {
        "class": EnableBLOB,
        "docs": "Command to control whether setBLOBs should be sent to this channel from a given Device. They can be turned off completely by setting Never (the default), allowed to be intermixed with other INDI commands by setting Also or made the only command by setting Only.",
        "arg": BLOBEnable,
        "attributes": [["device", None, False, labelValue, "Name of Device"],
                       ["name", None, False, labelValue, "Name of BLOB Property, or all if absent"]]
    },

    "newTextVector": {
        "class": NewTextVector,
        "docs": "Send new target text values.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["timestamp", None, False, timeValue, "Moment when this message was generated"]]
    },

    "newNumberVector": {
        "class": NewNumberVector,
        "docs": "Send new target numeric values.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["timestamp", None, False, timeValue, "Moment when this message was generated"]]
    },

    "newSwitchVector": {
        "class": NewSwitchVector,
        "docs": "Send new target switch states.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["timestamp", None, False, timeValue, "Moment when this message was generated"]]
    },

    "newBLOBVector": {
        "class": NewBLOBVector,
        "docs": "Send new target BLOBS.",
        "arg": listValue,
        "attributes": [["device", None, True, nameValue, "Name of Device"],
                       ["name", None, True, nameValue, "Name of Property"],
                       ["timestamp", None, False, timeValue, "Moment when this message was generated"]]
    },

    # Elements describing a vector member value, used in both directions.

    "oneText": {
        "class": OneText,
        "docs": "One member of a text vector.",
        "arg": textValue,
        "attributes": [["name", None, True, nameValue, "Name of this text element"]]
    },

    "oneNumber": {
        "class": OneNumber,
        "docs": "One member of a number vector.",
        "arg": numberValue,
        "attributes": [["name", None, True, nameValue, "Name of this number element"]]
    },

    "oneSwitch": {
        "class": OneSwitch,
        "docs": "One member of a switch vector.",
        "arg": switchState,
        "attributes": [["name", None, True, nameValue, "Name of this switch element"]]
    },

    "oneBLOB": {
        "class": OneBLOB,
        "docs": "One member of a BLOB vector. The contents of this element must always be encoded using base64. The format attribute consists of one or more file name suffixes, each preceded with a period, which indicate how the decoded data is to be interpreted. For example .fits indicates the decoded BLOB is a FITS file, and .fits.z indicates the decoded BLOB is a FITS file compressed with zlib. The INDI protocol places no restrictions on the contents or formats of BLOBs but at minimum astronomical INDI clients are encouraged to support the FITS image file format and the zlib compression mechanism. The size attribute indicates the number of bytes in the final BLOB after decoding and after any decompression. For example, if the format is .fits.z the size attribute is the number of bytes in the FITS file. A Client unfamiliar with the specified format may use the attribute as a simple string, perhaps in combination with the timestamp attribute, to create a file name in which to store the data without processing other than decoding the base64.",
        "arg": BLOBValue,
        "attributes": [["name", None, True, nameValue, "Name of this BLOB element"],
                       ["size", None, True, BLOBLength, "Number of bytes in decoded and uncompressed BLOB"],
                       ["iformat", "format", True, BLOBFormat, "Format as a file suffix, eg: .z, .fits, .fits.z"]]
    },

}


def makeINDIFn(indi_type):
    """
    Returns an INDI function of the requested type.
    """
    global indi_spec

    # Check that the requested type exists.
    if indi_type not in indi_spec:
        log.critical(indi_type + " is not a valid INDI XML command type.")
        return

    type_spec = indi_spec[indi_type]

    # Use indi_type as the XML element type, unless otherwise specified.
    if "xml" not in type_spec:
        type_spec["xml"] = indi_type

    # Function to make the object.
    def makeObject(fn_arg, fn_attr):

        # Check attributes against those in the specification.
        all_attr = []
        final_attr = {}
        for attr in type_spec["attributes"]:
            attr_name = attr[0]
            all_attr.append(attr_name)

            # Check if required.
            if attr[2] and attr_name not in fn_attr:
                log.critical(attr_name + " is a required attribute.")
                return

            # Check if valid.
            if attr_name in fn_attr:
                if attr[1] is None:
                    attr[1] = attr[0]
                final_attr[attr[1]] = attr[3](fn_attr[attr_name])

        # Check that there are no extra attributes.
        for attr in fn_attr:
            if attr not in all_attr:
                log.critical(attr + " is not an attribute of " + indi_type + ".")
                return

        # Make an INDI object of this class.
        return type_spec["class"](type_spec["xml"], fn_arg, final_attr, None)

    # Check if an argument was expected.
    if "arg" in type_spec:

        def ifunction(arg, indi_attr=None):

            # Check argument with validator function.
            arg = type_spec["arg"](arg)

            # Create object.
            return makeObject(arg, indi_attr)

    else:

        def ifunction(indi_attr=None):

            # Create object.
            return makeObject(None, indi_attr)

    # Manipulate some properties of the function so that help, etc. is clearer.
    ifunction.__name__ = indi_type
    ifunction.__doc__ = type_spec["docs"]  # todo: Add arguments dictionary.

    return ifunction


#
# The API
#


# XML parsing of incoming commands.

def parseETree(etree):
    type_spec = indi_spec[etree.tag]
    return type_spec["class"](type_spec["xml"], None, None, etree)


# Create the functions for generating INDI command objects.

deviceGetProperties = makeINDIFn("deviceGetProperties")
defTextVector = makeINDIFn("defTextVector")
defText = makeINDIFn("defText")
defNumberVector = makeINDIFn("defNumberVector")
defNumber = makeINDIFn("defNumber")
defSwitchVector = makeINDIFn("defSwitchVector")
defSwitch = makeINDIFn("defSwitch")
defLightVector = makeINDIFn("defLightVector")
defLight = makeINDIFn("defLight")
defBLOBVector = makeINDIFn("defBLOBVector")
defBLOB = makeINDIFn("defBLOB")
setTextVector = makeINDIFn("setTextVector")
setNumberVector = makeINDIFn("setNumberVector")
setSwitchVector = makeINDIFn("setSwitchVector")
setLightVector = makeINDIFn("setLightVector")
setBLOBVector = makeINDIFn("setBLOBVector")
message = makeINDIFn("message")
delProperty = makeINDIFn("delProperty")
oneLight = makeINDIFn("oneLight")

clientGetProperties = makeINDIFn("clientGetProperties")
enableBLOB = makeINDIFn("enableBLOB")
newTextVector = makeINDIFn("newTextVector")
newNumberVector = makeINDIFn("newNumberVector")
newSwitchVector = makeINDIFn("newSwitchVector")
newBLOBVector = makeINDIFn("newBLOBVector")

oneText = makeINDIFn("oneText")
oneNumber = makeINDIFn("oneNumber")
oneSwitch = makeINDIFn("oneSwitch")
oneBLOB = makeINDIFn("oneBLOB")
