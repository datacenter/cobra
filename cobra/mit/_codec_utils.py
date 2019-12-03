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


class listWithTotalCount(list):
    def __init__(self, *args, **kwargs):
        super(listWithTotalCount, self).__init__(*args, **kwargs)
        self._totalCount = None

    @property
    def totalCount(self):
        if self._totalCount is not None:
            return self._totalCount
        else:
            return len(self)

    @totalCount.setter
    def totalCount(self, value):
        self._totalCount = value


def getParentDn(dnStr):
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
    """ Given a class name (aaaUserEp) returns tuple aaa,UserEp"""
    idx = -1
    upperFound = False

    for c in className:
        idx += 1
        if c.isupper():
            upperFound = True
            break

    if upperFound:
        pkg = className[:idx]
        klass = className[idx:]
    else:
        pkg = className
        klass = ""
    return pkg, klass
