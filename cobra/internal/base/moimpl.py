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

from __future__ import unicode_literals
from builtins import next
from builtins import str
from builtins import object

from cobra.mit.naming import Dn
from cobra.mit.naming import Rn


class MoStatus(object):
    # Status Constants
    CLEAR = 1
    CREATED = 2
    MODIFIED = 4
    DELETED = 8

    @classmethod
    def fromString(cls, statusStr):
        status = MoStatus(0)
        if statusStr:
            codes = statusStr.split(',')
            for code in codes:
                strippedCode = code.strip()
                if strippedCode == 'created':
                    status.onBit(MoStatus.CREATED)
                elif strippedCode == 'modified':
                    status.onBit(MoStatus.MODIFIED)
                elif strippedCode == 'deleted':
                    status.onBit(MoStatus.DELETED)
                    return

    def __init__(self, status):
        self.__status = status

    @property
    def created(self):
        return (self.__status & MoStatus.CREATED) != 0

    @property
    def deleted(self):
        return (self.__status & MoStatus.DELETED) != 0

    @property
    def modified(self):
        return (self.__status & MoStatus.MODIFIED) != 0

    def onBit(self, status):
        self.__status |= status

    def offBit(self, status):
        self.__status &= ~status

    def clear(self):
        self.__status = 0

    def __str__(self):
        if self.deleted:
            return 'deleted'
        status = ''
        if self.created:
            status += 'created'
        if self.modified:
            if len(status):
                status += ',modified'
            else:
                status += 'modified'
        return status

    def __cmp__(self, other):
        if other is None:
            return -1
        return (self.__status, other.status)


