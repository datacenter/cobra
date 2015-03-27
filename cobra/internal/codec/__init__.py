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

"""ACI Python SDK codecs module."""


def getParentDn(dnStr):
    """Get the parent Dn.

    Args:
      dnStr (str): The Dn string to use to find the parent for.

    Returns:
      str: An empty strin if dnStr is None, otherwise the parent Dn as a string
    """
    if dnStr is None:
        return ''
    count = 0
    reverseDn = dnStr[::-1]
    pDn = ''
    foundParent = False
    for dnChar in reverseDn:
        if not foundParent and dnChar == ']':
            count += 1
        elif not foundParent and dnChar == '[':
            count -= 1
        elif not foundParent and count == 0 and dnChar == '/':
            foundParent = True
        elif foundParent:
            pDn += dnChar
    parentDn = pDn[::-1]
    return parentDn


def parseMoClassName(className):
    """Parse the Mo class name into the package and class name components.

    Given a class name (aaaUserEp) returns tuple aaa,UserEp.

    Args:
      className (str): The Mo class name in packageClass form.

    Returns:
      tuple: The Mo class name in (package, Class) form.
    """
    idx = -1
    upperFound = False

    for character in className:
        idx += 1
        if character.isupper():
            upperFound = True
            break

    if upperFound:
        pkg = className[:idx]
        klass = className[idx:]
    else:
        pkg = className
        klass = ""
    return (pkg, klass)

def buildMo(pyClass, moProps, parentMo, parentDnStr):
    """Build a Mo by calling pyClass.

    The naming properties are determined from pyClass.meta and set to
    the values in moProps.

    Args:
      pyClass (cobra.mit.mo.Mo): The class to be instantiated.  Note this
        class must be imported first usually by calling
        cobra.mit.meta.ClassLoader.
      moProps (dict): A dictionary representing the instance properties.
      parentMo (cobra.mit.mo.Mo): The parent Mo for the Mo that will be
        built.
      parentDnStr (str): A string representing the parent Mo for the Mo that
        will be built.

    Returns:
      cobra.mit.mo.Mo: The built managed object.
    """
    namingVals = []
    for propMeta in pyClass.meta.namingProps:
        propName = propMeta.moPropName
        namingVals.append(moProps[propName])
        del moProps[propName]

    parentMoOrDn = parentMo if parentMo else parentDnStr
    mo = pyClass(parentMoOrDn, *namingVals, markDirty=False, **moProps)
    mo.resetProps()
    return mo

def getPropValue(mo, propMeta, includeAllProps):
    """Get a Mo property value

    Args:
      mo (cobra.mit.mo.Mo): The Mo for the attribute.
      propMeta (cobra.mit.meta.PropMeta): The property meta object
      includeAllProps (bool): If True all properties will return values,
        otherwise only naming properties and properties that are marked dirty
        will return values.
    """
    name = propMeta.name
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
    return value
