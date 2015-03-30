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

"""Managed object implementation.

The internal implementation of managed objects.
"""

from __future__ import unicode_literals
from builtins import next    # pylint:disable=redefined-builtin
from builtins import str     # pylint:disable=redefined-builtin
from builtins import object  # pylint:disable=redefined-builtin

from cobra.mit.naming import Dn
from cobra.mit.naming import Rn


class MoStatus(object):

    """Managed object status.

    Implements a bitmask to represent managed object status.
    """

    # Status Constants
    DEFAULT = 0
    CREATED = 2
    MODIFIED = 4
    DELETED = 8

    @classmethod
    def fromString(cls, statusStr):
        """Constructor to create a MoStatus from a string.

        Args:
          statusStr (str): A status string, example: created,modified

        Returns:
          MoStatus: The MoStatus instance
        """
        status = MoStatus(1)
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
        return status

    def __init__(self, status):
        """Initialize a MoStatus instance.

        Args:
          status (int): The status as an integer.
        """
        self.__status = status

    @property
    def status(self):
        """Return the status."""
        return self.__status

    @property
    def created(self):
        """Check the status for created.

        Returns:
          bool: Returns True if the status has the created bit set.
        """
        return (self.__status & MoStatus.CREATED) != 0

    @property
    def deleted(self):
        """Check the status for deleted.

        Returns:
          bool: Returns True if the status has the deleted bit set.
        """
        return (self.__status & MoStatus.DELETED) != 0

    @property
    def modified(self):
        """Check the status for modified.

        Returns:
          bool: Returns True if the status has the modified bit set.
        """
        return (self.__status & MoStatus.MODIFIED) != 0

    def onBit(self, status):
        """Turn a bit on.

        Args:
          status (int): The bit to turn on.
        """
        self.__status |= status

    def offBit(self, status):
        """Turn a bit off.

        Args:
          status (int): The bit to turn off.
        """
        self.__status &= ~status

    def clear(self):
        """Clear the status to 0."""
        self.__status = 0

    def __str__(self):
        """Return the status as a string."""
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

    def __lt__(self, other):
        """Implement the < operator for status objects."""
        if other is None:
            return -1
        return self.status < other.status

    def __le__(self, other):
        """Implement the <= operator for status objects."""
        if other is None:
            return -1
        return self.status <= other.status

    def __eq__(self, other):
        """Implement the == operator for status objects."""
        if other is None:
            return -1
        return self.status == other.status

    def __ne__(self, other):
        """Implement the != operator for status objects."""
        if other is None:
            return -1
        return self.status != other.status

    def __gt__(self, other):
        """Implement the > operator for status objects."""
        if other is None:
            return -1
        return self.status > other.status

    def __ge__(self, other):
        """Implement the >= operator for status objects."""
        if other is None:
            return -1
        return self.status >= other.status