class BaseMo(object):

    class _ChildContainer(object):
        class _ClassContainer(object):
            def __init__(self, childClass):
                self._childClass = childClass

                # Key is the tuple of naming props and value is the child Mo
                self._childObjects = {}

            def __getitem__(self, key):
                return self._childObjects[key]

            def __contains__(self, key):
                return key in self._childObjects

            def __setitem__(self, key, value):
                self._checkKey(key, value)
                self._childObjects[key] = value

            def __delitem__(self, key):
                del self._childObjects[key]

            def __len__(self):
                return len(self._childObjects)

            def __iter__(self):
                return iter(list(self._childObjects.values()))

            def _checkKey(self, key, mo):
                meta = self._childClass.meta
                numNamingProps = len(meta.namingProps)
                namingVals = []
                if numNamingProps == 0:
                    if key is not None:
                        raise ValueError('"%s" is bad key for "%s"' %
                                         (str(key), meta.className))
                elif numNamingProps > 1:
                    if not isinstance(key, tuple):
                        raise ValueError('"%s" requires tuple of naming props'
                                          % meta.className)
                    elif len(key) != numNamingProps:
                        raise ValueError('"%s" requires "%d" naming props'
                                          % (meta.className, numNamingProps))
                    namingVals.extend(key)
                else:
                    namingVals.append(key)

                namingValsIter = iter(namingVals)
                for propMeta in meta.namingProps:
                    moVal = getattr(mo, propMeta.name)
                    keyVal = next(namingValsIter)
                    if moVal != keyVal:
                        raise ValueError("'%s' must be '%s' for mo '%s'" %
                                         (keyVal, moVal, str(mo.rn)))

        class _ChildIter(object):
            def __init__(self, classContainers):
                self._containers = iter(list(classContainers.values()))
                self._currentContainer = None

            def __next__(self):
                if self._currentContainer is None:
                    # If no more containers this statement will throw an
                    # StopIteration exception and we exit else we move on
                    # to the next container
                    self._currentContainer = iter(next(self._containers))
                try:
                    return next(self._currentContainer)
                except StopIteration:
                    # Current container is done, see if we have anything else
                    self._currentContainer = None
                    return next(self)

            def __iter__(self):
                return self

        def __init__(self, classMeta):
            self._classMeta = classMeta

            # Key is the first rn prefix with the leading '-' if any
            self._classContainers = {}

        def _getChildContainer(self, childPrefix, lookup=False):
            classContainer = self._classContainers.get(childPrefix, None)
            if classContainer is None:
                for childClass in self._classMeta.childClasses:
                    childMeta = childClass.meta
                    prefix = childMeta.rnPrefixes[0][0]
                    newPrefix = childPrefix
                    # Accessing a child like an attribute will lead to the
                    # childPrefix being passed in without a hyphen, add it
                    # here for this circumstance
                    if (childPrefix[-1] != '-' and
                        len(childMeta.namingProps) > 0):
                            newPrefix = childPrefix + '-'
                    if newPrefix == prefix:
                        # Do not overwrite the classContainer for a lookup
                        # operation
                        if not lookup:
                            classContainer = \
                            BaseMo._ChildContainer._ClassContainer(childClass)
                            self._classContainers[newPrefix] = classContainer
                        else:
                            classContainer = self._classContainers.get(
                                newPrefix, None)
                        break
                if classContainer is None:
                    # Could not find a child class with this prefix
                    raise AttributeError('No class with prefix "%s" found' %
                                         childPrefix)
            return classContainer

        def __iter__(self):
            return BaseMo._ChildContainer._ChildIter(self._classContainers)

        def __len__(self):
            numChildren = 0
            for classContainer in self._classContainers:
                numChildren += len(classContainer)
            return numChildren

    def __init__(self, parentMoOrDn, markDirty, *namingVals, 
            **creationProps):

        if self.__class__ == BaseMo:
            raise NotImplementedError('BaseMo cannot be instantiated.')

        self.__dict__['_BaseMo__meta'] = self.__class__.meta
        self.__dict__['_BaseMo__status'] = MoStatus(MoStatus.CREATED | MoStatus.MODIFIED)
        self.__dict__['_BaseMo__dirtyProps'] = set()
        self.__dict__['_BaseMo__children'] = BaseMo._ChildContainer(self.__meta)
        self.__dict__['_BaseMo__rn'] = Rn(self.__meta, *namingVals)
        self.__dict__['_BaseMo__dn'] = None

        if isinstance(parentMoOrDn, Dn):
            self.__dict__['_BaseMo__parentDn'] = parentMoOrDn.clone()
            self.__dict__['_BaseMo__parentMo'] = None
        elif isinstance(parentMoOrDn, BaseMo):
            self.__dict__['_BaseMo__parentMo'] = parentMoOrDn
            self.__dict__['_BaseMo__parentDn'] = parentMoOrDn.dn.clone()
        else:
            parentMoOrDn = str(parentMoOrDn)
            if isinstance(parentMoOrDn, str):
                self.__dict__['_BaseMo__parentDnStr'] = parentMoOrDn
                self.__dict__['_BaseMo__parentDn'] = None
                self.__dict__['_BaseMo__parentMo'] = None
            else:
                raise ValueError('parent mo or dn must be specified')

        # Set the naming props
        self.__dirtyProps.add('status')
        namingValsIter = iter(namingVals)
        for namingPropMeta in self.__meta.namingProps:
            propName = namingPropMeta.name
            value = next(namingValsIter)
            value = namingPropMeta.makeValue(value)
            self.__dict__[propName] = value
            self.__dirtyProps.add(propName)

        # Set the creation props
        props = self.__meta.props
        for name, value in list(creationProps.items()):
            propMeta = props[name]
            value = propMeta.makeValue(value)
            self.__dict__[name] = value
            if markDirty:
                self.__dirtyProps.add(name)

        if self.__parentMo:
            self.__parentMo.__modifyChild(self, attach=True)

    def __getattr__(self, attrName):
        if attrName in self.meta.props:
            # need to do lazy initialization of this prop to default value
            propMeta = self.meta.props[attrName]
            defValue = propMeta.defaultValue
            self.__setprop(propMeta, attrName, defValue, markDirty=False,
                    forced=True)
            return defValue

        # We got this call because properties did not match, so look for
        # child class containers
        return self.__children._getChildContainer(attrName, True)

    def __setattr__(self, attrName, attrValue):
        if attrName in self.meta.props:
            propMeta = self.meta.props[attrName]
            self.__setprop(propMeta, attrName, attrValue)
        elif attrName.startswith('_BaseMo__'):
            self.__dict__[attrName] = attrValue
        else:
            raise AttributeError('property "%s" not found' % attrName)

    def __setprop(self, propMeta, propName, propValue, markDirty=True,
            forced=False):
        value = propMeta.makeValue(propValue)
        if propMeta.isDn:
            raise ValueError("dn cannot be set")
        elif propMeta.isRn:
            raise ValueError("rn cannot be set")
        elif propMeta.isCreateOnly and not forced:
            raise ValueError('createOnly "%s" property cannot be set' %
                             propName)

        # Set the attribute to the object dict and mark it dirty
        self.__dict__[propName] = value

        if markDirty:
            self.__setModified()
            self.__dirtyProps.add(propName)

    def __setModified(self):
        self.__status.onBit(MoStatus.MODIFIED)
        self.__dirtyProps.add('status')

    def __modifyChild(self, childMo, attach):
        childMeta = childMo.meta
        namingVals = []
        for nPropMeta in childMeta.namingProps:
            namingVals.append(getattr(childMo, nPropMeta.name))
        childPrefix = childMeta.rnPrefixes[0][0]
        childContainer = self.__children._getChildContainer(childPrefix)
        if len(namingVals) == 0:
            if attach:
                childContainer[None] = childMo
            else:
                del childContainer[None]
        elif len(namingVals) == 1:
            if attach:
                childContainer[namingVals[0]] = childMo
            else:
                del childContainer[namingVals[0]]
        else:
            nvKey = tuple(namingVals)
            if attach:
                childContainer[nvKey] = childMo
            else:
                del childContainer[nvKey]

    def _setParent(self, parentMo):
        self.__parentMo = parentMo
        if parentMo is not None:
            self.__parentDn = parentMo.dn.clone()
        else:
            self.__parentDn = None

    def _attachChild(self, childMo):
        pMo = childMo.parent
        if pMo is not None:
            # Detach from the current parent
            pMo._detachChild(childMo)

        self.__modifyChild(childMo, True)
        childMo._setParent(self)

    def _detachChild(self, childMo):
        if childMo.parent != self:
            raise ValueError('%s is not attached to %s' (str(self.dn),
                str(childMo.dn)))
        self.__modifyChild(childMo, False)
        childMo._setParent(None)

    def _delete(self):
        self.__status.clear()
        self.__status.onBit(MoStatus.DELETED)
        self.__dirtyProps.add('status')

    def _dn(self):
        if self.__dn is None:
            self.__dn = self._parentDn().clone()
            self.__dn.appendRn(self.__rn)
        return self.__dn

    def _rn(self):
        return self.__rn

    def _status(self):
        return self.__status

    def _parentDn(self):
        if self.__parentDn is None:
            self.__parentDn = Dn.fromString(self.__parentDnStr)
        return self.__parentDn

    def _parent(self):
        return self.__parentMo

    def _dirtyProps(self):
        return iter(self.__dirtyProps)

    def _children(self):
        return iter(self.__children)

    def _numChildren(self):
        return len(self.__children)

    def _resetProps(self):
        self.__dirtyProps = set()

    def _isPropDirty(self, propName):
        return propName in self.__dirtyProps

