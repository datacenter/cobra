# Copyright 2019 Cisco Systems, Inc.
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

import sys
if sys.version_info[0] == 3:
    from builtins import str

import json
from ._loader import ClassLoader
from ._codec_utils import parseMoClassName, getParentDn, listWithTotalCount


def parseJSONError(rspText, errorClass, httpCode=None):
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


def fromJSONStr(jsonStr, tree_only=False):
    # Remove the children and add it from the fetch data set
    moDict = json.loads(jsonStr)
    return fromJSONDict(moDict) if not tree_only else moDict


def fromJSONDict(moDict):
    rootNode = moDict["imdata"]

    allMos = listWithTotalCount()
    allMos.totalCount = int(moDict["totalCount"])
    for moNode in rootNode:
        className = list(moNode.keys())[0]
        moData = moNode[className]
        mo = _createMo(className, moData, None)
        allMos.append(mo)
    return allMos


def _createMo(moClassName, moData, parentMo):
    pkgName, className = parseMoClassName(moClassName)
    fqClassName = "cobra.model." + pkgName + "." + className
    pyClass = ClassLoader.loadClass(fqClassName)
    parentDnStr = None
    moProps = moData['attributes']
    if 'dn' in moProps:
        parentDnStr = getParentDn(moProps['dn'])
        del moProps['dn']
    if 'rn' in moProps:
        del moProps['rn']
    if 'instanceId' in moProps:
        del moProps['instanceId']
    if 'status' in moProps:
        del moProps['status']

    namingVals = []
    for propMeta in pyClass.meta.namingProps:
        propName = propMeta.moPropName
        namingVals.append(moProps[propName])
        del moProps[propName]

    parentMoOrDn = parentMo if parentMo else parentDnStr
    mo = pyClass(parentMoOrDn, *namingVals, markDirty=False, **moProps)
    mo.resetProps()
    parentMoOrDn = parentMo if parentMo else parentDnStr

    children = moData.get('children', [])
    for childNode in children:
        className = list(childNode.keys())[0]
        moData = childNode[className]
        _createMo(className, moData, mo)

    return mo


def __toJSONDict(mo, includeAllProps=False, prettyPrint=False, excludeChildren=False):
    meta = mo.meta
    className = meta.moClassName

    moDict = {}
    attrDict = {}
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
        elif propMeta.isNaming or includeAllProps or mo.isPropDirty(name):
            value = getattr(mo, name)

        if value is not None:
            attrDict[moPropName] = {}
            attrDict[moPropName] = str(value)

    if len(attrDict) > 0:
        moDict['attributes'] = attrDict

    if not excludeChildren:
        childrenArray = []
        for childMo in mo.children:
            childMoDict = __toJSONDict(childMo, includeAllProps, prettyPrint, excludeChildren)
            childrenArray.append(childMoDict)
        if len(childrenArray) > 0:
            moDict['children'] = childrenArray

    return {className: moDict}


def toJSONStr(mo, includeAllProps=False, prettyPrint=False, excludeChildren=False):
    jsonDict = __toJSONDict(mo, includeAllProps, prettyPrint, excludeChildren)
    indent = 2 if prettyPrint else None
    jsonStr = json.dumps(jsonDict, indent=indent)

    return jsonStr