class BaseMo(object):

    """The internal Base Managed Object."""

    # pylint:disable=too-few-public-methods
    class _ChildContainer(object):

        """An internal container object for child objects."""

        class _ClassContainer(object):

            """An internal container objects for child classes."""

            def __init__(self, childClass):
                """Initialize a _ClassContainer instance.

                Args:
                  childClass (object): The child class.
                """
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
                """Check if a key is valid.

                Args:
                  key (str): The key to check for validity for this
                    child container.
                  mo (cobra.mit.mo.Mo): The mo to verify that the key is
                    correct.
                """
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

            """Internal class to iterate over child objects."""

            def __init__(self, classContainers):
                """Initialize a _ChildIter instance.

                Args:
                  classContainers (list): A list of _ClassContainer instances.
                """
                self._containers = iter(list(classContainers.values()))
                self._currentContainer = None

            def __next__(self):
                """Implement next().

                Returns:
                  cobra.mit.internal.base.moimpl.BaseMo._ChildContainer: The
                  next child container.
                """
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
                """Implement iter().

                Returns:
                  iterator: The child iterator.
                """
                # pylint:disable=non-iterator-returned
                return self

        def __init__(self, classMeta):
            """Initialize a _ChildContainer instance.

            Args:
              classMeta (cobra.mit.meta.ClassMeta): The class meta for the
                child class.
            """
            self._classMeta = classMeta

            # Key is the first rn prefix with the leading '-' if any
            self._classContainers = {}

        def _getChildContainer(self, childPrefix, lookup=False):
            """Get a child container based on prefix.

            This is called in two situations, looking up the child container
            when modifying a child and looking up a child container when
            accessing a child as an attribute, for example fvTenantObj.name.
            The second situation is considered a "lookup" operation and are
            handled differently because the child prefix changes depending
            on how this method is called.

            Args:
              childPrefix (str): The prefix for the child's Rn.
              lookup (bool, optional): If true the operation is considered a
                lookup and the child's Rn prefix is not expected to contain a
                trailing hyphen if there are naming properties, if False the
                rn prefix is expected to have a trailing hyphen if there are
                naming properties.

            Returns:
              cobra.internal.base.moimpl.BaseMo._ChildContainer: The child
              container with the specified childPrefix.
            """
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
                            # pylint:disable=protected-access
                            classContainer = \
                                BaseMo._ChildContainer._ClassContainer(
                                    childClass)
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
            """Get the child iterator.

            Returns:
              iterator: The child iterator.
            """
            # pylint:disable=non-iterator-returned,protected-access
            return BaseMo._ChildContainer._ChildIter(self._classContainers)

        def __len__(self):
            """Get the number of children.

            Returns:
              int: The number of children.
            """
            numChildren = 0
            for classContainer in self._classContainers:
                numChildren += len(classContainer)
            return numChildren

    def __init__(self, parentMoOrDn, markDirty, *namingVals,
                 **creationProps):
        """Initialize a BaseMo instance.

        This class can not be instantiated directly, instead instantiate a
        managed object.

        Args:
          parentMoOrDn (cobra.mit.mo.Mo or str): The parent managed object or
            the parent managed object distinguished name.
          markDirty (bool): If set to True, the creation properties will be
            marked dirty to indicate that they have not been committed.
          *namingVals (str): The required naming values for the managed object.
          **creationProps (dict of str): The properties that should be set at
            object creation time.

        """
        if self.__class__ == BaseMo:
            raise NotImplementedError('BaseMo cannot be instantiated.')

        # pylint:disable=no-member
        self.__dict__['_BaseMo__meta'] = self.__class__.meta
        self.__dict__['_BaseMo__status'] = MoStatus(MoStatus.CREATED |
                                                    MoStatus.MODIFIED)
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
            # pylint:disable=protected-access
            self.__parentMo.__modifyChild(self, attach=True)

    def __getattr__(self, attrName):
        """Get an attribute.

        A custom getattr for Mo's is used to allow attributes on BaseMo to
        be returned if the attribute does not exist on the Mo.

        Args:
          attrName (str): The attribute name.
        """
        if attrName in self.meta.props:
            # need to do lazy initialization of this prop to default value
            propMeta = self.meta.props[attrName]
            defValue = propMeta.defaultValue
            self.__setprop(propMeta, attrName, defValue, markDirty=False,
                           forced=True)
            return defValue

        # We got this call because properties did not match, so look for
        # child class containers
        # pylint:disable=protected-access
        return self.__children._getChildContainer(attrName, True)

    def __setattr__(self, attrName, attrValue):
        """Set an attribute.

        A custom setattr for Mo's is used to allow attributes on BaseMo to
        be set if the attributes does not exist on the Mo.

        Args:
          attrName (str): The attribute name.
          attrValue:  The attribute value

        Raises:
          AttributeError: If the attribute (property) can not be found.
        """
        if attrName in self.meta.props:
            propMeta = self.meta.props[attrName]
            self.__setprop(propMeta, attrName, attrValue)
        elif attrName.startswith('_BaseMo__'):
            self.__dict__[attrName] = attrValue
        else:
            raise AttributeError('property "%s" not found' % attrName)

    # pylint:disable=too-many-arguments
    def __setprop(self, propMeta, propName, propValue, markDirty=True,
                  forced=False):
        """Set a property for this Mo.

        Args:
          propMeta (cobra.mit.meta.PropMeta): The property meta object
          propName (str): The name of the property
          propValue:  The value that the property should be set to.
          markDirty (bool, optional): If True the property will be marked as
            dirty and not yet committed.  If False the property will not be
            marked as dirty.  The default is True.
          forced (bool, optional): If True the property will be set even if
            it is a create only property.  If False, trying to set a create
            only property will result in an exception.

        Raises:
          ValueError: If the property is a Dn property or the property is a
            Rn property or if the property is a create only property and
            forced is False.
        """
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
        """Set the Mo status to modified."""
        self.__status.onBit(MoStatus.MODIFIED)
        self.__dirtyProps.add('status')

    def __modifyChild(self, childMo, attach):
        """Modify the child of this Mo.

        Args:
          childMo (cobra.mit.mo.Mo): The child to modify.
          attach (bool): If True the child is attached to this Mo, otherwise
            the child container is deleted.
        """
        childMeta = childMo.meta
        namingVals = []
        for nPropMeta in childMeta.namingProps:
            namingVals.append(getattr(childMo, nPropMeta.name))
        childPrefix = childMeta.rnPrefixes[0][0]
        # pylint:disable=protected-access
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
        """Set the parent of this Mo.

        Initializes the parent Mo if it is not already initialized.

        Args:
          parentMo (cobra.mit.mo.Mo): The parent Mo.
        """
        # This attribute is defined in BaseMo
        # pylint:disable=attribute-defined-outside-init
        self.__parentMo = parentMo
        if parentMo is not None:
            # This attribute is defined in BaseMo
            # pylint:disable=attribute-defined-outside-init
            self.__parentDn = parentMo.dn.clone()
        else:
            self.__parentDn = None

    def _attachChild(self, childMo):
        """Attach a child to this Mo.

        If the child is already attached to parent it is detached first.

        Args:
          childMo (cobra.mit.mo.Mo): The child Mo.
        """
        pMo = childMo.parent
        if pMo is not None:
            # Detach from the current parent
            # pylint:disable=protected-access
            pMo._detachChild(childMo)

        self.__modifyChild(childMo, True)
        # pylint:disable=protected-access
        childMo._setParent(self)

    def _detachChild(self, childMo):
        """Detach a child Mo from this parent Mo.

        Args:
          childMo (cobra.mit.mo.Mo): The child Mo.

        Raises:
          ValueError: If the parent of the child Mo is not this Mo.
        """
        if childMo.parent != self:
            raise ValueError('%s is not attached to %s' % (str(self.dn),
                                                           str(childMo.dn)))
        self.__modifyChild(childMo, False)
        # pylint:disable=protected-access
        childMo._setParent(None)

    def _delete(self):
        """Mark this Mo as deleted."""
        self.__status.clear()
        self.__status.onBit(MoStatus.DELETED)
        self.__dirtyProps.add('status')

    def _dn(self):
        """Get the Dn for this Mo.

        Initializes the Dn if it wasn't already intialized.

        Returns:
          cobra.mit.naming.Dn: The Dn of this Mo.
        """
        # This attribute is defined in BaseMo
        # pylint:disable=access-member-before-definition
        if self.__dn is None:
            # This attribute is defined in BaseMo
            # pylint:disable=attribute-defined-outside-init
            self.__dn = self._parentDn().clone()
            self.__dn.appendRn(self.__rn)
        return self.__dn

    def _rn(self):
        """Get the Rn for this Mo.

        Returns:
          cobra.mit.naming.Rn: The Rn for this Mo.
        """
        return self.__rn

    def _status(self):
        """Get the status of this Mo.

        Returns:
          cobra.internal.base.moimpl.MoStatus: The status of this Mo.
        """
        return self.__status

    def _parentDn(self):
        """Get the Dn for the parent of this Mo.

        Initializes the parent Dn if it wasn't initilized yet.

        Returns:
          cobra.mit.naming.Dn: The Dn of the parent of this Mo.
        """
        if self.__parentDn is None:
            # This attribute is defined in BaseMo
            # pylint:disable=attribute-defined-outside-init
            self.__parentDn = Dn.fromString(self.__parentDnStr)
        return self.__parentDn

    def _parent(self):
        """Get the parent Mo for this Mo.

        Returns:
          cobra.mit.mo.Mo: The parent Mo for this Mo.
        """
        return self.__parentMo

    def _dirtyProps(self):
        """Get the dirty props for the Mo.

        Returns:
          iterator: An iterator for the dirty properties for the Mo.
        """
        return iter(self.__dirtyProps)

    def _children(self):
        """Get the children of the Mo.

        Returns:
          iterator: An iterator for the children of the Mo.
        """
        return iter(self.__children)

    def _numChildren(self):
        """Get the number of children of the Mo.

        Returns:
          int: The number of children.
        """
        return len(self.__children)

    def _resetProps(self):
        """Mark all properties as clean."""
        # This attribute is defined in BaseMo
        # pylint:disable=attribute-defined-outside-init
        self.__dirtyProps = set()

    def _isPropDirty(self, propName):
        """Check if the given propName is marked as dirty.

        Args:
          propName (str): The property name.

        Returns:
          bool: True if the propName is dirty, false otherwise.
        """
        return propName in self.__dirtyProps
