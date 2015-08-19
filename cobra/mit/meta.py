
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

"""The meta module for the ACI Python SDK (cobra)."""

from builtins import str     # pylint:disable=redefined-builtin
from builtins import next    # pylint:disable=redefined-builtin
from builtins import object  # pylint:disable=redefined-builtin

import importlib


class Category(object):

    """Category class for Managed Object (MO) class meta or property meta.

    Used to classify MOs or MO properties into various categories. The
    categories are defined in the ACI model package for ever MO property.
    """

    def __init__(self, name, categoryId):
        """Initialize a MO property category.

        Args:
          name (str): The name of the category
          categoryId (int): The integer representing the category id
        """
        self.name = name
        self.id = categoryId  # pylint:disable=invalid-name

    def __str__(self):
        """Implement str()."""
        return self.name

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


class ClassLoader(object):

    """Import a class by name.

    A convenience class to import classes from a string containing the class
    name
    """

    @classmethod
    def loadClass(cls, fqClassName):
        """Load a class from a fully qualified name.

        Args:
          fqClassName (str): A fully qualified class name as in
            package.module.class.  For example: cobra.model.pol.Uni

        Returns:
          cobra.mit.mo.Mo: The imported class
        """
        fqClassName = str(fqClassName)
        moduleName, className = fqClassName.rsplit('.', 1)
        module = importlib.import_module(moduleName)
        return getattr(module, className)


# pylint:disable=too-many-instance-attributes
class ClassMeta(object):

    """Represents a classes metadata.

    Attributes:
      className (str): The class name for the meta

      moClassName (None or str): The class name for the MO

      label (str): The label for the class meta

      category (None or cobra.mit.meta.Category): The class category

      isAbstract (bool): True if the class is abstract, False otherwise

      isRelation (bool): True if the class is a relationship object, False
        otherwise

      isSource (bool): True if the class is a source relationship object, False
        otherwise

      isExplicit (bool): True if the object is an explicit relationship, False
        if the object forms an indirect named relationship

      isNamed (bool): True if the object is a named source relationship object,
        False otherwise

      writeAccessMask (long): The write permissions for this class

      readAccessMask (long): The read permissions for this class

      isDomainable (bool): True if the MO is domainable, False otherwise

      isReadOnly (bool): True if the MO is readonly, False otherwise

      isConfigurable (bool): True if the MO can be configured, False
        otherwise

      isDeletable (bool): True if the MO can be deleted

      isContextRoot (bool): True if the MO is the context root

      concreteSubClasses (cobra.mit.meta.ClassMeta._ClassContainer): A
        container that keeps track of all the subclasses that are concrete

      superClasses (cobra.mit.meta.ClassMeta._ClassContainer): A container
        that keeps track of all the super classes

      childClasses (cobra.mit.meta.ClassMeta._ClassContainer): A container
        that keeps track of the actual child classes

      childNamesAndRnPrefix (list of tuples): A list containing tuples where
        the first element is the child name and the second element is the rn
        prefix

      parentClasses (cobra.mit.meta.ClassMeta._ClassContainer): A container
        that keeps track of the actual parent classes

      props (cobra.mit.meta._PropContainer): A container that keeps track of
        all of the classes properties

      namingProps (list): A list containing :class:`cobra.mit.meta.PropMeta`
        for each property that is a naming property.

      rnFormat (None or str): A string representing the relative name format

      rnPrefixes (list of tuples): The relative name prefixes where the first
        element in the tuple is the rn prefix and the second element is a bool
        where True means the prefix has naming properties and False otherwise.

      ctxRoot (None or cobra.mit.mo.Mo): The context root for this class.
    """

    def __init__(self, className):
        """Initialize a ClassMeta instance.

        Args:
          className (str): The class name for this meta object
        """
        self.className = className
        self.moClassName = None
        self.label = None
        self.category = None

        self.isAbstract = False
        self.isRelation = False
        self.isSource = False
        self.isExplicit = False
        self.isNamed = False

        self.writeAccessMask = 0
        self.readAccessMask = 0
        self.isDomainable = False
        self.isReadOnly = False
        self.isConfigurable = False
        self.isDeletable = False
        self.isContextRoot = False

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

    def getClass(self):
        """Use the className to import the class for this meta object.

        Returns:
          mixed: The imported class for this meta object
        """
        return ClassLoader.loadClass(self.className)

    def hasContextRoot(self):
        """Check if the meta has a context root.

        Returns:
          boo: True if the meta has a context root and False otherwise
        """
        ctxRoot = self.getContextRoot()
        return ctxRoot and ctxRoot != self

    def getContextRoot(self, pStack=None):
        """Get the meta's context root.

        Args:
          pStack (set): The parent stack

        Returns:
          None or cobra.mit.mo.Mo: The class of the context root
        """
        if pStack is None:
            pStack = set()
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

    class _ClassContainer(object):

        """A class that defines a container for Mo classes."""

        class LazyIter(object):

            """A class that defines an iterator that has a lazy nature."""

            def __init__(self, container):
                self._container = container
                self._classNames = iter(container.names)

            def __next__(self):
                nextClassName = next(self._classNames)
                return self._container[nextClassName]

            def __iter__(self):  # pylint:disable=non-iterator-returned
                return self

        @property
        def names(self):
            """Get the list of class names contained by the class container."""
            return list(self._classes.keys())

        def add(self, className):
            """Add a class to the class container.

            Args:
              className (str): The name of the class to add to the container.
            """
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

        def __iter__(self):  # pylint:disable=non-iterator-returned
            # pylint:disable=protected-access
            return ClassMeta._ClassContainer.LazyIter(self)

    class _PropContainer(object):

        """A class that defines a container for Mo properties."""

        def __init__(self):
            self._props = {}

        def add(self, propName, propMeta):
            """Add a property to the property container.

            Args:
              propName (str): The name of the property.
              propMeta (cobra.mit.meta.PropMeta): The property meta object.
            """
            self._props[propName] = propMeta

        @property
        def names(self):
            """Get the list of property names.

            Returns:
              list: The list of property names in the property container.
            """
            return list(self._props.keys())

        def __getitem__(self, propName):
            return self._props[propName]

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


