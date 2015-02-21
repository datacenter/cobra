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

from cobra.mit.meta import ClassLoader
from collections import deque


class Rn(object):
    """
    The Rn class is the relative name (Rn) of the managed object (MO). 
    You can use Rn to convert between Rn of an MO its constituent naming values.
    The string form of Rn is {prefix}{val1}{prefix2}{Val2} (...)
    Note: The naming value is enclosed in brackets ([]) if the meta object 
    specifies that properties be delimited.
    """

    @classmethod
    def fromString(cls, classMeta, rnStr):
        """
        Create a relative name object from the string form given the class meta

        :param classMeta: class meta of the mo class
        :type classMeta: cobra.mit.meta.ClassMeta

        :param rnStr: string form of rn
        :type rnStr: str

        :returns: Rn object
        :rtype: cobra.mit.naming.Rn
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
                    nPropMeta = propMetaIter.next()
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
        """
        Relative Name (Rn) of the Mo from class meta and list of naming values

        :param classMeta: class meta of the mo class
        :type classMeta: cobra.mit.meta.ClassMeta

        :param namingVals: list of naming values
        :type namingVals: list
        """
        self.__namingVals = namingVals
        self.__meta = classMeta
        self.__rnStr = None

    @property
    def namingVals(self):
        """
        Iterator of naming values for this rn

        :returns: iterator of the naming values for this rn
        :rtype: iterator
        """
        return iter(self.__namingVals)

    @property
    def meta(self):
        """
        class meta of the mo class for this Rn

        :returns: class meta of the mo for this Rn
        :rtype: cobra.mit.meta.ClassMeta
        """
        return self.__meta

    @property
    def moClass(self):
        """
        Mo class for this Rn

        :returns: Mo class for this Rn
        :rtype: cobra.mit.mo.Mo
        """
        return self.__meta.getClass()

    def __cmp__(self, other):
        """
        compares two rn objects using the natural ordering of their naming
        values

        :param other: other rn being compared
        :type other: cobra.mit.naming.Rn

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
                namingProps[propMeta.name] = namingValsIter.next()
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
    """

    @classmethod
    def fromString(cls, dnStr):
        """
        Create a Dn from the string form of Dn. This method parses the dn
        string into its constituent Rn strings and creates the Rn objects.

        :param dnStr: string form of Dn
        :type dnStr: str

        :returns: Dn object
        :rtype: cobra.mit.naming.Dn
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
        """
        Find the common parent for the given set of dn objects.

        :param dns: list of Dn objects
        :type dns: list

        :returns: Dn object of the common parent if any, else Dn for topRoot
        :rtype: cobra.mit.naming.Dn
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

    def __init__(self, rns=None):
        """
        Create a Dn from list of Rn objects.

        :param rns: list of Rns
        :type rns: list
        """
        self.__dnStr = None
        self.__rns = []
        self.__class = ClassLoader.loadClass('cobra.model.top.Root')
        self.__meta = self.__class.meta
        if rns is None:
            rns = []
        for rn in rns:
            self.appendRn(rn)

    def rn(self, index=None):
        """
        Returns the Rn object at the specified index. If index is None, then
        the Rn of the target Mo is returned

        :param index: index of the Rn object, this must be betwee 0 and the
                      length of the Dn
        :type index: int

        :returns: Rn object at the specified index
        :rtype: cobra.mit.naming.Rn
        """
        if index is None:
            return self.__rns[-1]
        return self.__rns[index]

    def getAncestor(self, level):
        """
        Returns the ancestor Dn based on the number of levels

        :param level: number of levels
        :type level: int

        :returns: Dn object of the ancestor as specified by the level param
        :rtype: cobra.mit.naming.Dn
        """
        rns = self.__rns[:-level]
        return Dn(rns)

    def getParent(self):
        """
        Returns the parent Dn, same as::
            self.getAncetor(1)

        :returns: Dn object of the immediate parent
        :rtype: cobra.mit.naming.Dn
        """
        return self.getAncestor(1)

    @property
    def rns(self):
        """
        Iterator for all the rns from topRoot to the target Mo

        :returns: iterator of Rns in this Dn
        :rtype: iterator
        """
        return iter(self.__rns)

    @property
    def meta(self):
        """
        class meta of the mo class for this Dn

        :returns: class meta of the mo for this Dn
        :rtype: cobra.mit.meta.ClassMeta
        """
        return self.__meta

    @property
    def moClass(self):
        """
        Mo class for this Dn

        :returns: Mo class for this Dn
        :rtype: cobra.mit.mo.Mo
        """
        return self.__class

    @property
    def contextRoot(self):
        for rn in reversed(self.__rns):
            if rn.meta.isContextRoot:
                return rn.meta
        return None

    def clone(self):
        """
        Return a new copy of this Dn

        :returns: copy of this Dn
        :rtype: cobra.mit.naming.Dn
        """
        newDn = Dn()
        for rn in self.__rns:
            newDn.appendRn(rn)
        return newDn

    def appendRn(self, rn):
        """
        Appends an Rn to this Dn, changes the target Mo
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
        """
        Return True if this Dn is a descendant of the other Dn

        :param ancestorDn: Dn being compared for ancestory
        :type ancestorDn: cobra.mit.naming.Dn

        :returns: True if this Dn is a descendant of the other Dn else False
        :rtype: boolean
        """
        ansDnStr = str(ancestorDn)
        dnStr = str(self)
        return (dnStr != ansDnStr and len(self) > len(ancestorDn) and
                dnStr.startswith(ansDnStr))

    def isAncestorOf(self, descendantDn):
        """
        Return True if this Dn is an ancestor of the other Dn

        :param descendantDn: Dn being compared for descendants
        :type descendantDn: cobra.mit.naming.Dn

        :returns: True if this Dn is an ancestor of the other Dn else False
        :rtype: boolean
        """
        return descendantDn.isDescendantOf(self)

    def __len__(self):
        """
        Returns the number of Rns in this Dn

        :returns: number of rns in the dn
        :rtype: int
        """
        return len(self.__rns)

    def __str__(self):
        """
        Returns the string form of the Dn

        :returns: string form of the Dn
        :rtype: str
        """
        if not self.__dnStr:
            self.__dnStr = self.__makeDn()
        return self.__dnStr

    def __cmp__(self, other):
        """
        compares two Dn objects using the natural ordering of their Rns

        :param other: other Dn being compared
        :type other: cobra.mit.naming.Dn

        :returns: 0 if equal, > 0 if self is greater and < 0 if self is smaller
        :rtype: int
        """
        return cmp(str(self), str(other))

    def __hash__(self):
        """
        Returns the hash code for the Dn

        :returns: hash code for the Dn
        :rtype: int
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
