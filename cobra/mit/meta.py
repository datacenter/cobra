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

"""The meta module for the ACI Python SDK (cobra)."""

import sys
if sys.version_info[0] == 3:
    from builtins import str
from builtins import object
from builtins import next
from ._loader import ClassLoader


class Category(object):
    def __init__(self, name, categoryId):
        self.name = name
        self.id = categoryId

    def __str__(self):
        return self.name

    # def __cmp__(self, other):
    #     if isinstance(other, Category):
    #         return self.id - other.id
    #     elif isinstance(other, int):
    #         return self.id - other
    #     elif isinstance(other, str):
    #         return cmp(self.name, other)

    def __hash__(self):
        return hash(self.name)

    def __lt__(self, other):
        """Implement <."""
        if isinstance(other, Category):
            return self.id < other.id
        elif isinstance(other, int):
            return self.id < other
        elif isinstance(other, str):
            return str(self.name) < other

    def __le__(self, other):
        """Implement <=."""
        if isinstance(other, Category):
            return self.id <= other.id
        elif isinstance(other, int):
            return self.id <= other
        elif isinstance(other, str):
            return str(self.name) <= other

    def __eq__(self, other):
        """Implement ==."""
        if isinstance(other, Category):
            return self.id == other.id
        elif isinstance(other, int):
            return self.id == other
        elif isinstance(other, str):
            return str(self.name) == other

    def __ne__(self, other):
        """Implement !=."""
        if isinstance(other, Category):
            return self.id != other.id
        elif isinstance(other, int):
            return self.id != other
        elif isinstance(other, str):
            return str(self.name) != other

    def __gt__(self, other):
        """Implement >."""
        if isinstance(other, Category):
            return self.id > other.id
        elif isinstance(other, int):
            return self.id > other
        elif isinstance(other, str):
            return str(self.name) > other

    def __ge__(self, other):
        """Implement >=."""
        if isinstance(other, Category):
            return self.id >= other.id
        elif isinstance(other, int):
            return self.id >= other
        elif isinstance(other, str):
            return str(self.name) >= other


class DeploymentCategory(object):
    categories = [('other', "Other"),
                  ('epg', "EPG"),
                  ('interface', "Interface"),
                  ('module', "Module"),
                  ('node', "Node"),
                  ('vm', "Virtual Machine"),
                  ('vm-port-group', "VM Port Group"),
                  ('policy', "Policy")
                  ]

    def __init__(self, name, label):
        self.name = name
        self.label = label


class DeploymentPathMeta(object):
    def __init__(self, name, label, dest):
        self.name = name
        self.label = label
        self.destination = dest
        self.__destinationCategory = None

    @property
    def destinationCategory(self):
        if self.__destinationCategory is None:
            destClass = ClassLoader.loadClass(self.destination)
            self.__destinationCategory = destClass.meta.deploymentCategory
        return self.__destinationCategory

    def __hash__(self):
        return hash(self.name)


def findDeploymentPathsMatchingResources(meta, resCategories):
    matchingPathNames = []
    for resCategory in resCategories:
        for path in meta.deploymentQueryPaths:
            if resCategory == path.destinationCategory.name or resCategory == 'node':
                matchingPathNames.append(path.name)
    return matchingPathNames


class ClassMeta(object):
    def __init__(self, className):
        self.className = className
        self.moClassName = None
        self.label = None
        self.category = None

        self.isAbstract = False
        self.isRelation = False
        self.isSource = False
        self.isExplicit = False
        self.isNamed = False
        self.isStats = False

        self.writeAccessMask = 0
        self.readAccessMask = 0
        self.isDomainable = False
        self.isReadOnly = False
        self.isConfigurable = False
        self.isDeletable = False
        self.isContextRoot = False
        self.isWireOnly = False

        self.concreteSubClasses = ClassMeta._ClassContainer()
        self.superClasses = ClassMeta._ClassContainer()

        self.childClasses = ClassMeta._ClassContainer()
        self.childNamesAndRnPrefix = []
        self.parentClasses = ClassMeta._ClassContainer()

        self.props = ClassMeta._PropContainer()
        self.namingProps = []

        self.rnFormat = None
        self.rnPrefixes = None
        self.ctxRoot = None

        self.deploymentQuery = False
        self.deploymentType = None
        self.deploymentQueryPaths = []
        self.deploymentCategory = DeploymentCategory('other', "Other")

    def getClass(self):
        return ClassLoader.loadClass(self.className)

    def hasContextRoot(self):
        ctxRoot = self.getContextRoot()
        return ctxRoot and ctxRoot != self

    def getContextRoot(self, pStack=set()):
        if self.isContextRoot:
            return self
        elif self.ctxRoot:
            return self.ctxRoot
        else:
            # Search for the context root in the ancestor hierarchy
            for parent in self.parentClasses:
                if parent in pStack:
                    continue
                else:
                    pStack.add(parent)
                parentMeta = parent.meta
                ctxRoot = parentMeta.getContextRoot(pStack)
                if ctxRoot:
                    self.ctxRoot = ctxRoot
                    return ctxRoot
        return None

    def allSuperClassNames(self):
        superClassNames = set([superClass.meta.moClassName for superClass in self.superClasses])
        superClassNames.add(self.moClassName)
        return superClassNames

    class _ClassContainer(object):
        class LazyIter(object):
            def __init__(self, container):
                self._container = container
                self._classNames = iter(container.names)

            def __next__(self):
                nextClassName = next(self._classNames)
                return self._container[nextClassName]

            def __iter__(self):
                return self

        @property
        def names(self):
            return list(self._classes.keys())

        def add(self, className):
            self._classes[className] = None

        def __init__(self):
            self._classes = {}

        def __getitem__(self, className):
            klass = self._classes[className]
            if not klass:
                klass = ClassLoader.loadClass(className)
                self._classes[className] = klass
            return klass

        def __contains__(self, className):
            return className in self._classes

        def __len__(self):
            return len(self._classes)

        def __iter__(self):
            return ClassMeta._ClassContainer.LazyIter(self)

    class _PropContainer(object):
        def __init__(self):
            self._props = {}

        def add(self, propName, propMeta):
            self._props[propName] = propMeta

        @property
        def names(self):
            return list(self._props.keys())

        def __getitem__(self, propName):
            return self._props.get(propName, None)

        def __contains__(self, propName):
            return propName in self._props

        def __len__(self):
            return len(self._props)

        def __iter__(self):
            return iter(list(self._props.values()))

        def __getattr__(self, propName):
            if propName not in self._props:
                raise AttributeError('No property %s' % propName)
            return self._props[propName]