class SourceRelationMeta(ClassMeta):

    """The meta data for a source object in a relationship."""

    # Cardinality constants
    ONE_TO_ONE = object()
    ONE_TO_M = object()
    N_TO_ONE = object()
    N_TO_M = object()

    def __init__(self, className, targetClassName):
        """Initialize a source relationship meta object.

        Args:
          className (str): The source Mo class name for the relationship
          targetClassName (str): The target class name for the relationship
        """
        ClassMeta.__init__(self, className)
        self.targetClassName = targetClassName
        self.cardinality = None
        self.isRelation = True
        self.isSource = True
        self.isExplicit = True

    def getTargetClass(self):
        """Import and returns the target class for a relationship.

        Returns:
          cobra.mit.mo.Mo: The target class
        """
        return ClassLoader.loadClass(self.targetClassName)


class NamedSourceRelationMeta(SourceRelationMeta):

    """The meta data for a named source relationship object."""

    def __init__(self, className, targetClassName):
        """Initialize a named source relationship meta object.

        Args:
          className (str): The source Mo class name for the relationship
          targetClassName (str): The target class name for the relationship
        """
        SourceRelationMeta.__init__(self, className, targetClassName)
        self.targetNameProps = {}
        self.isExplicit = False
        self.isNamed = True


class TargetRelationMeta(ClassMeta):

    """The meta data for a target object in a relationship."""

    def __init__(self, className, sourceClassName):
        """Initialize a target relationship meta object.

        Args:
          className (str): The target Mo class name for the relationship
          sourceClassName (str): The source class name for the relationship
        """
        ClassMeta.__init__(self, className)
        self.sourceClassName = sourceClassName
        self.isRelation = True
        self.isTarget = True

    def getSourceClass(self):
        """Import and return the source class.

        Returns:
          cobra.mit.mo.Mo: The source class
        """
        return ClassLoader.loadClass(self.sourceClassName)


