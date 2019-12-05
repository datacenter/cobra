# *************************************************************************
# Copyright (c) 2013 Cisco Systems, Inc.  All rights reserved.
# *************************************************************************

import sys
if sys.version_info[0] == 3:
    from builtins import str

import xml.etree.cElementTree as ET
import xml.dom.minidom
from ._loader import ClassLoader
from ._codec_utils import parseMoClassName, getParentDn, listWithTotalCount


def parseXMLError(rspStr, errorClass, httpCode=None):
    errorNode = ET.fromstring(rspStr).find('error')
    if errorNode is not None:
        errorStr = errorNode.attrib['text']
        errorCode = errorNode.attrib['code']
        raise errorClass(int(errorCode), errorStr, httpCode)

    raise ValueError(rspStr)


def _fromXMLRootNode(xmlRootNode):
    allMos = listWithTotalCount()
    allMos.totalCount = int(xmlRootNode.attrib['totalCount'])
    for moNode in xmlRootNode:
        mo = _createMo(moNode, None)
        allMos.append(mo)
    return allMos


def fromXMLStr(xmlStr, tree_only=False):
    xmlRootNode = ET.fromstring(xmlStr)
    return _fromXMLRootNode(xmlRootNode) if not tree_only else xmlRootNode


def fromXMLStream(xmlStream, tree_only=False):
    # Remove the children and add it from the fetch data set
    xmlRootNode = ET.parse(xmlStream).getroot()
    return _fromXMLRootNode(xmlRootNode) if not tree_only else xmlRootNode


def _createMo(node, parentMo):
    pkgName, className = parseMoClassName(node.tag)
    fqClassName = "cobra.model." + pkgName + "." + className
    pyClass = ClassLoader.loadClass(fqClassName)
    parentDnStr = None
    moProps = {}
    for attr, val in list(node.attrib.items()):
        if attr == 'dn':
            # Set the dn of this MO from the data returned by server
            parentDnStr = getParentDn(str(val))
        elif attr == 'rn' or attr == 'instanceId':
            pass
        elif attr == 'status' and not val:
            pass
        else:
            moProps[attr] = str(val)

    namingVals = []
    for propMeta in pyClass.meta.namingProps:
        propName = propMeta.moPropName
        namingVals.append(moProps[propName])
        del moProps[propName]

    parentMoOrDn = parentMo if parentMo else parentDnStr
    mo = pyClass(parentMoOrDn, *namingVals, markDirty=False, **moProps)
    mo.resetProps()

    for childNode in node:
        _createMo(childNode, mo)

    return mo


def toXMLStr(mo, includeAllProps=False, prettyPrint=False, excludeChildren=False):
    xmlString = _toXMLStr(mo, includeAllProps, excludeChildren)
    xmlHeader = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xmlStr = xmlHeader + xmlString
    if prettyPrint and xmlString:
        tmp = xml.dom.minidom.parseString(xmlStr)
        xmlStr = tmp.toprettyxml(indent='  ')
    return xmlStr


def _toXMLStr(mo, includeAllProps, excludeChildren=False):
    def encodeValue(xmlValue):
        newValue = []
        for xmlChar in xmlValue:
            if xmlChar == '&':
                newValue.append('&amp;')
            elif xmlChar == '"':
                newValue.append('&quot;')
            elif xmlChar == "'":
                newValue.append('&apos;')
            elif xmlChar == ">":
                newValue.append('&gt;')
            elif xmlChar == "<":
                newValue.append('&lt;')
            else:
                newValue.append(xmlChar)
        return ''.join(newValue)

    meta = mo.meta
    className = meta.moClassName

    # Create the attribute string
    attrStr = ""
    for propMeta in meta.props:
        name = propMeta.name
        moPropName = propMeta.moPropName
        value = None
        if propMeta.isDn:
            if includeAllProps:
                value = str(mo.dn)
        elif propMeta.isRn:
            if includeAllProps:
                value = str(mo.rn)
        elif (propMeta.isNaming or includeAllProps or
                mo.isPropDirty(name)):
            value = getattr(mo, name)
        if value is not None:
            value = encodeValue(str(value))
            attrStr = attrStr + " {0}='{1}'".format(moPropName, value)

    childXml = ""
    if not excludeChildren:
        for childMo in mo.children:
            childXml += _toXMLStr(childMo, includeAllProps, excludeChildren)

    xmlStr = ""
    if attrStr or childXml:
        xmlStr = "<{0}{1}>{2}</{3}>".format(className, attrStr, childXml,
                                                className)

    return xmlStr
