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
from builtins import object

import importlib
from .naming import Dn
from .request import DnQuery, ClassQuery
from ._query import DnQueryProc, ClassQueryProc

# Load the top root class dynamically from the cobra model runtime
topRoot = importlib.import_module('cobra.model.top')
topRoot = getattr(topRoot, 'Root')


class Mit(object):
    """

    """
    QueryDepth = {
        'self': 0,
        'children': 1,
        'subtree': -1
    }

    def __init__(self):
        self.__rootMo = topRoot(Dn())
        self.__classIndex = dict()
        self.__dnIndex = dict()
        self.__deletedIndex = dict()
        self.__updateIndex(self.__rootMo, None)
        self.__index = 0

    def __iter__(self):
        return iter(list(self.__dnIndex.values()))

    @property
    def rootMo(self):
        return self.__rootMo

    def __updateIndex(self, mo, parentMo):
        # Add the root mo to the class/dn index
        self.__updateClassIndex(mo)
        self.__updateDnIndex(mo)
        if parentMo and parentMo.status.deleted:
            mo.delete()
        if mo.status.deleted:
            self.__deletedIndex[mo.dn] = mo

    def add(self, moSrc):
        # Check if the ancestor is deleted in the mit
        deletedAncestorDn = self.__hasDeletedAncestor(moSrc.dn.getParent())
        if deletedAncestorDn is not None:
            raise ValueError('Ancestor "{0}" is deleted'.format(str(deletedAncestorDn)))
        self.__add(moSrc)

    def __add(self, moSrc):
        # Update the MIT with this new mo and its subtree, All mos will be added
        # to the class and dn index.
        moDst = self.__dnIndex.get(moSrc.dn, None)
        if moDst is None:
            parentMo = self.__makeParent(moSrc.dn)
            moDst = moSrc.clone(parentMo, depth=1)
            self.__updateIndex(moDst, parentMo)
        elif id(moSrc) != id(moDst):
            moDst.update(moSrc)
            if moDst.status.deleted:
                self.__updateSubtreeStatus(moDst)
            else:
                # Remove it from deleted index if present
                if moDst.dn in self.__deletedIndex:
                    del self.__deletedIndex[moDst.dn]

        for childMo in moSrc.children:
            if moSrc.status.deleted:
                childMo.delete()
            self.__add(childMo)

    def __hasDeletedAncestor(self, dn):
        if dn in self.__deletedIndex:
            return dn
        if dn.isRoot:
            return None
        return self.__hasDeletedAncestor(dn.getParent())

    def __updateSubtreeStatus(self, mo):
        self.__deletedIndex[mo.dn] = mo
        for childMo in mo.children:
            self.__updateSubtreeStatus(childMo)
            childMo.delete()

    def getMoByDn(self, dn):
        mo = self.__dnIndex.get(dn, None)
        return [mo] if mo is not None else []

    def getMoByClass(self, moClassNames):
        if not isinstance(moClassNames, list):
            moClassNames = [moClassNames]
        moSet = set()
        for moClassName in moClassNames:
            moClassSet = self.__classIndex.get(moClassName, set())
            moSet.update(moClassSet)
        return list(moSet)

    def query(self, queryObj):
        qTable = {
            DnQuery: DnQueryProc,
            ClassQuery: ClassQueryProc
        }
        qProcClass = qTable[queryObj.__class__]
        qProc = qProcClass(queryObj)
        return qProc.process(self, [])

    def isMoDeleted(self, mo):
        return mo.dn in self.__deletedIndex

    def remove(self, mo):
        raise NotImplementedError()

    def __updateClassIndex(self, newMo):
        def __updateClassHierarchy(classIndex, currentClass, indexedMo):
            className = currentClass.meta.moClassName
            moSet = classIndex.get(className, set())
            moSet.add(indexedMo)
            classIndex[className] = moSet

            for superClass in currentClass.meta.superClasses:
                __updateClassHierarchy(classIndex, superClass, indexedMo)

        # BEWARE: This method must be called ONLY for the new mos that
        # do not exist in the mit
        moClass = newMo.__class__
        __updateClassHierarchy(self.__classIndex, moClass, newMo)

    def __updateDnIndex(self, newMo):
        # BEWARE: This method must be called ONLY for the new mos that
        # do not exist in the mit
        self.__dnIndex[newMo.dn] = newMo

    def __makeParent(self, dn):
        parentDn = dn.getParent()
        parentMo = self.__dnIndex.get(parentDn, None)
        if parentMo is not None:
            return parentMo

        grandParentMo = self.__makeParent(parentDn)
        parentMo = self.__makeMo(grandParentMo, parentDn)

        # New parent, please add it to your index
        self.__updateIndex(parentMo, grandParentMo)
        return parentMo

    @staticmethod
    def __makeMo(parentMo, dn):
        klass = dn.moClass
        namingVals = list(dn.rn().namingVals)
        return klass(parentMo, markDirty=False, *namingVals)
