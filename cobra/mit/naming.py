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

from past.builtins import cmp
from builtins import next
from builtins import str
from builtins import object

from cobra.mit.meta import ClassLoader
from collections import deque


class Rn(object):
    """The relative name (Rn) of the managed object (MO).
    
    You can use Rn to convert between Rn of an MO its constituent naming
    values. The string form of Rn is {prefix}{val1}{prefix2}{Val2} (...)
    
    Note:
      The naming value is enclosed in brackets ([]) if the meta object
      specifies that properties be delimited.

    Attributes:
      namingVals (tupleiterator): An interator for the naming values - readonly

      meta (cobra.mit.meta.ClassMeta): The class meta for this Rn - readonly
      
      moClass (cobra.mit.mo.Mo): The class of the Mo for this Rn - readonly
    """

    @classmethod
    def fromString(cls, classMeta, rnStr):
        """Create a relative name instance from a string and classMeta

        Args:
          classMeta (cobra.mit.meta.ClassMeta): class meta of the mo class
          rnStr (str): string form of the Rn

        Raises:
          ValueError: If the Rn prefix is not valid or the Rn does not follow
            the proper rnFormat

        Returns:
          cobra.mit.naming.Rn: The Rn object
        """
        def findBalancedPropDelims(rn, start):
            stk = deque()
            first = True
            end = start
            # loop through the rnStr looking for [ and append them to the deque
            # and ] and pop them off the deque, once things are balanced return
            # that character as the end of the Rn.
            while end < len(rn):
                if not first and len(stk) == 0:
                    return end
                symbol = rn[end]
                if symbol == "[":
                    if first and len(stk) == 0:
                        first = False
                    stk.append(symbol)
                elif symbol == "]":
                    if first and len(stk) == 0:
                        raise ValueError("Invalid Rn: Found closing prop " +
                                         "delimiter before opening prop " +
                                         "delimiter.")
                    else:
                        stk.pop()
                end += 1
            return -1

        def parseNamingProps(meta, rn):
            rnFormat = meta.rnFormat
            if not len(meta.namingProps):
                if rn == rnFormat:
                    return []
                else:
                    raise ValueError('rn prefix mismatch')

            nPropVals = []
            rnLen = len(rn)
            end = 0
            start = 0
            propMetaIter = iter(meta.namingProps)
            needPropDelimiter = False
            nPropMeta = None
            for rnPrefix, hasProp in meta.rnPrefixes:
                if start > end:
                    # Parse the naming prop value
                    if needPropDelimiter:
                        end = findBalancedPropDelims(rn, start)
                    else:
                        end = rnStr.find(rnPrefix, start)

                    if end == -1:
                        raise ValueError("rn prefix '%s' not found in '%s'" %
                                         (rnPrefix, rn))
                    nPropVal = rn[start:end]
                    if needPropDelimiter:
                        nPropVal = nPropVal[1:-1]
                    if nPropMeta:
                        nPropVals.append(nPropVal)
                    start = end

                # Find the rn prefix
                if not rn.startswith(rnPrefix, start):
                    raise ValueError('rn "%s" must be %s' % (rn, rnFormat))

                if hasProp:
                    nPropMeta = next(propMetaIter)
                    needPropDelimiter = nPropMeta.needDelimiter

                start += len(rnPrefix)
            end = rnLen
            nPropVal = rn[start:end]
            if needPropDelimiter:
                nPropVal = nPropVal[1:-1]
            if nPropMeta:
                nPropVals.append(nPropVal)
            return nPropVals

        namingVals = parseNamingProps(classMeta, rnStr)
        return Rn(classMeta, *namingVals)

    def __init__(self, classMeta, *namingVals):
        """Initalize a Rn object

        Args:
          classMeta (cobra.mit.meta.ClassMeta): class meta of the mo class
          **namingVals: The naming values for the Rn
        """
        self.__namingVals = namingVals
        self.__meta = classMeta
        self.__rnStr = None

    @property
    def namingVals(self):
        return iter(self.__namingVals)

    @property
    def meta(self):
        return self.__meta

    @property
    def moClass(self):
        return self.__meta.getClass()

    def __cmp__(self, other):
        """
        compares two rn objects using the natural ordering of their naming
        values

        :param other: other rn being compared
        :type other: :py:class:`cobra.mit.naming.Rn`

        :returns: 0 if equal, > 0 if self is greater and < 0 if self is smaller
        :rtype: int
        """
        selfRnStr = str(self)
        otherRnStr = str(other)
        return cmp(selfRnStr, otherRnStr)

    def __str__(self):
        """
        Returns the string form of the Rn

        :returns: string form of the Rn
        :rtype: str
        """
        if not self.__rnStr:
            self.__rnStr = self.__makeRnStr()
        return self.__rnStr

    def __hash__(self):
        """
        Returns the hash code for the Rn

        :returns: hash code for the Rn
        :rtype: int
        """
        return hash(str(self))

    def __makeRnStr(self):
        if self.__meta.namingProps:
            namingProps = {}
            namingValsIter = iter(self.__namingVals)
            for propMeta in self.__meta.namingProps:
                namingProps[propMeta.name] = next(namingValsIter)
            return self.__meta.rnFormat % namingProps
        else:
            return self.__meta.rnFormat