class StatsClassMeta(ClassMeta):
    def __init__(self, className, statsLabel):
        super(StatsClassMeta, self).__init__(className)
        self._counters = list()
        self.statsLabel = statsLabel
        self.isStats = True

    @property
    def counters(self):
        return list(self._counters)


class CounterMeta(object):
    def __init__(self, name, category, unit, label):
        self.name = name
        self.category = category
        self.unit = unit
        self.label = label
        self._propRefs = dict()

    @property
    def props(self):
        return list(self._propRefs.values())

    def __getitem__(self, category):
        return self._propRefs[category]


class SourceRelationMeta(ClassMeta):
    # Cardinality constants
    ONE_TO_ONE = object()
    ONE_TO_M = object()
    N_TO_ONE = object()
    N_TO_M = object()

    def __init__(self, className, targetClassName):
        ClassMeta.__init__(self, className)
        self.targetClassName = targetClassName
        self.cardinality = None
        self.isRelation = True
        self.isSource = True
        self.isExplicit = True

    def getTargetClass(self):
        return ClassLoader.loadClass(self.targetClassName)


class NamedSourceRelationMeta(SourceRelationMeta):
    def __init__(self, className, targetClassName):
        SourceRelationMeta.__init__(self, className, targetClassName)
        self.targetNameProps = {}
        self.isExplicit = False
        self.isNamed = True


class TargetRelationMeta(ClassMeta):
    def __init__(self, className, sourceClassName):
        ClassMeta.__init__(self, className)
        self.sourceClassName = sourceClassName
        self.isRelation = True
        self.isTarget = True

    def getSourceClass(self):
        return ClassLoader.loadClass(self.sourceClassName)


class Constant(object):
    def __init__(self, const, label, value):
        self.value = value
        self.label = label
        self.const = const

    def __str__(self):
        return self.const

    # def __cmp__(self, other):
    #     return cmp(self.const, other.const)

    def __lt__(self, other):
        """Implement <."""
        return self.const < other.const

    def __le__(self, other):
        """Implement <=."""
        return self.const <= other.const

    def __eq__(self, other):
        """Implement ==."""
        return self.const == other.const

    def __ne__(self, other):
        """Implement !=."""
        return self.const != other.const

    def __gt__(self, other):
        """Implement >."""
        return self.const > other.const

    def __ge__(self, other):
        """Implement >=."""
        return self.const >= other.const


class PropMeta(object):
    def __init__(self, typeClassName, name, moPropName, propId, category):
        self.typeClass = typeClassName  # Load this dynamically
        self.name = name
        self.moPropName = moPropName
        self.id = None
        self.category = category
        self.help = None
        self.label = None
        self.unit = None
        self.defaultValue = None
        self.range = None
        # A field without a default value, when reported in the XML
        # format if present, will anyway be represented with '', this
        # field needs to match that representation, hence an empty
        # string is used
        self.defaultValueStr = ''

        self.isDn = False
        self.isRn = False
        self.isConfig = False
        self.isImplicit = False
        self.isOper = False
        self.isAdmin = False
        self.isCreateOnly = False
        self.isNaming = False
        self.isStats = False
        self.isPassword = False
        self.needDelimiter = False

        self.constants = {}
        self.constsToLabels = {}
        self.labelsToConsts = {}

        self._validators = []

    @staticmethod
    def makeValue(value):
        return value

    def isValidValue(self, value):
        if not self._validators:
            return True
        for propValidator in self._validators:
            if propValidator.isValidValue(value):
                return True
        return False

    def _addConstant(self, const, label, value):
        self.constants[const] = Constant(const, label, value)
        self.constsToLabels[const] = label
        self.labelsToConsts[label] = const

    def _addValidator(self, validator):
        self._validators.append(validator)

    def __str__(self):
        return self.name

    # def __cmp__(self, other):
    #     return cmp(self.name, other.name)

    def __lt__(self, other):
        """Implement <."""
        return self.name < other.name

    def __le__(self, other):
        """Implement <=."""
        return self.name <= other.name

    def __eq__(self, other):
        """Implement ==."""
        return self.name == other.name

    def __ne__(self, other):
        """Implement !=."""
        return self.name != other.name

    def __gt__(self, other):
        """Implement >."""
        return self.name > other.name

    def __ge__(self, other):
        """Implement >=."""
        return self.name >= other.name

    def __hash__(self):
        return hash(self.name)
