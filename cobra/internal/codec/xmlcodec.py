# Copyright 2015 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The ACI Python SDK json codec module."""

from builtins import str  # pylint:disable=redefined-builtin

import xml.etree.cElementTree as ET
import xml.dom.minidom
from cobra.mit.meta import ClassLoader
from cobra.internal.codec import (parseMoClassName, getParentDn, buildMo,
                                  getPropValue)


def parseXMLError(rspStr, errorClass, httpCode=None):
    """Parse an error in a XML response.

    This method takes a string and uses the cElementTree module to parse it
    for the error code and error string.

    Args:
      rspText (str): The response as a string
      errorClass (Exception): The exception that should be called when the
        error is parsed.  If set to None, a ValueError will be raised.
      httpCode (int, optional): The http error code that indicated an error
        occurred.

    Raises:
        Exception: If the errorClass is set, the type of exception it is set
          to will be raised.
        ValueError: If the response can not be parsed.
    """

    errorNode = ET.fromstring(rspStr).find('error')
    if errorNode is not None:
        errorStr = errorNode.attrib['text']
        errorCode = errorNode.attrib['code']
        raise errorClass(int(errorCode), errorStr, httpCode)

    raise ValueError(rspStr)


def _fromXMLRootNode(xmlRootNode):
    """Parse a cElementTree.Element object into Mo's.

    Args:
      xmlRootNode (xml.etree.ElementTree.Element): The root node element
        object.

    Returns:
      cobra.mit.mo.Mo: The Mo parsed from the XML Element object.

    """
    allMos = []
    for moNode in xmlRootNode:
        mo = _createMo(moNode, None)
        allMos.append(mo)
    return allMos


def fromXMLStr(xmlStr):
    """Create a Mo from a XML string.

    This method does cElementTree.fromstring on the XML string and passes the
    resulting object on to _fromXMLRootNode.

    Args:
      xmlStr (str): The XML string representing a Mo.

    Returns:
      cora.mit.mo.Mo: The Mo represented by the XML string.
    """
    xmlRootNode = ET.fromstring(xmlStr)
    return _fromXMLRootNode(xmlRootNode)


def fromXMLStream(xmlStream):
    """Create a Mo from a XML stream.

    Args:
      xmlStream (file or file like object): The source stream to parse.

    Returns:
      cobra.mit.mo.Mo: The Mo that was parsed from the stream.
    """
    # Remove the children and add it from the fetch data set
    xmlRootNode = ET.parse(xmlStream).getroot()
    return _fromXMLRootNode(xmlRootNode)

# pylint:disable=too-many-locals
def _createMo(node, parentMo):
    """Create a managed object.

    Use the XML node and parentMo to create a Mo.

    Args:
      node (xml.etree.cElementTree.Element): The node in the XML that should
        be used to create the Mo.
      parentMo (str or cobra.mit.mo.Mo): The parent Mo for this Mo either as
        a Mo or as a Dn string.

    Returns:
      cobra.mit.mo.Mo: The managed object represented by node.
    """
    pkgName, className = parseMoClassName(node.tag)
    fqClassName = "cobra.model." + pkgName + "." + className
    pyClass = ClassLoader.loadClass(fqClassName)
    parentDnStr = None
    moProps = {}
    for attr, val in list(node.attrib.items()):
        if (attr != 'dn' and attr != 'rn' and attr != 'instanceId' and
                attr != 'status'):
            moProps[attr] = str(val)
        elif attr == 'dn':
            # Set the dn of this MO from the data returned by server
            parentDnStr = getParentDn(str(val))

    mo = buildMo(pyClass, moProps, parentMo, parentDnStr)

    for childNode in node:
        _createMo(childNode, mo)

    return mo


def toXMLStr(mo, includeAllProps=False, prettyPrint=False,
             excludeChildren=False):
    """Create a XML string from a Mo with the XML header.

    This method also provides the ability to pretty print the XML string.

    Args:
      mo (cobra.mit.mo.Mo): The Mo that should be represented by the XML
        string.
      includeAllProps (bool): Include all properties if True, only include
        naming properties and properties that are marked dirty.
      prettyPrint (bool, optional): Return the XML string in an easier to read
        format.  The default is False.
      excludeChildren (bool, optional): Do not include children Mo's if True,
        do include children Mo's otherwise. The default is False.

    Returns:
      str: The XML string derived from the mo.
    """
    xmlString = _toXMLStr(mo, includeAllProps, excludeChildren)
    xmlHeader = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xmlStr = xmlHeader + xmlString
    if prettyPrint and xmlString:
        tmp = xml.dom.minidom.parseString(xmlStr)
        xmlStr = tmp.toprettyxml(indent='  ')
    return xmlStr


def _toXMLStr(mo, includeAllProps, excludeChildren=False):
    """Create a XML string from a Mo without the XML header.

    This method does not provide the ability to pretty print the XML string.

    Args:
      mo (cobra.mit.mo.Mo): The Mo that should be represented by the XML
        string.
      includeAllProps (bool): Include all properties if True, only include
        naming properties and properties that are marked dirty.
      excludeChildren (bool, optional): Do not include children Mo's if True,
        do include children Mo's otherwise. The default is False.

    Returns:
       str: The XML string derived from the mo.
    """
    def encodeValue(xmlValue):
        """Encode a string into XML entities.

        Args:
          xmlValue (str): The string to encode.

        Returns:
          str: The xmlValue encoded to xml entities where needed.
        """
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
        moPropName = propMeta.moPropName
        value = getPropValue(mo, propMeta, includeAllProps)
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