class Dn(object):
    """
    The distinguished name (Dn) uniquely identifies a managed object (MO).
    A Dn is an ordered list of relative names, such as:

    dn = rn1/rn2/rn3/....

    In this example, the Dn provides a fully qualified path for **user-john**
    from the top of the Mit to the Mo.

    dn = "uni/userext/user-john"
    
    Attributes:
      rns (listiterator): Iterator for all the rns from topRoot to the target
        Mo

      meta (cobra.mit.meta.ClassMeta): class meta of the mo class for this Dn

      moClass (cobra.mit.mo.Mo): Mo class for this Dn

      contextRoot (cobra.mit.mo.Mo): The context root for this Dn
    """

    def __init__(self, rns=None):
        """Initialize a Dn instance from list of Rn objects.

        Args:
          rns (list): list of Rns
        """
        self.__dnStr = None
        self.__rns = []
        self.__class = ClassLoader.loadClass('cobra.model.top.Root')
        self.__meta = self.__class.meta
        if rns is None:
            rns = []
        for rn in rns:
            self.appendRn(rn)

    @property
    def rns(self):
        return iter(self.__rns)

    @property
    def meta(self):
        return self.__meta

    @property
    def moClass(self):
        return self.__class

    @property
    def contextRoot(self):
        for rn in reversed(self.__rns):
            if rn.meta.isContextRoot:
                return rn.meta
        return None

    @classmethod
    def fromString(cls, dnStr):
        """Create a distingushed name instance from a dn string

        Parses the dn string into its constituent Rn strings and creates the Rn
        objects.

        Args:
          dnStr (str): string form of Dn

        Raises:
          ValueError: If an Rn in the Dn is found to not be consistent with the
            ACI model

        Returns (cobra.mit.naming.Dn): The Dn instance
        """
        rnStrs = cls.__splitDnStr(dnStr)
        newDn = Dn()
        pMeta = newDn.meta
        for rnStr in rnStrs:
            rnMeta = cls.__findChild(pMeta, rnStr)
            if rnMeta is None:
                raise ValueError("Dn '%s' cannot contain '%s'" %
                                 (str(newDn), rnStr))
            rn = Rn.fromString(rnMeta, rnStr)
            newDn.appendRn(rn)
            pMeta = rnMeta
        return newDn

    @classmethod
    def findCommonParent(cls, dns):
        """Find the common parent for the given set of dn objects.

        Args:
          dns (list): The Dn objects to find the common parent of

        Returns:
          cobra.mit.naming.Dn: Dn object of the common parent if any, else Dn
            for topRoot
        """
        def allRnsEqual(allDns, i):
            firstRn = None
            for eachDn in allDns:
                currentRn = eachDn.__rns[i]
                if firstRn is None:
                    firstRn = currentRn
                else:
                    if firstRn != currentRn:
                        return False

            # All Rns at this level are equal
            return True

        if not dns:
            return None
        elif len(dns) == 1:
            return dns[0]

        index = 0
        maxLen = min([len(dn.__rns) for dn in dns])
        while index < maxLen:
            if allRnsEqual(dns, index):
                index += 1
            else:
                break
        if index == 0:
            return Dn()
        rns = dns[0].__rns
        return Dn(rns[:index])

    def rn(self, index=None):
        """Get a Rn at a specified index
        
        If index is None, then the Rn of the target Mo is returned

        Args:
          index (None or int): index of the Rn object, this must be between
            0 and the length of the Dn (i.e. number of Rns) or None. The
            default is None

        Returns (cobra.mit.naming.Rn): Rn object at the specified index
        """
        if index is None:
            return self.__rns[-1]
        return self.__rns[index]

    def getAncestor(self, level):
        """Get the ancestor Dn based on the number of levels

        Args:
          level (int): number of levels

        Returns:
          cobra.mit.naming.Dn: The Dn object of the ancestor as specified by
          the level argument
        """
        rns = self.__rns[:-level]
        return Dn(rns)

    def getParent(self):
        """Get the parent Dn of the current Dn
        
        Same as::

            self.getAncetor(1)

        Returns:
          cobra.mit.naming.Dn: Dn object of the immediate parent
        """
        return self.getAncestor(1)

    def clone(self):
        """Get a new copy of this Dn

        Returns:
          cobra.mit.naming.Dn: Copy of this Dn
        """
        newDn = Dn()
        for rn in self.__rns:
            newDn.appendRn(rn)
        return newDn

    def appendRn(self, rn):
        """ Append an Rn to this Dn
        
        Note:
          This changes the target MO

        Args:
          rn (cobra.mit.naming.Rn): The Rn to append to this Dn

        Raises:
          ValueError: If the Dn can not contain the Rn
        """
        rnClassName = rn.meta.className
        if rnClassName == 'cobra.model.top.Root':
            return
        if rnClassName not in self.__meta.childClasses:
            className = str(self.meta.className)
            raise ValueError("'%s' cannot contain '%s'" % (className,
                                                           str(rnClassName)))
        self.__rns.append(rn)
        self.__meta = rn.meta
        self.__class = rn.moClass
        self.__dnStr = None

    def isDescendantOf(self, ancestorDn):
        """Check if a Dn is a descendant of this Dn

        Args:
          ancestorDn (cobra.mit.naming.Dn): Dn being compared for descendants

        Returns:
          boo: True if this Dn is a descendant of the other Dn else False
        """
        ansDnStr = str(ancestorDn)
        dnStr = str(self)
        return (dnStr != ansDnStr and len(self) > len(ancestorDn) and
                dnStr.startswith(ansDnStr))

    def isAncestorOf(self, descendantDn):
        """ Check if a Dn is an ancestor of this Dn

        Args:
          descendantDn (cobra.mit.naming.Dn): Dn being compared for ancestary

        Returns:
          bool: True if this Dn is an ancestor of the other Dn else False
        """
        return descendantDn.isDescendantOf(self)

    def __len__(self):
        """ Get the length of the Dn
        
        The length is the number of Rns in this Dn

        Returns:
          int: number of rns in the dn
        """
        return len(self.__rns)

    def __str__(self):
        """Get the string form of this Dn

        Returns:
          str: string form of the Dn
        """
        if not self.__dnStr:
            self.__dnStr = self.__makeDn()
        return self.__dnStr

    def __cmp__(self, other):
        """ Compare two Dn objects using the natural ordering of their Rns

        Args:
        other (cobra.mit.naming.Dn): other Dn being compared

        Returns:
          int: 0 if equal, > 0 if self is greater and < 0 if self is smaller
        """
        return cmp(str(self), str(other))

    def __hash__(self):
        """Get the hash code for the Dn

        Returns:
          int: hash code for the Dn
        """
        return hash(str(self))

    def __makeDn(self):
        rnStrs = []
        for rn in self.__rns:
            rnStrs.append(str(rn))
        return '/'.join(rnStrs)

    @classmethod
    def __splitDnStr(cls, dnStr):
        rnStrs = []
        rnStr = ""
        delimCount = 0
        for dnChar in dnStr:
            if delimCount == 0 and dnChar == '/':
                # Found rn string, eat the char and capture the Rn
                if rnStr:
                    rnStrs.append(rnStr)
                rnStr = ""
            elif dnChar == '[':
                delimCount += 1
                rnStr += dnChar
            elif dnChar == ']':
                delimCount -= 1
                rnStr += dnChar
            else:
                rnStr += dnChar
        if rnStr:
            rnStrs.append(rnStr)
        if delimCount != 0:
            raise ValueError("Invalid dn '%s' with unbalanced delimiters" %
                             dnStr)
        return rnStrs

    @classmethod
    def __findChild(cls, pMeta, rnStr):
        # This method assumes that the childNamesAndRnPrefix in the meta
        # is sorted with longest prefix first. This will allow us to match
        # child prefixes that are sub strings. For example 'ac' and 'action'
        # where the list will have 'action' first and then 'ac'. This way
        # it is guaranteed that the longest prefix is matched first
        for childClassName, childRnPrefix in pMeta.childNamesAndRnPrefix:
            if rnStr.startswith(childRnPrefix):
                childClass = pMeta.childClasses[childClassName]
                return childClass.meta
        return None