class Constant(object):

    """A class to represent constants for properties."""

    def __init__(self, const, label, value):
        """Initialize a constant object.

        Args:
          const (str): The constant string that can be used for the property
          label (str): The label for this constant
          value (int): The value for this constant
        """
        self.value = value
        self.label = label
        self.const = const

    def __str__(self):
        """Implement str()."""
        return self.const

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


# pylint:disable=too-many-instance-attributes
class PropMeta(object):

    """The meta data for properties of managed objects.

    Attributes:
      typeClass (str): The class of the property

      name (str): The name of the property

      moPropName (str): The managed object property name

      id (None or int): The property id

      category (cobra.mit.meta.Category): The property category object

      help (None or str): The help string for the property

      label (None or str): The label for the property

      unit (None or str): The units the property is in

      defaultValue (None or str): The default value for the property

      isDn (bool): True if the property is a distingushed name, False otherwise

      isRn (bool): True if the property is a relative name, False otherwise

      isConfig (bool): True if the property is a configuration property, False
        otherwise

      isImplicit (bool): True if the property is implicitly defined, False
        otherwise

      isOper (bool): True if the property is an operations property, False
        otherwise

      isAdmin (bool): True if the property is an admin property, False
        otherwise

      isCreateOnly (bool): True if the property can only be set when the MO is
        created, False otherwise

      isNaming (bool): True if the property is a naming property, False
        otherwise

      isStats (bool): True if the property is a stats property, False otherwise

      isPassword (bool): True if the property is a password property, False
        otherwise

      needDelimiter (bool): True if the property needs delimiters, False
        otherwise

      constants (dict of cobra.mit.meta.Constants): A dictionary where the keys
        are the constants const and the values are the constants objects

      constsToLabels (dict): A dictionary mapping the properties constants
        consts to the constants label

      labelsToConsts (dict): A dictionary mapping the properties constants
        labels to the constants consts
    """

    # pylint:disable=too-many-arguments
    def __init__(self, typeClassName, name, moPropName, propId, category):
        """Initialize a PropMeta instance.

        Args:
          typeClassName (str): The class for the type of python object that
            should be used to represent this property
          moPropName (str): The managed object property name
          propId (int): The property Id number
          category (cobra.mit.meta.Category): The property category
        """
        self.typeClass = typeClassName  # Load this dynamically
        self.name = name
        self.moPropName = moPropName
        self.id = propId  # pylint:disable=invalid-name
        self.category = category
        self.help = None
        self.label = None
        self.unit = None
        self.defaultValue = None
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
        """
        Create a property using a value.

        Args:
          value (str): The value to set the property to

        Returns:
          str: The value
        """
        return value

    def isValidValue(self, value):
        """Check a value against the validators in the meta.

        Args:
          value (str): The value to check

        Returns:
          bool: True if the value is valid for this property or False otherwise
        """
        if not self._validators:
            return True
        for propValidator in self._validators:
            if propValidator.isValidValue(value):
                return True
        return False

    def _addConstant(self, const, label, value):
        """Add a constant to the constants list.

        Args:
          const (str): The string that uniquely identifies the constant.
          label (str): The label for the constant.
          value:  The value the const is defined to represent.
        """
        self.constants[const] = Constant(const, label, value)
        self.constsToLabels[const] = label
        self.labelsToConsts[label] = const

    def _addValidator(self, validator):
        """Append a validator to the validators list.

        Not currently used.

        Args:
          validator: A validator for the property.
        """
        self._validators.append(validator)

    def __str__(self):
        """Implement str()."""
        return self.name

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
        """Implement hash()."""
        return hash(self.name)
