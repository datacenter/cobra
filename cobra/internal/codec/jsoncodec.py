# Copyright 2015 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The ACI Python SDK json codec module."""

from builtins import str  # pylint:disable=redefined-builtin
import json
from cobra.mit.meta import ClassLoader
from cobra.internal.codec import (parseMoClassName, getParentDn, buildMo,
                                  getPropValue)


def parseJSONError(rspText, errorClass, httpCode=None):
    """Parse an error in a JSON response.

    This method takes a string and does a json.loads on it, then parses the
    response as a python dictionary.

    Args:
      rspText (str): The response as a string
      errorClass (Exception): The exception that should be called when the
        error is parsed.  If set to None, a ValueError will be raised.
      httpCode (int, optional): The http error code that indicated an error
        occurred.

    Raises:
        Exception: If the errorClass is set, the type of exception it is set
          to will be raised.
        ValueError: If the errorClass is None or the response can not be
          parsed.
    """
    try:
        rspDict = json.loads(rspText)
        data = rspDict.get('imdata', None)
        if data:
            firstRecord = data[0]
            if 'error' == list(firstRecord.keys())[0]:
                errorDict = firstRecord['error']
                reasonStr = errorDict['attributes']['text']
                errorCode = errorDict['attributes']['code']
                if errorClass:
                    raise errorClass(errorCode, reasonStr, httpCode)
                raise ValueError(reasonStr)
    except:
        raise ValueError(rspText)


def fromJSONStr(jsonStr):
    """Create a Mo from a JSON string.

    This method does json.loads on the JSON string and passes it to
    fromJSONDict to process.

    Args:
      jsonStr (str): The JSON string representing a Mo.

    Returns:
      cora.mit.mo.Mo: The managaed object represented by the JSON.
    """
    moDict = json.loads(jsonStr)
    return fromJSONDict(moDict)


def fromJSONDict(moDict):
    """Create a Mo from a python dictionary.

    Args:
      moDict (dict): The dictionary containing the Mo.

    Returns:
      cobra.mit.mo.Mo: The Mo object.
    """
    rootNode = moDict["imdata"]

    allMos = []
    for moNode in rootNode:
        className = list(moNode.keys())[0]
        moData = moNode[className]
        mo = _createMo(className, moData, None)
        allMos.append(mo)
    return allMos


def _createMo(moClassName, moData, parentMo):
    """Create a Mo given a class name, some data and a parent Mo.

    Args:
      moClassName (str): The Mo class name in packageClass form.
      moData (dict): The Mo as a python dictionary.
      parentMo (str or cobra.mit.mo.Mo): The parent Mo as a Dn string or
        a Mo.

    Returns:
      cobra.mit.mo.Mo: The Mo from moClass and moData.
    """
    pkgName, className = parseMoClassName(moClassName)
    fqClassName = "cobra.model." + pkgName + "." + className
    pyClass = ClassLoader.loadClass(fqClassName)
    parentMoOrDn = parentMo
    moProps = moData['attributes']

    if 'dn' in moProps:
        # No parentMo, use the dn of this MO from the data returned by server
        if parentMoOrDn is None:
            parentMoOrDn = getParentDn(moProps['dn'])
        del moProps['dn']

    # Ignore Rn and InstanceId
    if 'rn' in moProps:
        del moProps['rn']
    if 'instanceId' in moProps:
        del moProps['instanceId']

    if 'status' in moProps and not moProps['status']:
        # Ignore empty status
        del moProps['status']

    mo = buildMo(pyClass, moProps, parentMoOrDn)

    children = moData.get('children', [])
    for childNode in children:
        className = list(childNode.keys())[0]
        moData = childNode[className]
        _createMo(className, moData, mo)

    return mo


def __toJSONDict(mo, includeAllProps=False, excludeChildren=False):
    """Create a dictionary from a Mo.

    Args:
      mo (cobra.mit.mo.MO): The managed object to represent as a dictionary.
      includeAllProps (bool, optional): If True all of the Mo's properties
        will be included in the Mo, otherwise only the naming properties and
        properties marked dirty will be included. The default is False.
      excludeChildren (bool): If True the children will not be included in
        the resulting dictionary, otherwise the children are included.  The
        default is False.

    Returns:
      dict: The Mo as a python dictionary.
    """
    meta = mo.meta
    className = meta.moClassName

    moDict = {}
    attrDict = {}
    for propMeta in meta.props:
        moPropName = propMeta.moPropName
        value = getPropValue(mo, propMeta, includeAllProps)
        if value is not None:
            attrDict[moPropName] = {}
            attrDict[moPropName] = str(value)

    if len(attrDict) > 0:
        moDict['attributes'] = attrDict

    if not excludeChildren:
        childrenArray = []
        for childMo in mo.children:
            childMoDict = __toJSONDict(childMo, includeAllProps,
                                       excludeChildren)
            childrenArray.append(childMoDict)
        if len(childrenArray) > 0:
            moDict['children'] = childrenArray

    return {className: moDict}


def toJSONStr(mo, includeAllProps=False, prettyPrint=False,
              excludeChildren=False):
    """Create a JSON string representing the given Mo.

    Args:
      mo (cobra.mit.mo.Mo): The Mo that should be represented by the resulting
        JSON string.
      includeAllProps (bool, optional): If True all the properties of the Mo
        will be included, otherwise only the naming properties and properties
        marked dirty are included.  The default is False.
      prettyPrint (bool, optional): If True the resulting JSON string will be
        returned in an easier to read format.  The default is False.
      excludeChildren (bool, optional): If True the children will not be
        included in the resulting JSON string, otherwise the children will be
        included.  The default is False.

    Returns:
      str: The Mo represented as a JSON string.
    """
    jsonDict = __toJSONDict(mo, includeAllProps, excludeChildren)
    indent = 2 if prettyPrint else None
    # Keys are sorted because the APIC REST API requires the attributes to come
    # first.
    jsonStr = json.dumps(jsonDict, indent=indent, sort_keys=True)

    return jsonStr
