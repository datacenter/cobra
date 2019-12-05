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

# import sys
# if sys.version_info[0] == 3:
from builtins import object

import importlib


class QueryProc(object):
    def __init__(self, query):
        self._query = query
        self._filterParser = self.__makeFilterParser()

    def process(self, mit, moList):
        raise NotImplementedError()

    @staticmethod
    def __makeFilterParser():
        filterMod = importlib.import_module('cobra.mit._filter')
        return getattr(filterMod, 'filterParser')


class QueryTargetProc(QueryProc):
    def __init__(self, query):
        super(QueryTargetProc, self).__init__(query)
        self.__procTable = {
            None: self.selfProc,
            'self': self.selfProc,
            'children': self.childrenProc,
            'subtree': self.subtreeProc
        }
        classes = query.classFilter
        self.__queryClassList = classes.split(',') if classes is not None else []
        self.__propFilter = self._filterParser.from_string(query.propFilter) if query.propFilter is not None else None
        self.__respProc = ResponseQueryProc(self._query)

    def process(self, mit, moList):
        proc = self.__procTable[self._query.queryTarget]
        return proc(moList)

    def selfProc(self, moList):
        mos = []
        for mo in moList:
            mos.extend(self.__doRespProcess(mo))
        return mos

    def childrenProc(self, moList):
        mos = []
        for mo in moList:
            for childMo in mo.children:
                mos.extend(self.__doRespProcess(childMo))
        return mos

    def subtreeProc(self, moList):
        mos = []
        for mo in moList:
            self.__subtreeProc(mo, mos)
        return mos

    def __subtreeProc(self, mo, resultMoList):
        procMos = self.__doRespProcess(mo)
        resultMoList.extend(procMos)
        for childMo in mo.children:
            self.__subtreeProc(childMo, resultMoList)

    def __doRespProcess(self, mo):
        mos = []
        if not self.__queryClassList or mo.isInstance(self.__queryClassList):
            if self.__propFilter is None or self.__propFilter.evaluate(mo):
                if not mo.status.deleted:
                    mos = self.__respProc.process(None, [mo])
        return mos


class ResponseQueryProc(QueryProc):
    def __init__(self, query):
        super(ResponseQueryProc, self).__init__(query)
        classes = query.subtreeClassFilter
        self.__queryClassList = classes.split(',') if classes is not None else []
        self.__propFilter = self._filterParser.from_string(query.subtreePropFilter) if query.subtreePropFilter is not None else None
        self.__procTable = {
            None: self.selfProc,
            'no': self.selfProc,
            'children': self.childrenProc,
            'full': self.subtreeProc
        }

    def process(self, mit, moList):
        proc = self.__procTable[self._query.subtree]
        return proc(moList)

    def selfProc(self, moList):
        mos = []
        for mo in moList:
            mos.append(mo.clone(parentMo=None, depth=0))
        return mos

    def childrenProc(self, moList):
        mos = []
        for mo in moList:
            # parent is selected by default apply filters to child and pick only children that match
            pMo = mo.clone(parentMo=None, depth=0)
            for childMo in mo.children:
                if self.__filterMo(childMo):
                    # Clone the children that match the criteria
                    pMo._attachChild(childMo.clone(parentMo=None, depth=0))
            mos.append(pMo)
        return mos

    def subtreeProc(self, moList):
        mos = []
        for mo in moList:
            # parent is selected, find all the descendants that match the filters and attach
            pMo = mo.clone(parentMo=None, depth=0)
            for childMo in mo.children:
                selectedChildMo = self.__subtreeProc(childMo)
                if selectedChildMo is not None:
                    pMo._attachChild(selectedChildMo)
            mos.append(pMo)
        return mos

    def __subtreeProc(self, mo):
        pMo = None
        if self.__filterMo(mo):
            pMo = mo.clone(parentMo=None)
        else:
            for childMo in mo.children:
                selectedChildMo = self.__subtreeProc(childMo)
                if selectedChildMo is not None:
                    if pMo is None:
                        pMo = mo.clone(parentMo=None, depth=0)
                    pMo._attachChild(selectedChildMo)
        return pMo

    def __filterMo(self, mo):
        if not self.__queryClassList or mo.isInstance(self.__queryClassList):
            if self.__propFilter is None or self.__propFilter.evaluate(mo):
                return not mo.status.deleted
        return False


class DnQueryProc(QueryProc):
    def __init__(self, dnQuery):
        super(DnQueryProc, self).__init__(dnQuery)

    def process(self, mit, moList):
        mos = mit.getMoByDn(self._query.dnStr)
        if mos:
            qProc = QueryTargetProc(self._query)
            return qProc.process(mit, mos)
        return mos


class ClassQueryProc(QueryProc):
    def __init__(self, classQuery):
        super(ClassQueryProc, self).__init__(classQuery)
        self._classNames = classQuery.className.split(',')

    def process(self, mit, moList):
        mos = mit.getMoByClass(self._classNames)
        if mos:
            qProc = QueryTargetProc(self._query)
            return qProc.process(mit, mos)
        return mos
